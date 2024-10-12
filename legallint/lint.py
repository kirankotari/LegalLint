import os
from legallint.utils import read_yaml, exit
from legallint.exceptions import LegalLintError, LegalLintWarning, LegalLintInfo

class Settings:
    basedir = os.getcwd()
    allowed_licenses = set()
    trigger_error_licenses = set()
    skip_libraries = set()

    config_file = 'legallint.yaml'

    @classmethod
    def load(cls, settings):
        if (not settings) and (not os.path.isfile(f"{cls.basedir}/{cls.config_file}")):
            print("no legallint.yaml setting found.")
            exit()

        if not settings:
            config = read_yaml(f"{cls.basedir}/{cls.config_file}")
            cls.allowed_licenses = set(config.get('allowed_licenses', []))
            cls.trigger_error_licenses = set(config.get('trigger_error_licenses', []))
            cls.skip_libraries = set(config.get('skip_libraries', []) or [])

        if settings:
            cls.allowed_licenses, cls.trigger_error_licenses, cls.skip_libraries = settings

        cls.allowed_licenses |= {key.split('-')[0] for key in cls.allowed_licenses}
        cls.trigger_error_licenses |= {key.split('-')[0] for key in cls.trigger_error_licenses}

class LegalLint:
    def __init__(self, deps, settings=None):
        Settings.load(settings)
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

        if not len(Settings.trigger_error_licenses):
            self.errors |= self.warnings
            self.warnings = set()

        for dep, lic_set in deps.items():
            if dep in self.allowed:
                print(f"{marks[0]:<5} {dep:<20} {'; '.join(lic_set)}")
            if dep in self.errors:
                print(f"{marks[1]:<5} {dep:<20} {'; '.join(lic_set)}")
            if dep in self.warnings:
                print(f"{marks[2]:<5} {dep:<20} {'; '.join(lic_set)}")

        if len(self.errors):
            print(LegalLintError())
            exit(-1)
        if len(self.warnings):
            print(LegalLintWarning())
            exit(-1)
        print(LegalLintInfo())



