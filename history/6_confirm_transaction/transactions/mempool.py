from typing import List, TYPE_CHECKING, Optional
from . import Tx, TxIO, create_tx
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

    def _build_transfer_tx(self, sender: str, receiver: str, amount: int):
        """
        블록체인에서 특정 사용자가 다른 사용자에게 암호화폐를 전송하는 트랜잭션을 만드는 함수
        [[ UTXO (Unspent Transaction Output) 모델 기반의 구조 ]]
        sender: 자금을 보내는 주소
        receiver: 자금을 받는 주소
        amount: 보낼 금액
        """
        if self._blockchain is None:
            raise RuntimeError("blockchain is not set")

        # 송금자가 충분한 자금을 가지고 있는지 확인
        if self._blockchain.balance_by_address(sender) < amount:
            raise ValueError("Not enough money")

        # 거래 입력 목록, 이 트랜젝션이 어떤 UTXO들을 소비할 것인지 명시
        inputs: List[TxIO] = []

        # 거래 출력 목록, 이 트랜잭션이 누구에게 얼마를 보낼 것인지 정의, 이 트랜젝션을 통해 새롭게 생성될 UTXO
        outputs: List[TxIO] = []

        collected_amount = 0

        # 보유 UTXO 목록, 블록체인 상에서 sender 주소가 아직 사용하지 않은 출력들(UTXO) 리스트 이 중 일부를 골라서 inputs로 소비하게 됨
        sender_utxos = self._blockchain.get_utxos(sender)

        # UTXO 수집 및 입력 구성, 송금 금액을 충당할 때까지 UTXO들을 하나씩 선택해서 inputs에 추가
        for output in sender_utxos:
            if collected_amount > amount:
                break
            inputs.append({"owner": output["owner"], "amount": output["amount"]})
            collected_amount += output["amount"]

        # 잔돈 처리
        change = collected_amount - amount
        if change != 0:
            outputs.append({"owner": sender, "amount": change})

        # 최종 수신자에게 송금 출력 추가
        outputs.append({"owner": receiver, "amount": amount})

        return create_tx(inputs, outputs)

    def create_transfer(self, receiver: str, amount: int):
        tx = self._build_transfer_tx("sang_address", receiver, amount)
        self.txs.append(tx)

    def confirm_tx(self):
        coinbase = make_coinbase_tx("sang_address")
        txs = self.txs
        txs.append(coinbase)
        self.txs = []
        return txs


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
