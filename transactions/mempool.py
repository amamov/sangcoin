from typing import List, TYPE_CHECKING, Optional
from . import Tx, TxIn, TxOut, UTXO, create_tx
from .coinbase import make_coinbase_tx

if TYPE_CHECKING:
    from blockchain import Blockchain


class Mempool:
    """
    Mempool(메모리풀) : 아직 확정되지 않은 거래 내역들을 두는 곳(블럭에 포함되어 있지 않은 거래 내역)
    거래내역이 확정되려면 채굴자(블록을 생성한 사람)가 거래내역을 블록에 삽입해야 한다.
    채굴자는 컴퓨터 파워, 그래픽 카드 등으로 블록을 채굴하고 Mempool에 와서 거래내역을 블록에 추가한다.
    이 과정에서 채굴자는 수수료를 받는다.
    """

    def __init__(self, txs: List[Tx]):
        self.txs = txs
        self._blockchain: Optional[Blockchain] = None

    # TODO
    # @property
    # def blockchain(self) -> "Blockchain":
    #     if self._blockchain is None:
    #         raise RuntimeError("blockchain is not set")
    #     return self._blockchain

    # @blockchain.setter
    # def blockchain(self, value: "Blockchain"):
    #     self._blockchain = value

    def set_blockchain(self, blockchain):
        self._blockchain = blockchain

    def get_blockchain(self) -> "Blockchain":
        if self._blockchain is None:
            raise RuntimeError("blockchain is not set")
        return self._blockchain

    def _build_transfer_tx(self, sender: str, receiver: str, amount: int) -> Tx:
        """
        블록체인에서 특정 사용자가 다른 사용자에게 암호화폐를 전송하는 트랜잭션을 만드는 함수
        [[ UTXO (Unspent Transaction Output) 모델 기반의 구조 ]]
        sender: 자금을 보내는 주소
        receiver: 자금을 받는 주소
        amount: 보낼 금액

        [[트랜잭션 생성]]
        - 보내는 주소(sender)가 가진 UTXO를 모아 보내려는 금액 이상이 될때까지 inputs를 구성
        - 잔돈이 있으면 본인 주소로 반환하는 change output 구성
        - 수신자(receiver)에게 보낼 output 생성
        - 새 트랜잭션 ID는 전체 트랜잭션에 해시를 적용해서 생성
        """
        if self.get_blockchain().balance_by_address(sender) < amount:
            raise ValueError("not enough 돈")

        tx_inputs: List[TxIn] = []
        tx_outputs: List[TxOut] = []
        total = 0

        utxos = self.get_blockchain().get_utxos_by_address(sender)

        for utxo in utxos:
            if total >= amount:
                break
            tx_inputs.append(
                {"id": utxo["id"], "index": utxo["index"], "owner": sender}
            )
            total += utxo["amount"]

        change = total - amount
        if change != 0:
            tx_outputs.append({"owner": sender, "amount": change})

        tx_outputs.append({"owner": receiver, "amount": amount})

        return create_tx(tx_inputs, tx_outputs)

    def create_transfer(self, receiver: str, amount: int):
        """
        _build_transfer_tx로 만든 트랜잭션을 Mempool에 추가
        아직 블록에 포함되지 않았으므로 확정되지 않은 상태
        """
        tx = self._build_transfer_tx("sang_address", receiver, amount)
        self.txs.append(tx)

    def confirm_tx(self):
        coinbase = make_coinbase_tx("sang_address")
        txs = self.txs
        txs.append(coinbase)
        self.txs = []
        return txs

    def is_utxo_used(self, utxo: UTXO) -> bool:
        """
        해당 UTXO가 현재 mempool에서 사용 중인지 확인하는 함수
        double spending 방지에서 아주 핵심적인 역할
        """
        for tx in self.txs:
            for tx_in in tx["inputs"]:
                if (tx_in["id"], tx_in["index"]) == (utxo["id"], utxo["index"]):
                    return True
        return False


mempool = Mempool([])
