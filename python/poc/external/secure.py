import libdecode
import key


def get_private_key():
    obs_key = key.key
    secret_key = libdecode.decode(obs_key)
    return secret_key
