# standard
import os
import json


# base directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# path to settings.ini file
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')


# default settings
DEFAULT = {
    'white': {
        'name': 'Kaveh',
        'time': 10 * 60  # ten min
    },
    'black': {
        'name': 'Amin',
        'time': 10 * 60  # ten min
    }
}


class Settings(object):
    """Settings API"""
    def __init__(self):
        if os.path.exists(SETTINGS_FILE):
            fh = open(SETTINGS_FILE, 'rt')
            self._content = json.loads(fh.read())
            fh.close()
        else:
            self._content = DEFAULT
            try:
                self.save()
            except Exception:
                pass

    def get(self, key, default=None):
        return self._content.get(key, default)

    def set(self, key, value):
        self._content[key] = value

    def save(self):
        fh = open(SETTINGS_FILE, 'wt')
        fh.write(json.dumps(self._content, indent=4))
        fh.close()


# create interface
_s = Settings()

get = _s.get

set = _s.set

save = _s.save
