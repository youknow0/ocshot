import ConfigParser as configparser
import os

class Config(object):
    INI_FILE = "ocshot.ini"

    def _create_default_config(self):
        if not os.path.isdir(self._config_path):
            os.mkdir(self._config_path)

    def __init__(self, config_path):
        self._config_path = config_path
        self._create_default_config()
        self.conf = configparser.ConfigParser()
    
    def _get_ini_path(self):
        return os.path.join(self._config_path, self.INI_FILE)

    def read(self):
        inipath = self._get_ini_path()
        self.conf.read(inipath)

    def write(self):
        initpath = self._get_ini_path()

        with open('w', inipath) as inifile:
            self.conf.write(inifile)

