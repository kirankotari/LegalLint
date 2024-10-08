"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""

from legallint.plugin import Plugin


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self, data):
        return f"Processed Python data: {data}"