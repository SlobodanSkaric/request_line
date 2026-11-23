from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)


def verify_password(palin:str, hashed_password:str) -> bool:
    return password_hasher.verify(palin, hashed_password)