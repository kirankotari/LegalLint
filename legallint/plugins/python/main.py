"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""
import re
from importlib.metadata import distributions

from legallint.plugin import Plugin
from legallint.license.update import License
from legallint.utils import get_pwd, get_lines, get_matching_keys, read_toml, flatten_set


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self):
        Toml.get_dependencies()
        deps = Toml.to_set()

        # if not deps:
        #     deps = Reqs.get_dependencies()

        # print(f"python deps found {deps}")
        Expand.map_dependencies_by_package()
        deps = Expand.get_dependencies(deps)
        deps = deps - Expand.not_installed
        print(f"python deps expanded {deps}")
        pylic = PythonLicense()
        for dep in deps:
            lic = pylic.get_package_license(dep)
            print(f"{dep}: {pylic.set_to_string(lic)}")
            # break
        return


class PythonLicense(License):
    def __init__(self):
        super().__init__()
        self.licenses = super().get(is_print=False)
        self.license_set = {key.split('-')[0] for key in self.licenses if len(key.split('-')[0]) > 2}
        # print(self.license_set)

    def set_to_string(self, value_set):
        return next(iter(value_set)) if len(value_set) == 1 else value_set

    def get_package_license(self, pkg_name):
        try:
            dist = next(d for d in distributions() if d.metadata['Name'].lower() == pkg_name.lower())

            if license := self._get_license_from_metadata(dist, 'License'):
                return license

            if license := self._get_license_from_metadata(dist, 'License-Expression'):
                return license

            if license := self._get_license_from_classifiers(dist):
                return license

            if license := self._get_license_from_files(dist):
                return license

        except StopIteration:
            print(f"Package '{pkg_name}' not found.")
            return None

        return None

    # Helper function to retrieve license from metadata fields
    def _get_license_from_metadata(self, dist, field_name):
        return dist.metadata.get(field_name, '').strip()

    # Helper function to check classifiers for licenses
    def _get_license_from_classifiers(self, dist):
        classifiers = dist.metadata.get_all('Classifier', [])
        pkg_licenses = set()
        for line in classifiers:
            if 'license' not in line.lower():
                continue
            if license := {
                lic for lic in self.licenses if f"{lic} " in line} or {
                lic for lic in self.license_set if f"{lic} " in line}:
                pkg_licenses |= license
        return pkg_licenses or None


    # Helper function to check LICENSE files in the distribution
    def _get_license_from_files(self, dist):
        pkg_licenses = set()
        for each in dist.files:
            if 'LICENSE' in each.name.upper():
                license_path = each.locate().as_posix()
                license_content = dist.read_text(license_path)
                if license := {
                    lic for lic in self.licenses if lic in license_content} or {
                    lic for lic in self.license_set if lic in license_content}:
                    pkg_licenses |= license
        return pkg_licenses or None


class Expand:
    dep_map = {}
    visited, not_installed = set(), set()

    dep_pattern = re.compile(r"([a-zA-Z0-9\-_]+)")

    @classmethod
    def get_dependencies(cls, pkgs_set):
        """
        Recursively get all dependencies (including dependencies of dependencies).
        """
        dependencies = set()

        for pkg_name in pkgs_set:
            if pkg_name in cls.visited:
                continue
            cls.visited.add(pkg_name)

            if pkg_name not in cls.dep_map:
                cls.not_installed.add(pkg_name)
                continue

            direct_deps = cls.dep_map.get(pkg_name, set())
            dependencies |= direct_deps

            # Recursively find dependencies for each direct dependency
            for dep in direct_deps:
                dependencies |= cls.get_dependencies({dep})

        dependencies |= pkgs_set
        return dependencies

    @classmethod
    def map_dependencies_by_package(cls):
        """
        Maps each package to its direct dependencies.
        """

        for dist in distributions():
            dist_name = dist.metadata.get('Name')
            if dist.requires:
                cls.dep_map[dist_name] = {cls.dep_pattern.match(dep).group(1) for dep in dist.requires}
            else:
                cls.dep_map[dist_name] = set()  # No dependencies



class Toml:
    basedir = get_pwd()
    file = 'pyproject.toml'
    dependencies = {}

    @classmethod
    def get_dependencies(cls, fpath=None):
        if not fpath:
            fpath = f"{cls.basedir}/{cls.file}"
        config = read_toml(fpath)

        # Poetry dependencies
        if 'tool' in config and 'poetry' in config['tool']:
            poetry = config['tool']['poetry']
            for matched_key in get_matching_keys('dependencies', list(poetry.keys())):
                # print(poetry[matched_key])
                if 'python' in poetry[matched_key]:
                    del poetry[matched_key]['python']
                cls.dependencies[matched_key] = list(poetry[matched_key].keys())
            if 'group' in poetry:
                for group, group_deps in poetry['group'].items():
                    if 'dependencies' in group_deps:
                        # print(group_deps['dependencies'])
                        cls.dependencies[group] = list(group_deps['dependencies'].keys())

        # Setuptools dependencies (if present)
        if 'project' in config and 'dependencies' in config['project']:
            cls.dependencies['setuptools'] = [
                each.split('>=')[0] if '>=' in each else each.split('==')[0] if '==' in each else each
                for each in config['project']['dependencies']
            ]
        return cls.dependencies
    
    @classmethod
    def to_set(cls, deps=None):
        return flatten_set(cls.dependencies) if not deps and cls.dependencies else set()


if __name__ == "__main__":
    Toml.get_dependencies()
    deps = Toml.to_set()
    print(deps)
    deps = Expand.get_dependencies(deps)
    print(deps)

