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
        """
        if self.get_blockchain().balance_by_address(sender) < amount:
            raise ValueError("not enough 돈")

        tx_inputs: List[TxIn] = []
        tx_outputs: List[TxOut] = []
        total = 0

        utxos = self.get_blockchain().get_utxos_by_address(sender)

        for utxo in utxos:
            if total > amount:
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
        tx = self._build_transfer_tx("sang_address", receiver, amount)
        self.txs.append(tx)

    def confirm_tx(self):
        coinbase = make_coinbase_tx("sang_address")
        txs = self.txs
        txs.append(coinbase)
        self.txs = []
        return txs

    def is_utxo_used(self, utxo: UTXO) -> bool:
        for tx in self.txs:
            for tx_in in tx["inputs"]:
                if tx_in["id"] == utxo["id"] and tx_in["index"] == utxo["index"]:
                    return True
        return False


mempool = Mempool([])


"""
_build_transfer_tx 내부 동작 시뮬레이션

[
    {"owner": sender, "amount": 20},
    {"owner": sender, "amount": 15},
    {"owner": sender, "amount": 10},
    {"owner": sender, "amount": 30},
    {"owner": sender, "amount": 50},
]

amount = 67 (송금금액)

==>

inputs = [
    {"owner": sender, "amount": 20},
    {"owner": sender, "amount": 15},
    {"owner": sender, "amount": 10},
    {"owner": sender, "amount": 30},
]  # 총합 = 75

outputs = [
    {"owner": sender, "amount": 8},      # 잔돈
    {"owner": receiver, "amount": 67},   # 수신자에게 보낼 금액
]

"""
