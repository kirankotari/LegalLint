import os
from legallint.utils import read_toml, read_yaml, get_pwd

class Settings:
    basedir = os.getcwd()
    allowed_licenses = set()
    trigger_error_licenses = set()
    skip_libraries = set()

    config_files = ['pyproject.toml', 'legallint.yaml']
    # TODO: need to move pyprject.toml to python plugin

    @classmethod
    def load(cls):
        for file in cls.config_files:
            pth = f"{cls.basedir}/{file}"
            # print(pth)
            if 'toml' in file:
                config = read_toml(pth)
                if 'licenses' not in config:
                    continue
                cls.allowed_licenses = set(config['licenses'].get('allowed', []))
                cls.trigger_error_licenses = set(config['licenses'].get('trigger_error', []))
                cls.skip_libraries = set(config['licenses'].get('skip_libraries', []) or [])
            if 'yaml' in file:
                config = read_yaml(pth)
                # print(config)
                cls.allowed_licenses = set(config.get('allowed_licenses', []))
                cls.trigger_error_licenses = set(config.get('trigger_error_licenses', []))
                cls.skip_libraries = set(config.get('skip_libraries', []) or [])
        if len(cls.allowed_licenses) == 0 and len(cls.trigger_error_licenses) == 0:
            print("no legallint setting found.")

        cls.allowed_licenses |= {key.split('-')[0] for key in cls.allowed_licenses}
        cls.trigger_error_licenses |= {key.split('-')[0] for key in cls.trigger_error_licenses}

class LegalLint:
    def __init__(self, deps):
        Settings.load()
        self.allowed = set()
        self.errors = set()
        self.warnings = set()
        self.validate(deps)

    def validate(self, deps):
        marks = ('\u2714', '\u2716', '\u203C') # check, error, warning
        for dep, lic_set in deps.items():
            if dep in Settings.skip_libraries:
                continue
            for lic in lic_set:
                if lic in Settings.trigger_error_licenses:
                    self.errors.add(dep)
                    if dep in self.allowed:
                        self.allowed.remove(dep)
                    break
                if lic in Settings.allowed_licenses:
                    self.allowed.add(dep)
            if dep not in self.errors and dep not in self.allowed:
                self.warnings.add(dep)
        for dep, lic_set in deps.items():
            if dep in self.allowed:
                print(f"{marks[0]:<5} {dep:<20} {'; '.join(lic_set)}")
            if dep in self.errors:
                print(f"{marks[1]:<5} {dep:<20} {'; '.join(lic_set)}")
            if dep in self.warnings:
                print(f"{marks[2]:<5} {dep:<20} {'; '.join(lic_set)}")


