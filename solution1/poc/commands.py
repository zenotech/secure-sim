import os
import click
import crypto
import ConfigParser
from binascii import hexlify


APP_NAME = 'hpc_security_demo'

@click.group()
@click.pass_context
def cli(ctx):
    """HPC Security Command Line Tools"""
    if ctx.invoked_subcommand not in ['configure', 'generate_key']:
        config = get_configuration()
        if config is None:
            raise click.UsageError("Configuration not found! Please run configure before first use")


@cli.command()
def generate_key():
    """Generate new keys"""
    key = crypto.generate_key()
    click.echo('Private Key (len {}):: \n{}'.format(len(hexlify(key.get_privkey())), hexlify(key.get_privkey())))
    click.echo('Public Key (len {})::\n{}'.format(len(hexlify(key.get_pubkey())), hexlify(key.get_pubkey())))


@cli.command()
@click.option('--keys', help='Print site public key', is_flag=True)
def list_sites(keys):
    """List sites with stored public keys"""
    config = get_configuration()
    for key in config:
        site = key.split('.')
        if site[0] != 'HOME':
            click.echo(site[0])
            if keys:
                click.echo(config[key])


@cli.command()
@click.argument('site_name')
@click.argument('public_key')
def add_site(site_name, public_key):
    """Add public key for new HPC site"""
    click.echo('Adding site key for site {}'.format(site_name))
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    config = ConfigParser.ConfigParser()
    config.add_section(site_name)
    config.set(site_name, 'public_key', public_key)
    with open(cfg, 'a') as configfile:
        config.write(configfile) 


@cli.command()
@click.argument('site')
def get_shared_key(site):
    """Generate a shared key for the site"""
    key = get_priv_key()
    site_public = get_site_public_key(site)
    shared = crypto.shared_key(key, site_public, format='hex')
    click.echo(hexlify(shared))


@cli.command()
@click.argument('in_file', "File to encrypt")
@click.argument('target_site', "Site to encrypt file for")
def encrypt(in_file, target_site):
    """Encrypt File"""
    click.echo("Encrypting file {} for site {}".format(in_file, target_site))
    public_key = get_site_public_key(target_site)
    private_key = get_priv_key()
    crypto.encrypt_file(private_key, public_key, in_file)


@cli.command()
@click.argument('in_file', "File to decrypt")
@click.option('--output', help='File name to output', default = None)
def decrypt(in_file, output):
    """decrypt File"""
    click.echo("Decrypting file {}".format(in_file))
    # public_key = get_site_public_key(target_site)
    private_key = get_priv_key()
    crypto.decrypt_file(private_key, in_file, out_filename = output)


@cli.command()
@click.option('--public_key', prompt='Public key',
              default=lambda: get_config_value("public_key") or "")
@click.option('--private_key', prompt='Private key',
              default=lambda: get_config_value("private_key") or "")
def configure(public_key, private_key):
    """Configure the client"""
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    print "Writing client configuration to %s" % cfg
    if not os.path.exists(os.path.dirname(cfg)):
        os.makedirs(os.path.dirname(cfg))
    parser = ConfigParser.SafeConfigParser()
    parser.add_section('HOME')
    parser.set('HOME', 'public_key', public_key)
    parser.set('HOME', 'private_key', private_key)
    with open(cfg, "w+") as config_file:
        parser.write(config_file)


def get_config_value(item):
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    parser = ConfigParser.RawConfigParser()
    parser.read([cfg])
    for section in parser.sections():
        for key, value in parser.items(section):
            if key == item:
                return value
    return None


def get_configuration():
    cfg = os.environ.get('POC_CONFIG', None)
    if not cfg:
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config')
    if not os.path.isfile(cfg):
        return None
    parser = ConfigParser.RawConfigParser()
    parser.read([cfg])
    rv = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            rv['%s.%s' % (section, key)] = value
    return rv


def get_priv_key():
    rv = get_configuration()
    public_key = rv['HOME.public_key'] if 'HOME.public_key' in rv else None
    private_key = rv['HOME.private_key'] if 'HOME.private_key' in rv else None
    if not private_key or not public_key:
        raise click.UsageError("Configuration Error! Please run configure before first use")
    return crypto.load_key(private_key, public_key)


def get_site_public_key(site):
    rv = get_configuration()
    public_key = rv['{}.public_key'.format(site)] if '{}.public_key'.format(site) in rv else None
    if not public_key:
        raise click.UsageError("Site public key not found, please run add_site first.")
    return public_key



if __name__ == '__main__':
    cli()