from legallint.plugin import Plugin

class NpmPlugin(Plugin):
    def get_name(self):
        return "npm"

    def run(self):
        deps = None
        # print(f"npm deps found {deps}")
        return

    def load_settings(self):
        return None