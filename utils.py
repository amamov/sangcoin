import json
import hashlib
from dataclasses import is_dataclass, fields


# 바이트로 변환
def bytes_from(obj) -> bytes:
    if hasattr(obj, "to_dict"):
        return json.dumps(obj.to_dict(), sort_keys=True).encode("utf-8")
    return json.dumps(dict_from(obj), sort_keys=True).encode("utf-8")


def restore_buffer(buffer: bytes):
    return json.loads(buffer.decode("utf-8"))


# 직렬화(dict로 변환)
def dict_from(obj) -> dict | None | list:
    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            if callable(value):
                continue
            result[f.name] = dict_from(value)
        return result

    elif isinstance(obj, dict):
        return {dict_from(k): dict_from(v) for k, v in obj.items()}

    elif isinstance(obj, (list, tuple, set)):
        return [dict_from(item) for item in obj]

    elif callable(obj):
        return None  # or raise or skip depending on policy

    else:
        return obj


def hash_dataclass(obj) -> str:
    data = json.dumps(dict_from(obj), sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
