# Simple access to .ini files

from pathlib import Path
import configparser
import os

class IniManager:
    def __init__(self, filename):
        self.filename = filename
        self.config = configparser.ConfigParser()
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                self.config.read_file(f)

    def getvalue(self, section, key, default=None):
        """Returns the value corresponding to specified section and key"""
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        return default

    def setvalue(self, section, key, value):
        """Set specified valued in [section] ->  key"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        # with open(self.filename, "w", encoding="utf-8") as f:
        fn = Path(self.filename).resolve()
        with open(fn, "w", encoding="utf-8") as f:
            self.config.write(f)

    def getkeys(self, section):
        keys = None
        if self.config.has_section(section):
            keys = list(dict(self.config[section]).keys())
        return keys

    def getsection(self, section):
        return self.config[section]

    def reload(self):
        """Rilegge il file INI da disco, aggiornando la cache."""
        self.config.read(self.filename, encoding='utf-8')