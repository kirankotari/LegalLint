from legallint.plugin import Plugin

class NodePlugin(Plugin):
    def get_name(self):
        return "node"

    def run(self):
        deps = None
        print(f"node deps found {deps}")
        return

    def load_settings(self):
        return None