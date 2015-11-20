import os
import crypto
import ConfigParser


class SecureSim(object):

    def __init__(self, config_file):
        self.sites = {}
        if not os.path.isfile(config_file):
            raise ValueError("Config file {} not found".format(config_file))
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
        self.ecc_key = crypto.load_key(self.private_key, self.public_key)
        print self.__dict__

    def does_site_exist(self, site):
        return site in self.sites

    def encrpyt_file(self, in_file, out_file, site):
        site_key = self.sites[site]
        time, size, out_file = crypto.encrypt_file(self.ecc_key, site_key, in_file, out_filename=out_file, ciphername='aes-256-cbc')

    def decrpyt_file(self, in_file, out_file):
        crypto.decrypt_file(self.ecc_key, in_file, out_filename=out_file, ciphername='aes-256-cbc')

if __name__ == '__main__':
    SecureSim('./internal.site')
