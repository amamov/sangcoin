import json
import hashlib


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
