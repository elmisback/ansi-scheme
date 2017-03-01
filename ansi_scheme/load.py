import os
import re
from io import open
import pkg_resources
import json

import click

from .constants import *

def _add_from_github(scheme_name):
    raise NotImplementedError()

def _parse_rgb_hex(string):
    """Resolves an ANSI hex value from the string."""
    matches = re.findall('[0-9a-fA-F]', string)
    if len(matches) < 6:
        raise ValueError('Not enough hex values in "{}".'
                .format(string))
    r = ''.join(matches[:2])
    g = ''.join(matches[2:4])
    b = ''.join(matches[4:6])
    return '/'.join([r, g, b])

def _resolve_colorscheme(data_dir, scheme_name, style_name):
    """Raises ValueError if the scheme is unavailable."""
    if scheme_name == 'default':
        return DEFAULT_SCHEME
    user_scheme_path = os.path.join(data_dir, scheme_name + EXT)
    pkg_scheme_path = os.path.join(PKG_SCHEMES, scheme_name + EXT)
    if os.path.exists(user_scheme_path):
        with open(user_scheme_path, 'rt') as f:
            scheme = json.loads(f.read())
    elif pkg_resources.resource_exists(__name__, pkg_scheme_path):
        s = pkg_resources.resource_string(__name__,
                            pkg_scheme_path).decode('utf-8')
        scheme = json.loads(s)
    else:
        raise ValueError(
                '{} is neither a user scheme nor a package scheme.'
                .format(scheme_name))
    return scheme

def _resolve_colors(scheme):
    """Returns a dict of color index i -> ab/cd/ef hex value.

    Raises ValueError if the scheme is unavailable."""
    colors = scheme['colors']
    lowercase_colors = list(map(str.lower, COLORS))
    return dict((str(lowercase_colors.index(k.lower()))
                 if k.lower() in lowercase_colors else k,
             _parse_rgb_hex(v))
              for k, v in colors.items())

def _resolve_style_value(colors, v):
    """"Raises IndexError"""
    try:
        return _parse_rgb_hex(v)
    except ValueError:  # Not a hex value.
        pass
    if v.isdigit():  # it's a color index
        try:
            v = COLORS[int(v)] if int(v) <= len(COLORS) else v
            return colors[v]
        except KeyError:
            raise ValueError('{} is not a defined color.'.format(v))
    else:  # it's a color name
        try:
            index = [c.lower() for c in COLORS].index(v.lower())
        except IndexError:
            raise ValueError('{} is not a recognized color.'.format(v))
        try:
            return colors[str(index)]
        except KeyError:
            raise ValueError('{} is not a defined color.'.format(v))

def _resolve_style(scheme, colors, style_name):
    """Raises ValueError if the style is unavailable."""
    try:
        # Allow default overrides.
        available_styles = DEFAULT_STYLES.copy()
        available_styles.update(scheme.get('styles', {}))
        style = available_styles[style_name]
    except KeyError:
        raise ValueError("Style '{}' is not defined for scheme '{}'"
                .format(style_name, scheme_name))
    return dict((k, _resolve_style_value(colors, v))
                for k, v in style.items())

def _palette_template():
    """Returns a template for the terminal-color-setting-escape codes."""
    tmux = os.getenv('TMUX')
    term = (os.getenv('TERM') or os.getenv('TERMINAL'))
    if tmux and len(tmux) > 0:
        return '\033Ptmux;\033\033]4;{};rgb:{}\033\033\\\033\\'
    elif term and term.startswith('screen'):
        return '\033P\033]4;{};rgb:{}\033\\'
    else:
        return '\033]4;{};rgb:{}\033\\'

def set_colors(colors):
    """Sets the terminal's color palette."""
    tmp = _palette_template()
    output = ''.join([tmp.format(i, c) for i, c in colors.items()])
    print(output)
    print(output, end='')

def _style_template():
    """Returns a template for setting targets like fg/bg/cs."""
    tmux = os.getenv('TMUX')
    term = (os.getenv('TERM') or os.getenv('TERMINAL'))
    if tmux and len(tmux) > 0:
        return '\033Ptmux;\033\033]{};rgb:{}\033\033\\\033\\'
    elif term and term.startswith('screen'):
        return '\033P\033]{};rgb:{}\033\\'
    else:
        return '\033]{};rgb:{}\033\\'

def set_style(colors, style):
    """Sets fg/bg/cs for the terminal."""
    style_n = {
        'foreground': 10,
        'background': 11,
        'cursor': 12
    }

    tmp = _style_template()
    output = ''.join([tmp.format(style_n[k], v) for k, v in style.items()])
    print(output, end='')

@click.command()
@click.option('--from-github', is_flag=True)
@click.argument('scheme', required=False)
@click.argument('style', required=False)
@click.pass_obj
def load(user, from_github, scheme, style):
    """Load schemes and styles."""
    scheme_name = scheme or user.settings['scheme_name']
    style_name = style or user.settings['style_name']
    style_name = style_name or DEFAULT_STYLE

    if from_github:
        _add_from_github(scheme_name)

    try:
        scheme = _resolve_colorscheme(user.data_dir, scheme_name, style_name)
        colors = _resolve_colors(scheme)
        style = _resolve_style(scheme, colors, style_name)
    except ValueError:  # fail to resolve
        raise

    set_colors(colors)
    set_style(colors, style)

    user.settings['scheme_name'] = scheme_name
    user.settings['style_name'] = style_name

    user.save_settings()
