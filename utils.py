import json
import hashlib


def bytes_from(obj) -> bytes:
    return json.dumps(obj.__dict__).encode("utf-8")


def restore_buffer(buffer: bytes):
    data = json.loads(buffer.decode("utf-8"))
    block = type("Block", (), {})()  # empty object
    block.__dict__.update(data)
    return block


def hash_data(obj) -> str:
    data = json.dumps(
        {
            "data": obj.data,
            "prev_hash": obj.prev_hash,
            "height": obj.height,
            "nonce": obj.nonce,
            "timestamp": obj.timestamp,
            "difficulty": obj.difficulty,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
