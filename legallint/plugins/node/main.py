from legallint.plugin import Plugin

class NodePlugin(Plugin):
    def get_name(self):
        return "node"

    def run(self, data):
        return f"Processed Node data: {data}"