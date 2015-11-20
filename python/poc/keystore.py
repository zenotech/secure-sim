import os
import ConfigParser

from binascii import hexlify

import backend.ecc as crypto


class KeyStore(object):

    def __init__(self, config_file, new = False):
        self.sites = {}
        if new:
            self._write_new_config(config_file)
        else:
            if not os.path.isfile(config_file):
                raise ValueError("Config file {} not found".format(config_file))
            self.config_file = config_file
            parser = ConfigParser.RawConfigParser()
            parser.read([config_file])
            if parser.has_option('HOME', 'public_key'):
                self.public_key = parser.get('HOME', 'public_key')
            else:
                raise ValueError("Public key not found in config {}".format(config_file))
            if parser.has_option('HOME', 'private_key'):
                self.private_key = parser.get('HOME', 'private_key')
            else:
                raise ValueError("Public key not found in config {}".format(config_file))
            for section in parser.sections():
                if section != "HOME":
                    self.sites[section] = parser.get(section, 'public_key')
            self.key = crypto.Key(self.private_key, self.public_key)

    def _write_new_config(self, config_file):
        self.key = crypto.Key.generate_key()
        self.public_key = hexlify(self.key.get_pubkey())
        self.private_key = hexlify(self.key.get_privkey())
        parser = ConfigParser.SafeConfigParser()
        parser.add_section('HOME')
        parser.set('HOME', 'public_key', self.public_key)
        parser.set('HOME', 'private_key',  self.private_key)
        with open(config_file, "w+") as f:
            parser.write(f)
        self.config_file = config_file

    def update_key(self, private_key, public_key):
        self.key = crypto.Key(private_key, public_key)
        self.public_key = public_key
        self.private_key = private_key
        parser = ConfigParser.RawConfigParser()
        parser.read([self.config_file])
        if not parser.has_section('HOME'):
            parser.add_section('HOME')
        parser.set('HOME', 'public_key', self.public_key)
        parser.set('HOME', 'private_key',  self.private_key)
        with open(self.config_file, "w+") as f:
            parser.write(f)

    def does_site_exist(self, site):
        return site in self.sites

    def list_sites(self):
        return self.sites

    def add_site(self, site_name, public_key, write = True):
        self.sites[site_name] = public_key
        if write: 
            config = ConfigParser.ConfigParser()
            config.add_section(site_name)
            config.set(site_name, 'public_key', public_key)
            with open(self.config_file, 'a') as configfile:
                config.write(configfile) 

    def get_shared_secret(self, site):
        return self.key.shared_key(self.sites[site], format = 'hex')

    def encrypt_file(self, site, in_file, out_file):
        site_key = self.sites[site]
        return self.key.encrypt_file(site_key, in_file, out_filename=out_file)

    def decrypt_file(self, in_file, out_file):
        return self.key.decrypt_file(in_file, out_filename=out_file)

if __name__ == '__main__':
    SecureSim('./internal.site')
