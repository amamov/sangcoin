import time
from typing import TypedDict, List
from utils import hash_data


"""
블록체인 UTXO 기반 트랜잭션 흐름
UTXO 모델은 비트코인과 유사한 구조로 모든 트랜잭션은
기존의 사용되지 않은 출력(UTXO)를 사용해 새로운 출력을 만드는 방식으로 처리됨

1. 사용자의 잔액 조회 (blockchain.Blockchain.get_utxos_by_address)
2. 트랜잭션 생성 (transactions.mempool.Mempool._build_transfer_tx)
3. Mempool에 추가 (transactions.mempool.Mempool.create_transfer)
4. 블록 채굴 (blockchainBlockchain.add_block)
5. 블록 저장 및 확정 (transactions.coinbase.make_coinbase_tx)

- 불변성 보장: 트랜잭션은 한 번 블록에 포함되면 영구 보관
- 분산성 유리: 상태 대신 트랜잭션을 기반으로 잔액 계산 가능
- 검증 효율적: 단순한 UTXO 사용 여부만 체크하면 됨


트랜잭션이란? 기존의 코인을 input으로 "소비"하고, 새로운 output으로 "재발행"하는 것.
잔액이란? 내가 소유한 output들(= 아직 소비되지 않은 것들, 즉 UTXO)의 합계.
보안이란? 내가 소유하지 않은 output은 input으로 사용할 수 없음 (디지털 서명 필요).

| 항목        | Mempool 트랜잭션     | Coinbase 트랜잭션        |
|------------|-------------------  |--------------------     |
| 포함 위치    | 아직 블록에 없음      | 항상 블록 안에 있음       |
| 용도        | 사용자 간 전송        | 채굴자에게 보상 지급       |
| 생성 주체    | 사용자               | 시스템 / 채굴자           |
| input 존재  | 있음 (기존 UTXO 소비) | 없음 (id="", index=-1)   |
| output 의미 | 새로운 UTXO 전송      | 새 코인 발행 (보상)       |

"""


class TxIn(TypedDict):
    """
    이전 트랜잭션에서 받은 코인을 소비함
    이 트랜잭션이 쓸 수 있는 돈의 출처를 증명함
    """

    id: str  # 이전 트랜잭션의 ID
    index: int  # 해당 트랜잭션의 outputs 증 몇 번째를 쓰는지
    owner: str  # 이 input을 사용할 수 있는 사람(서명 주체)


class TxOut(TypedDict):
    """
    이번 트랜잭션을 통해 새로 생성된 코인
    이 트랜잭션으로 누구에게 얼마를 줄지를 정의함
    """

    owner: str  # 수신자 주소
    amount: int  # 보낼 금액


class UTXO(TypedDict):
    id: str
    index: int
    amount: int


class Tx(TypedDict):
    id: str
    timestamp: int
    inputs: List[TxIn]
    outputs: List[TxOut]


def create_tx(inputs: List[TxIn], outputs: List[TxOut]) -> Tx:
    tx: Tx = {
        "id": "",
        "timestamp": int(time.time()),
        "inputs": inputs,
        "outputs": outputs,
    }
    tx["id"] = hash_data(tx)
    return tx


"""
상황: Alice가 Bob에게 30을 보내려 한다. Alice는 두 개의 UTXO를 갖고 있음:
tx1의 output 0번 (amount: 20)
tx2의 output 1번 (amount: 15)

{
  "inputs": [
    { "id": "tx1", "index": 0, "owner": "alice" },
    { "id": "tx2", "index": 1, "owner": "alice" }
  ],
  "outputs": [
    { "owner": "bob", "amount": 30 },
    { "owner": "alice", "amount": 5 }  // Change
  ]
}

inputs: 이전에 받은 코인을 가져다가 쓰는 것

outputs: 이 트랜잭션을 통해 새롭게 발행되는 코인들

"""
