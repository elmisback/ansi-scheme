#!/usr/bin/env python
"""ansi-theme: terminal themes via ANSI escape codes

# Usage

    # Set the terminal's color palette.
    ansi-theme set base16-atelier-heath

    # List available themes.
    # Themes from the base16 project are preinstalled.
    ansi-theme ls

    # Use a light background
    ansi-theme set --brightness 1

    # Add a new theme
    ansi-theme add path/to/theme.ansitheme

    # Write a vim colorscheme file that works with all themes
    ansi-theme vimfile > ansi-theme.vim
"""
from __future__ import print_function
import os
import argparse
import os
import pickle
import sys
import pkg_resources
import re

# TODO Save user's bg/fg/cs preferences.
# TODO Support iTerm2.

_XDG = os.environ['XDG_DATA_HOME']
_FALLBACK = os.path.abspath('~/.{}'.format(__name__))
DATA_DIR = os.path.join(_XDG, 'ansi-theme') if _XDG else _FALLBACK
USER_FILE = os.path.join(DATA_DIR, 'user.dat')
PKG_THEMES = 'default-themes'
EXT = '.ansitheme'
_CLI = False

def _mkdir_p(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def _cleanup(line):
    """Puts a hex value in 12/34/56 format, strips anything after that."""
    line = line.strip()[:8].split()[0]
    if len(line) == 6:
        line = "{}/{}/{}".format(line[:2], line[2:4], line[4:])
    return line

def _read_string_as_colors(s):
    return [_cleanup(l) for l in s.split()]

def _read_colors(colorfile):
    with open(colorfile, 'r') as f:
        colors = _read_string_as_colors(s)
    return colors

def _write_colors(colors, outfile=None):
    if not outfile:
        for c in colors:
            print(c)
        return
    with open(outfile, 'w') as f:
        f.writelines([c + '\n' for c in colors])

def _name_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]

def _name_to_user_path(name):
    themefile = name + EXT
    return os.path.join(DATA_DIR, themefile)

def _name_to_pkg_path(name):
    themefile = name + EXT
    return os.path.join(PKG_THEMES, themefile)

def _is_user_theme(theme):
    return os.path.exists(_name_to_user_path(theme))

def _is_pkg_theme(theme):
    themefile = theme + EXT
    path = os.path.join(PKG_THEMES, themefile)
    return pkg_resources.resource_exists(__name__, path)

def _name_to_colors(name):
    if _is_user_theme(name):
        return _read_colors(_name_to_user_path(name))
    if _is_pkg_theme(name):
        return _read_string_as_colors(pkg_resources.resource_string(__name__, _name_to_pkg_path(name)))

    raise ValueError('Invalid name.')

def add_theme(theme_path):
    colors = _read_colors(theme_path)
    name = _name_from_path(theme_path)
    out = _name_to_user_path(name)
    _write_colors(colors, out)

def rm_theme(theme_name):
    """Remove the user theme theme_name if it exists."""
    path = _name_to_user_path(theme_name)
    if os.path.exists(path):
        os.remove(path)
    else:
        message = ("Couldn't find the theme {} at path {}. Note only"
                   "user-installed themes can be deleted."
                  ).format(theme_name, path)
        if _CLI:
            print(message)
            sys.exit(1)

def mv_theme(src, target):
    colors = _name_to_colors(src)
    _write_colors(colors, _name_to_user_path(target))
    rm_theme(src, pkg_path_is_error=False)

def ls_themes():
    # User themes
    themes = sorted([_name_from_path(p)
                    for p in os.listdir(DATA_DIR) if p.endswith(EXT)])
    if themes:
        print('User themes:')
        for theme in themes:
            print(theme)

    # Package themes
    themes = sorted([
        _name_from_path(p)
        for p in pkg_resources.resource_listdir(__name__, PKG_THEMES)])
    print('Package themes:')
    for theme in themes:
        print(theme)

def _get_user_data():
    if not os.path.exists(USER_FILE):
        return None
    else:
        with open(USER_FILE, 'r') as f:
            return pickle.load(f)

def _save_user_pref(name, value):
    user = _get_user_data()
    if not user:
        user = {}
    user[name] = value
    with open(USER_FILE, 'w') as f:
        pickle.dump(user, f)

def _get_user_pref(name):
    user = _get_user_data()
    if not user:
        return None
    else:
        return user.get(name)

def export_theme(name):
    if not name:
        name = _get_user_pref('theme')
        if not name:
            raise ValueError('Specify a theme to export.')
    _write_colors(_name_to_colors(name))

def _target_template():
    """Returns a template for setting targets like fg/bg/cs."""
    tmux = os.getenv('TMUX')
    term = (os.getenv('TERM') or os.getenv('TERMINAL'))
    if tmux and len(tmux) > 0:
        return '\033Ptmux;\033\033]{};rgb:{}\033\033\\\033\\'
    elif term and term.startswith('screen'):
        return '\033P\033]{};rgb:{}\033\\'
    else:
        return '\033]{};rgb:{}\033\\'

def _system_palette_template():
    """Returns a template for the terminal-color-setting-escape codes."""
    tmux = os.getenv('TMUX')
    term = (os.getenv('TERM') or os.getenv('TERMINAL'))
    if tmux and len(tmux) > 0:
        return '\033Ptmux;\033\033]4;{};rgb:{}\033\033\\\033\\'
    elif term and term.startswith('screen'):
        return '\033P\033]4;{};rgb:{}\033\\'
    else:
        return '\033]4;{};rgb:{}\033\\'

