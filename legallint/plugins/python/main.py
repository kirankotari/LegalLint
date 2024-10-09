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
            if dep not in {'idna', 'requests', 'packaging', 'iniconfig', 'certifi'}:
                continue
            lic = pylic.get_package_license(dep)
            print(f"{dep}: {lic}")
            # break
        return
"""
In [19]: for d in distributions():
    ...:     if d.metadata.get("Name") == 'urllib3':
    ...:         dist = d

In [36]: dist.locate_file('urllib3-1.26.13.dist-info/LICENSE.txt')
Out[36]: PosixPath('/Users/kkotari/.pyenv/versions/3.9.15/lib/python3.9/site-packages/urllib3-1.26.13.dist-info/LICENSE.txt')

In [37]: dist.read_text('/Users/kkotari/.pyenv/versions/3.9.15/lib/python3.9/site-packages/urllib3-1.26.13.dist-info/LICENSE.txt')
Out[37]: 'MIT License\n\nCopyright (c) 2008-2020 Andrey Petrov and contributors (see CONTRIBUTORS.txt)\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n'

"""
class PythonLicense(License):
    def __init__(self):
        super().__init__()
        self.licenses = super().get(is_print=False)
        self.license_set = {key.split('-')[0] for key in self.licenses if len(key.split('-')[0]) > 2}
        # print(self.license_set)

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
    # def get_package_license(self, pkg_name):
    #     try:
    #         dist = next(d for d in distributions() if d.metadata['Name'].lower() == pkg_name.lower())
    #         # Check the License field first
    #         license = dist.metadata.get('License', '').strip()
    #         if license.lower() in self.license_set:
    #             return self.license_set[license.lower()]

    #         license = dist.metadata.get('License-Expression', '').strip()
    #         if license.lower() in self.license_set:
    #             return self.license_set[license.lower()]

    #         classifers = dist.metadata.get_all('Classifier', [])
    #         for line in classifers:
    #             if 'license' not in line.lower():
    #                 continue
    #             license = {lic.lower() for lic in self.license_set.keys() if f"{lic} " in line.lower()}
    #             license = {self.license_set[each] for each in license}
    #             if not len(license):
    #                 break
    #             return license

    #         for each in dist.files:
    #             if 'LICENSE' in each.name:
    #                 path = each.locate()
    #                 print(path)
    #                 line = dist.read_text(each.locate().as_posix())
    #                 license = {lic for lic in self.licenses.keys() if f"{lic} " in line}
    #                 # license = {self.license_set[each] for each in license}
    #                 if len(license):
    #                     return license




    #         print(f"{pkg_name} license: {license}")
    #         # for k, v in dist.metadata.items():
    #         #     if str(k) == 'Description':
    #         #         continue
    #         #     print(f"{k}: {v}")

    #         # license = dist.metadata.get('License', '').strip()
    #         # print(f"from License: {license}")
    #         # if not license:
    #         #     # If no License field, check Classifications field (if available)
    #         #     license = next((item for item in dist.metadata.get('Classifications', []) if 'License' in item), '').strip()
    #         #     print(f"from Classification: {license}")
    #         #     if not license:
    #         #         # If no License and no Classifications, check README (if available)
    #         #         license = dist.metadata.get('Description', '').strip()  # Fall back to the 'Description' or README
    #         #         # print(f"from Description: {license}")
    #         return license
    #     except StopIteration:
    #         return None
        
    def check_license_keywords(self, pkg_name):
        """
        Checks if any of the license keywords match the package's license
        and returns all matching keywords.
        """
        license = self.get_package_license(pkg_name)
        if type(license) is str:
            return license
        
        if type(license) is set:
            def set_to_string(s):
                if len(s) == 1:
                    return next(iter(s))  # Get the single element in the set
                return s
            return set_to_string(license)
        matched_keywords = []

        # if license:
        #     matched_keywords.extend(
        #         keyword
        #         for keyword in self.licenses
        #         if keyword.lower() in license.lower()
        #     )
        return matched_keywords 

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

