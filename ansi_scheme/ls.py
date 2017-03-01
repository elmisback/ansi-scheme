import os
import pkg_resources

import click

from .constants import *

@click.command()
@click.option('-q', help="machine-readable output")
@click.option('--all', 'scheme_set', flag_value='all', help="show all schemes", default=True)
@click.option('--user', 'scheme_set', flag_value='user', help="show user schemes only")
@click.option('--package', 'scheme_set', flag_value='package', help="show package schemes only")
@click.pass_obj
def ls(user, q, scheme_set):
    """List schemes."""
    user_schemes = [os.path.splitext(s)[0]
            for s in os.listdir(user.data_dir) if s.endswith(EXT)]
    package_schemes = [os.path.splitext(s)[0]
            for s in pkg_resources.resource_listdir(__name__, PKG_SCHEMES)]
    sections = []
    if (scheme_set == 'user' or scheme_set == 'all') and user_schemes:
        sections.append('User schemes:\n' + '\n'.join(user_schemes))
    if scheme_set == 'package' or scheme_set == 'all':
        sections.append('Package schemes:\n' + '\n'.join(package_schemes))
    print('\n\n'.join(sections))
