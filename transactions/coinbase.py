from . import Tx, TxIO, create_tx

MINER_REWARD = 50


def make_coinbase_tx(address: str) -> Tx:
    """
    Conbase Transaction : 새 블록 안에서 가장 첫 번째 트랜젝션으로,
    채굴자에게 블록보상(새로운 코인 + 수수료)을 지급하기 위해 만들어진 트랜젝션
    -> 블록체인 네트워크에서 새로운 코인을 발행하려면 누군가에게 줘야 하는데,
    이 역할을 채굴자가 수행하고, 그 보상을 코인베이스 트랜젝션을 통해 지급 받는다.
    -> 신규 발행(Inflation) 기능 담당
    """
    coinbase_tx_in: TxIO = {"amount": MINER_REWARD, "owner": "COINBASE"}
    coinbase_tx_out: TxIO = {"amount": MINER_REWARD, "owner": address}
    return create_tx([coinbase_tx_in], [coinbase_tx_out])
