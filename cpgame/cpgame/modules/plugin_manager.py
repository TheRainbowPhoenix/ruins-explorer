# cpgame/modules/plugin_manager.py
# Registers and executes custom, string-based commands from events.

try:
    from typing import Dict, Any, List, Callable
except:
    pass

from cpgame.engine.logger import log

class PluginManager:
    def __init__(self):
        self._commands: Dict[str, Callable] = {}

    def register(self, command_name: str, function: Callable):
        """Registers a Python function to be callable by a string name."""
        log("PluginManager: Registering command '{}'".format(command_name))
        self._commands[command_name] = function

    def execute(self, command_string: str):
        """Parses and executes a command string like 'command(param1, 123)'."""
        log("PluginManager: Executing '{}'".format(command_string))
        try:
            name, params = self._parse_command(command_string)
            if name in self._commands:
                self._commands[name](*params)
            else:
                log("PluginManager Error: Command '{}' not found.".format(name))
        except Exception as e:
            log("PluginManager Error executing '{}': {}".format(command_string, e))

    def _parse_command(self, command_string: str) -> tuple:
        """A simple, non-regex parser for 'command(p1,p2,...)' format."""
        open_paren = command_string.find('(')
        close_paren = command_string.rfind(')')
        
        if open_paren == -1 or close_paren == -1:
            return command_string, []

        name = command_string[:open_paren]
        params_str = command_string[open_paren + 1 : close_paren]
        
        if not params_str:
            return name, []
            
        raw_params = params_str.split(',')
        params = []
        for p in raw_params:
            p = p.strip()
            try:
                params.append(int(p))
            except ValueError:
                # Remove quotes from strings
                if len(p) > 1 and p.startswith("'") and p.endswith("'"):
                    params.append(p[1:-1])
                else:
                    params.append(p)
        return name, params