import os
import click
from binascii import hexlify
from importlib import import_module

from keystore import KeyStore
from backend import ecc as crypto
import workflow as flow
import agent

APP_NAME = 'hpc_security_demo'


@click.group()
@click.pass_context
def cli(ctx):
    """HPC Security Command Line Tools"""
    if ctx.invoked_subcommand not in ['configure', 'generate_key', 'start_agent']:
        config = get_config_file()
        if config is None:
            raise click.UsageError("Configuration not found!"
                                   "Please run configure before first use")


@cli.command()
def generate_key():
    """Generate new key pair"""
    key = crypto.Key.generate_key()
    click.echo('Private Key (len {}):: \n{}'.format(
        len(key.get_privkey()),
        hexlify(key.get_privkey())))
    click.echo('Public Key (len {})::\n{}'.format(
        len(key.get_pubkey()),
        hexlify(key.get_pubkey())))


@cli.command()
@click.option('--keys', help='Print site public key', is_flag=True)
def list_sites(keys):
    """List sites with stored public keys"""
    key_store = KeyStore(get_config_file())
    for site, key in key_store.list_sites().iteritems():
        if keys:
            click.echo("{} = {}".format(site, key))
        else:
            click.echo(site)


@cli.command()
@click.argument('site_name')
@click.argument('public_key')
def add_site(site_name, public_key):
    """Add public key for new HPC site"""
    click.echo('Adding site key for site {}'.format(site_name))
    key_store = KeyStore(get_config_file())
    key_store.add_site(site_name, public_key)


@cli.command()
@click.argument('site')
def get_shared_key(site):
    """Generate a shared key for the site"""
    key_store = KeyStore(get_config_file())
    pub_key, secret = key_store.get_shared_secret(site)
    click.echo("Public Key: \n{}".format(hexlify(pub_key)))
    click.echo("Secret: \n{}".format(hexlify(secret)))
    # click.echo(hexlify(key_store.get_shared_secret(site)))


@cli.command()
@click.argument('target_site', "Site to encrypt file for")
@click.argument('input', "File to encrypt")
@click.option('--output', '-o', help='File name to output', default=None)
def encrypt(target_site, input, output):
    """Encrypt File"""
    click.echo("Encrypting file {} for site {}".format(input, target_site))
    key_store = KeyStore(get_config_file())
    time, size, out_file = key_store.encrypt_file(target_site, input, output)
    click.echo("{} bytes encrypted in {} seconds, output to {}".format(
        size, time, out_file))


@cli.command()
@click.argument('input', "File to decrypt")
@click.option('--key', default=None)
@click.option('--agent_url', default=None)
@click.option('--key_module', default=None)
@click.option('--output', help='File name to output', default=None)
def decrypt(input, key, agent_url, key_module, output):
    """Decrypt File"""
    click.echo("Decrypting file {}".format(input))
    if key:
        time, size, out_file =  crypto.decrypt_file_with_symkey(input, key, output)
        click.echo("{} bytes decrypted in {} seconds,output to {}".format(size,
                                                                          time,
                                                                          out_file))
    elif agent_url:
        sym_key = agent.get_sym_key(agent_url)
        time, size, out_file =  crypto.decrypt_file_with_symkey(input, sym_key, output)
        click.echo("{} bytes decrypted in {} seconds,output to {}".format(size,
                                                                          time,
                                                                          out_file))
    elif key_module:
        m = import_module(key_module)
        key_func = getattr(m,'get_private_key')
        priv_key = key_func()
        if priv_key is not None:
            key_store = KeyStore(get_config_file(), private_key = priv_key)
            time, size, out_file = key_store.decrypt_file(input, output)
            click.echo("{} bytes decrypted in {} seconds,output to {}".format(size,
                                                                          time,
                                                                          out_file))
        else:
            click.echo("Private Key not returned by key module")
    else:
        key_store = KeyStore(get_config_file())
        time, size, out_file = key_store.decrypt_file(input, output)
        click.echo("{} bytes decrypted in {} seconds,output to {}".format(size,
                                                                          time,
                                                                          out_file))

@cli.command()
@click.argument('site')
def workflow(site):
    """Run the simulated workflow"""
    click.echo("Preparing input for site {}".format(site))
    key_store = KeyStore(get_config_file())
    if key_store.does_site_exist(site):
        flow.generate_mesh()
        flow.generate_control_files()
        flow.compress_input()
        flow.encrpyt_input()
        flow.transfer_files()
    else:
        click.echo("Site {} does not exist in keystore, please add_site".format(site))


@cli.command()
@click.argument('public_key')
@click.argument('private_key')
@click.argument('encrypted_file')
@click.option('--count', '-c', default=None, type=int)
@click.argument('client_ip', nargs=-1)
def start_agent(public_key, private_key, encrypted_file, count, client_ip):
    """Start the agent process"""
    key = crypto.Key(priv_key = private_key, pub_key = public_key)
    cipher = key.read_cipher(encrypted_file)
    agent.start_server(cipher, valid_ips = client_ip, max_requests = count)

@cli.command()
def configure():
    """Configure the client"""
    if not get_config_file():
        if click.confirm('Config file does not exist,'
                         ' generate new keys and write file?'):
            key_store = KeyStore(get_config_file_name(), new=True)
            click.echo("Keystore written to {} \n Private Key: \
                \n {} \n Public Key: \n {}".format(
                get_config_file_name(),
                key_store.private_key,
                key_store.public_key))
    else:
        key_store = KeyStore(get_config_file())
        private = click.prompt('Private Key', default=key_store.private_key)
        public = click.prompt('Public Key', default=key_store.public_key)
        key_store.update_key(private, public)
        click.echo("Keystore written to {}".format(get_config_file()))


def get_config_file_name():
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    return cfg


def get_config_file():
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    if os.path.isfile(cfg):
        return cfg
    return None

if __name__ == '__main__':
    cli()
