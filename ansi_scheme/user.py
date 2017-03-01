import os
import errno
import json

def _mkdir_p(path):
    """mkdir -p `path`"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class User(object):
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def __init__(self):
        xdg = os.environ['XDG_DATA_HOME']
        data_dir = (os.path.join(xdg, 'ansi-scheme') if xdg else
                    os.path.abspath('~/.ansi-scheme'))
        _mkdir_p(data_dir)

        # Make sure the user settings file exists.
        settings_file = os.path.join(data_dir, 'settings.json')
        default_settings = {
                'scheme_name': 'default',
                'style_name': None
        }

        # Create the file if it doesn't exist yet.
        with open(settings_file, 'a+t') as f:
            f.seek(0)
            try:
                settings = json.loads(f.read())
            except ValueError:  # loads failure; set defaults
                settings = default_settings

        self.settings = settings
        self.data_dir = data_dir
        self.settings_file = settings_file
