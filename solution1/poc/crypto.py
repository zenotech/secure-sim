import time
import pyelliptic
import os
import struct
import Crypto.Hash.SHA384 as SHA384
from hashlib import sha512
from binascii import unhexlify

# CURVE = 'secp256k1'
# CURVE = 'secp521r1'
CURVE = 'sect283r1'


def generate_key():
    return pyelliptic.ECC(curve=CURVE)


def load_key(priv_key, pub_key):
    """
    Return ECC key
    priv_key and pub_key assumed to be hex.
    """
    pubkey_x, pubkey_y  = pyelliptic.ECC._decode_pubkey(pub_key, format='hex')
    return pyelliptic.ECC(curve=CURVE, raw_privkey = unhexlify(priv_key), pubkey_x = pubkey_x, pubkey_y = pubkey_y)


def shared_key(priv_key, pub_key, format = 'binary'):
    """Generate a new shared encryption key from a keypair."""
    shared_key = priv_key.get_ecdh_key(pub_key, format)
    shared_key = shared_key[:32] + SHA384.new(shared_key[32:]).digest()
    return shared_key


def encrypt_file(key, public_key, in_filename, out_filename=None, ciphername='aes-256-cbc'):
    """ 
    """
    start = time.clock()
    if not out_filename:
        out_filename = in_filename + '.enc'

    curve = pyelliptic.OpenSSL.get_curve_by_id(key.curve)

    ephem = pyelliptic.ECC(curve=curve)

    pubkey_x, pubkey_y = pyelliptic.ECC._decode_pubkey(public_key, format='hex')

    key = sha512(ephem.raw_get_ecdh_key(pubkey_x, pubkey_y)).digest()

    key_e, key_m = key[:32], key[32:]
    
    pubkey = ephem.get_pubkey()
    
    iv = pyelliptic.Cipher.gen_IV(ciphername)
    blocksize = pyelliptic.Cipher.get_blocksize(ciphername)

    ctx = pyelliptic.Cipher(key_e, iv, 1, ciphername)

    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            outfile.write(pubkey)

            while True:
                chunk = infile.read(blocksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(ctx.update((chunk)))
            outfile.write(ctx.final())
    end = time.clock()
    return ((end - start, filesize, out_filename))

def decrypt_file(key, in_filename, out_filename=None, ciphername='aes-256-cbc'):
    """ 
    """
    if not out_filename:
        if in_filename.endswith('.enc'):
            out_filename = in_filename[:-4]

    blocksize = pyelliptic.OpenSSL.get_cipher(ciphername).get_blocksize()

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(blocksize)
            coord_len = len(key.pubkey_x) * 2 + 1
            pkey = infile.read(coord_len)
            pubkey_x, pubkey_y = pyelliptic.ECC._decode_pubkey(pkey)
            key = sha512(key.raw_get_ecdh_key(pubkey_x, pubkey_y)).digest()
            key_e, key_m = key[:32], key[32:]
            ctx = pyelliptic.Cipher(key_e, iv, 0, ciphername)
            while True:
                chunk = infile.read(blocksize)
                if len(chunk) == 0:
                    break
                outfile.write(ctx.update(chunk))
            # outfile.write(ctx.final())
            outfile.truncate(origsize)
