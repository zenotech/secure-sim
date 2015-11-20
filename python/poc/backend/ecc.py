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
CIPHER = 'aes-256-cbc'


class Key(object):

    def __init__(self, priv_key = None, pub_key = None):
        if priv_key or pub_key:
            if pub_key and pub_key:
                pubkey_x, pubkey_y  = pyelliptic.ECC._decode_pubkey(pub_key, format='hex')
                self.key = pyelliptic.ECC(curve=CURVE, raw_privkey = unhexlify(priv_key), pubkey_x = pubkey_x, pubkey_y = pubkey_y)
            else:
                raise ValueError("Private AND Public key both need to be specified")
        else:
            self.key = self.generate_key()
    
    @staticmethod
    def generate_key():
        return pyelliptic.ECC(curve=CURVE)

    def get_private_key(self):
        return self.key.get_privkey()

    def get_public_key(self):
        return self.key.get_pubkey()

    def shared_key(self, pub_key, format = 'binary'):
        """Generate a new shared encryption key for given public key"""
        shared_key = self.key.get_ecdh_key(pub_key, format)
        shared_key = shared_key[:32] + SHA384.new(shared_key[32:]).digest()
        return shared_key

    def encrypt_file(self, public_key, in_filename, out_filename=None):
        """ 
        """
        start = time.clock()
        if not out_filename:
            out_filename = in_filename + '.enc'

        curve = pyelliptic.OpenSSL.get_curve_by_id(self.key.curve)

        ephem = pyelliptic.ECC(curve=curve)

        pubkey_x, pubkey_y = pyelliptic.ECC._decode_pubkey(public_key, format='hex')

        key = sha512(ephem.raw_get_ecdh_key(pubkey_x, pubkey_y)).digest()

        key_e, key_m = key[:32], key[32:]
        
        pubkey = ephem.get_pubkey()
        
        iv = pyelliptic.Cipher.gen_IV(CIPHER)
        blocksize = pyelliptic.Cipher.get_blocksize(CIPHER)

        ctx = pyelliptic.Cipher(key_e, iv, 1, CIPHER)

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

    def decrypt_file(self, in_filename, out_filename=None):
        """ 
        """
        start = time.clock()
        if not out_filename:
            if in_filename.endswith('.enc'):
                out_filename = in_filename[:-4]

        blocksize = pyelliptic.OpenSSL.get_cipher(CIPHER).get_blocksize()

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
                iv = infile.read(blocksize)
                coord_len = len(self.key.pubkey_x) * 2 + 1
                pkey = infile.read(coord_len)
                pubkey_x, pubkey_y = pyelliptic.ECC._decode_pubkey(pkey)
                key = sha512(self.key.raw_get_ecdh_key(pubkey_x, pubkey_y)).digest()
                key_e, key_m = key[:32], key[32:]
                ctx = pyelliptic.Cipher(key_e, iv, 0, CIPHER)
                while True:
                    chunk = infile.read(blocksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(ctx.update(chunk))
                # outfile.write(ctx.final())
                outfile.truncate(origsize)
        end = time.clock()
        return ((end - start, origsize, out_filename))


