"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""

from legallint.plugin import Plugin
from legallint.utils import get_pwd, get_lines, get_matching_keys, read_toml


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self, data):
        return f"Processed Python data: {data}"


class Toml:
    basedir = get_pwd()
    file = 'pyproject.toml'

    @classmethod
    def get_dependencies(cls, fpath=None):
        if not fpath:
            fpath = f"{cls.basedir}/{cls.file}"
        config = read_toml(fpath)

        dependencies = {}
        # Poetry dependencies
        if 'tool' in config and 'poetry' in config['tool']:
            poetry = config['tool']['poetry']
            for matched_key in get_matching_keys('dependencies', list(poetry.keys())):
                if 'python' in poetry[matched_key]:
                    del poetry[matched_key]['python']
                dependencies[matched_key] = list(poetry[matched_key].keys())
            if 'group' in poetry:
                for group, group_deps in poetry['group'].items():
                    if 'dependencies' in group_deps:
                        dependencies[group] = list(group_deps['dependencies'].keys())

        # Setuptools dependencies (if present)
        if 'project' in config and 'dependencies' in config['project']:
            dependencies['setuptools'] = [
                each.split('>=')[0] if '>=' in each else each.split('==')[0] if '==' in each else each
                for each in config['project']['dependencies']
            ]
        return dependencies



if __name__ == "__main__":
    print(Toml.get_dependencies())

