import os
import abc
import sys
import importlib

from collections import defaultdict
from legallint.utils import get_basedir, check_subclass

class Plugin(abc.ABC):
    @abc.abstractmethod
    def get_name(self):
        """Returns the name of the plugin."""
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, data):
        """Processes the input data."""
        raise NotImplementedError

    @abc.abstractmethod
    def load_settings(self):
        """Load LegalLint settings"""
        raise NotImplementedError

class PluginManager:
    def __init__(self, plugindirs=None):
        self.plugindirs = plugindirs if plugindirs is not None else []
        self.plugins = defaultdict(list)
        self.basedir = get_basedir()

    def load_plugins(self, plugin=None):
        """Loads all plugins from the plugin directory."""
        self.plugindirs.insert(0, f"{self.basedir}/plugins")

        pth = os.getenv('LEGALLINT_PLUGINPATH')
        if pth is not None:
            self.plugindirs.extend(pth.split(os.pathsep))

        syspath = sys.path
        for eplugin in self.plugindirs:
            sys.path = [f"{eplugin}"] + syspath
            fnames = os.listdir(eplugin)

            for fname in fnames:
                if (fname.startswith(".#") or fname.startswith("__")):
                    continue
                if not fname.startswith("for_"):
                    continue
                elif fname.endswith(".py"):
                    modname = fname[:-3]
                    self._load_plugin(modname[4:], modname)
                elif fname.endswith(".pyc"):
                    modname = fname[:-4]
                    self._load_plugin(modname[4:], modname)
        sys.path = syspath
        return self.plugins


    def _load_plugin(self, lang, module):
        """Dynamically loads a plugin modules"""
        module = __import__(module)
        for attr in dir(module):
            plugin_class = getattr(module, attr)
            if isinstance(plugin_class, type) and check_subclass(plugin_class, Plugin):
                self.plugins[lang] = plugin_class()

    def get_plugins_by_language(self, lang):
        """Returns plugins that support a specific language."""
        for plugin in self.plugins.keys():
            if lang == plugin:
                return self.plugins[lang]
        print(f"plugin for given {lang} is not loaded")
    
    def get_supported_languages(self):
        return list(self.plugins.keys())

    def run_plugin(self, plugin_name):
        """Runs a specific plugin by name."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].run()
        else:
            raise ValueError(f"Plugin '{plugin_name}' not found.")
