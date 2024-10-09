"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""
import os
from legallint.plugin import Plugin


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self, data):
        return f"Processed Python data: {data}"


#  create a class requirements.txt , dev-req.txt , req-dev.txt root direc scan find txt files / req / read that file store the data[] in a var list 



class Requirements:
    basedir = os.getcwd()  # Current working directory
    files = ['requirements.txt', 'dev-requirements.txt']  # List of potential requirements files ((dep, req,))
    dependencies = {}

    @classmethod
    def get_requirements_file(cls):
        """
        Locate the requirements file (requirements.txt or dev-requirements.txt) in the base directory.
        Returns the file path if found, otherwise returns None.
        """
        for filename in cls.files:
            fpath = os.path.join(cls.basedir, filename)
            if os.path.isfile(fpath):
                return fpath
        return None
    # we should get list files 

    @classmethod
    def get_dependencies(cls, fpath=None):
        """
        Read the requirements file and extract dependencies.
        Optionally take a specific file path.
        """
        if fpath is None:
            fpath = cls.get_requirements_file()
        
        if fpath is None:
            print("No requirements file found in the base directory.")
            return cls.dependencies

        try:
            with open(fpath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Ignore empty lines and comments
                        # Handle version specifications (e.g., package==version or package>=version)
                        package = line.split(' ')[0].split('==')[0].split('>=')[0]
                        cls.dependencies[package] = line  # Store full line for further use
        except Exception as e:
            print(f"Error reading requirements file: {e}")

        return cls.dependencies
    # we need only keys and it supposed to be a set not dict

    @classmethod
    def to_set(cls, deps=None):
        """
        Convert the collected dependencies into a set for uniqueness.
        """
        # {‘reqs’: [‘pytest’, ‘pandas’], ‘dev-requirements’: [‘mkdocs’]}
        return set(cls.dependencies.keys()) if deps is None else set(deps)
    
if __name__ == "__main__":
    fpath=  Requirements.get_requirements_file()
    if fpath:
        print(fpath)# it prints 
        deps= Requirements.get_dependencies(fpath=fpath)
        print(deps)


