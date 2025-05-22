from db import db


def print_all_keys():
    with db.store.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            print(f"{key!r} => {value!r}")


print_all_keys()