def set_theme(theme, brightness):
    if not theme:
        theme = _get_user_pref('theme')
        if not theme:
            raise ValueError('No theme found that could be set.')

    # Handle the possibility that a path was passed.
    path = theme
    if path and os.path.exists(path):
        add_theme(path)
        theme = _name_from_path(path)

    # Set the color palette.
    colors = _name_to_colors(theme)
    tmp = _system_palette_template()
    for i, c in enumerate(colors):
        # Emits the proper ANSI code
        print(tmp.format(i, c), end='')

    # Update the user theme
    _save_user_pref('theme', theme)

    defaults = {
        -1: {
            'fg': 8,
            'bg': 0,
            'cs': 18
            },
        0: {
            'fg': 7,
            'bg': 0,
            'cs': 18
            },
        1: {
            'fg': 19,
            'bg': 15,
            'cs': 19
            }
    }

    if brightness is None:
        default = defaults[0]
        fg = _get_user_pref('fg')
        fg = fg if fg is not None else default['fg']
        bg = _get_user_pref('bg')
        bg = bg if bg is not None else default['bg']
        cs = _get_user_pref('cs')
        cs = cs if cs is not None else default['cs']
    else:
        default = defaults[brightness]
        fg = default['fg']
        bg = default['bg']

        # Use the user's specified cursor color if possible.
        cs = _get_user_pref('cs')
        cs = cs if cs is not None else default['cs']

    # Scale to colorspaces smaller than 22
    scale = lambda v: 8 if len(colors) < 22 and v > 15 else v

    _set_target('fg', scale(fg))
    _set_target('bg', scale(bg))
    _set_target('cs', scale(cs))

def _set_target(target, value):
    target_n = {
        'fg': 10,
        'bg': 11,
        'cs': 12
            }[target]
    value = str(value)
    # Check if value is an index
    if len(value) < 6:
        theme = _get_user_pref('theme')
        if not theme:
            raise ValueError('First specify a colorscheme.')
        colors = _name_to_colors(theme)
        resolved = colors[int(value)]
    resolved = _cleanup(resolved)
    tmp = _target_template()
    print(tmp.format(target_n, resolved), end='')
    _save_user_pref(target, value)

def print_vimfile():
    raise NotImplemented

def print_colors(theme):
    if not theme:
        theme = _get_user_pref('theme')
        if not theme:
            raise ValueError('First specify a colorscheme.')
    colors = _name_to_colors(theme)
    for i, c in enumerate(colors):
        v = ';'.join([str(int(v, 16)) for v in c.split('/')])
        print('\x1b[38;2;{2}m{1:<9} \x1b[48;2;{2}m_______\x1b[0m # {0}'.format(i, c, v))

def cli():
    _mkdir_p(DATA_DIR)

    global _CLI
    _CLI = True

    parser = argparse.ArgumentParser(
        description=__doc__.split('\n')[0])
    sub = parser.add_subparsers()

    foreach = lambda func: lambda L: map(func, L)

    _add = sub.add_parser('add', help="adds one or more themes")
    _add.add_argument('themes', nargs='+', type=argparse.FileType('r'),
        help='the theme filepaths')
    _add.set_defaults(func=foreach(add_theme), key='themes')

    mv = sub.add_parser('mv', help="renames a theme")
    mv.add_argument('src')
    mv.add_argument('target')
    mv.set_defaults(func=mv_theme, keys=['src', 'target'])

    _set = sub.add_parser('set',
        help="sets the theme (and brightness)")
    _set.add_argument('-b', '--brightness', nargs='?',
        help="an integer in the range -1 to 1",
        type=int, choices=[-1, 0, 1], default=None)
    _set.add_argument('theme', nargs='?')
    _set.set_defaults(func=set_theme, keys=['theme', 'brightness'])

    rm = sub.add_parser('rm',
        help="removes one or more themes")
    rm.add_argument('themes', nargs='+')
    rm.set_defaults(func=foreach(rm_theme), key='themes')

    export = sub.add_parser('export',
        help="prints a theme to stdout")
    export.add_argument('theme', nargs='?')
    export.set_defaults(func=export_theme, key='theme')

    ls = sub.add_parser('ls',
        help="lists available themes")
    ls.set_defaults(func=ls_themes)

    vimfile = sub.add_parser('vimfile',
        help="prints a vim colorscheme that works for all themes")
    vimfile.set_defaults(func=print_vimfile)

    _print = sub.add_parser('print',
        help="prints terminal colors 0 - 21")
    _print.add_argument('theme', nargs='?')
    _print.set_defaults(func=print_colors, key='theme')

    # Manual fg/bg/cs setting
    set_target_fn = lambda target: lambda val: _set_target(target, val)

    bg = sub.add_parser('bg',
        help="sets the background")
    bg.add_argument('value', type=str,
            help='a color index or 6-digit hex value')
    bg.set_defaults(func=set_target_fn('bg'), key='value')

    fg = sub.add_parser('fg',
        help="sets the foreground")
    fg.add_argument('value', type=str,
            help='a color index or 6-digit hex value')
    fg.set_defaults(func=set_target_fn('fg'), key='value')

    cs = sub.add_parser('cs',
        help="sets the cursor color")
    cs.add_argument('value', type=str,
            help='a color index or 6-digit hex value')
    cs.set_defaults(func=set_target_fn('cs'), key='value')

    args = parser.parse_args()

    # Handle all subparsers
    d = vars(args)
    try:
        if 'keys' in args:
            args.func(**{k:d[k] for k in args.keys})
        elif 'key' in args:
            args.func(d[args.key])
        else:
            args.func()
    except ValueError as err:
        print(err.message)
        sys.exit(1)

if __name__ == "__main__":
    cli()
