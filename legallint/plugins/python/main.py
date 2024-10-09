"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""
import re
from importlib.metadata import distributions

from legallint.plugin import Plugin
from legallint.utils import get_pwd, get_lines, get_matching_keys, read_toml, flatten_set


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self):
        Toml.get_dependencies()
        deps = Toml.to_set()

        # if not deps:
        #     Reqs.get_dependencies()
        #     deps = Reqs.to_set()

        # print(f"python deps found {deps}")

        Expand.map_dependencies_by_package()
        deps = Expand.get_dependencies(deps)
        deps = deps - Expand.not_installed
        # print(f"python deps expanded {deps}")
        return


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

""" filter_dependencies by platform, python, extras
import sys
import platform

# Define the dependencies (as if from a pyproject.toml file)
install_requires = [
    "requests>=2.25.1; python_version >= '3.6'",
    "pytest>=6.2",  # Regular pytest dependency
    "pytest[mock]"  # pytest with mock extra
]

extras_require = {
    "win32": ["pywin32; sys_platform == 'win32'"],
    "linux": ["some-linux-specific-package; sys_platform == 'linux'"],
    "testing": ["pytest>=6.2", "pytest[mock]"]  # Add a custom testing extra
}

toml_dependencies = {
    "dependencies": [
        {"package": "requests", "version": "^2.25.1", "optional": False, "markers": "python_version >= '3.6'"},
        {"package": "pywin32", "version": "^300", "optional": True, "markers": "sys_platform == 'win32'"},
        {"package": "some-linux-specific-package", "version": "^1.0", "optional": True, "markers": "sys_platform == 'linux'"},
        {"package": "pytest", "version": ">=6.2", "optional": False, "markers": ""},
        {"package": "pytest[mock]", "version": "", "optional": False, "markers": ""}
    ]
}

# Function to filter dependencies based on conditions
def filter_dependencies(dependencies, python_version=sys.version_info, sys_platform=platform.system(), extras_enabled=set()):
    filtered_deps = []

    for dep in dependencies:
        if isinstance(dep, dict):
            package = dep["package"]
            version = dep["version"]
            optional = dep["optional"]
            markers = dep.get("markers", "")

            # If markers are provided, evaluate the condition
            if markers:
                if eval(markers, {"python_version": python_version, "sys_platform": sys_platform}):
                    filtered_deps.append(f"{package}{version if version else ''}")
            elif not markers:
                filtered_deps.append(f"{package}{version if version else ''}")

        elif isinstance(dep, str):
            # Handle install_requires or any other string-based dependency
            if ';' in dep:
                dep, condition = dep.split(';')
                if eval(condition, {"python_version": python_version, "sys_platform": sys_platform}):
                    filtered_deps.append(dep.strip())
            else:
                filtered_deps.append(dep.strip())

    # Check for extra dependencies if provided
    filtered_extras = []
    for extra, deps in extras_require.items():
        if extra in extras_enabled:
            filtered_extras.extend(filter_dependencies(deps, python_version, sys_platform, extras_enabled))

    return filtered_deps + filtered_extras

# Filter install_requires and optional dependencies
filtered_install_requires = filter_dependencies(install_requires)

# Filter TOML dependencies
filtered_toml_dependencies = filter_dependencies(toml_dependencies["dependencies"])

# Enable "testing" extra as an example (this can be dynamic based on user input)
extras_enabled = {"testing", "win32", "linux"}  # Let's say we want to enable "testing", "win32", and "linux" extras

# Output the filtered dependencies
print("Filtered install_requires:", filtered_install_requires)
print("Filtered TOML dependencies:", filtered_toml_dependencies)
print("Filtered extras (based on enabled extras):", filter_dependencies(extras_require.get("testing", []), extras_enabled=extras_enabled))

"""