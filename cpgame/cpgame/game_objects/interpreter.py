# cpgame/game_objects/interpreter.py
# An interpreter for executing event command lists.

from cpgame.systems.jrpg import JRPG

try:
    from typing import Dict, Any, List, Optional
except:
    pass

class GameInterpreter:
    """
    Executes a list of event commands. This is a simplified version
    that does not use fibers but processes commands sequentially.
    """
    def __init__(self):
        self._map_id = 0
        self._event_id = 0
        self._list: Optional[List[Dict]] = None
        self._index = 0
        self._wait_count = 0
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def setup(self, command_list: List[Dict], event_id: int = 0):
        """Sets up the interpreter with a new command list."""
        self.clear()
        
        if JRPG.objects and JRPG.objects.map:
            self._map_id = JRPG.objects.map._map_id
        else:
            self._map_id = 0
        
        self._event_id = event_id
        self._list = command_list
        self._running = True

    def clear(self):
        self._map_id = 0
        self._event_id = 0
        self._list = None
        self._index = 0
        self._wait_count = 0
        self._running = False

    def update(self):
        """Updates the interpreter. Called once per frame."""
        if not self._running:
            return

        if self._wait_count > 0:
            self._wait_count -= 1
            return

        # Loop to execute commands until a wait is required
        while self._list and self._index < len(self._list):
            command = self._list[self._index]
            if not self.execute_command(command):
                # If execute_command returns False, it means we need to wait
                return
            self._index += 1
        
        # If we reach here, the event is finished
        self.clear()

    def execute_command(self, command: Dict) -> bool:
        """Executes a single command and returns True if execution can continue."""
        code = command.get("code", 0)
        params = command.get("parameters", [])

        if code == 101: # Show Text
            self.command_101(params)
            return False # Wait for dialog
        elif code == 201: # Transfer Player
            self.command_201(params)
            return False # Wait for transfer
        # Add other commands here with `elif code == ...:`
        
        return True # Continue to next command immediately

    # --- Command Implementations ---

    def command_101(self, params: List[Any]):
        """Show Text"""
        # In a full engine, you'd handle face graphics, position, etc.
        # Here we just find all subsequent text lines.
        text_lines = []
        if not self._list or not JRPG.objects:
            return
        
        # TODO: Add this !!
        # JRPG.objects.message.face_name = params[0]
        # JRPG.objects.message.face_index = params[1]
        # JRPG.objects.message.background = params[2]
        # JRPG.objects.message.position = params[3]
        
        while self._index + 1 < len(self._list) and self._list[self._index + 1]["code"] == 401:
            self._index += 1
            text_lines.append(self._list[self._index]["parameters"][0])
            # TODO: JRPG.objects.message.add(self._list[self._index]["parameters"][0])
        
        try:
            next_event_code = self._list[self._index]["code"]
            if next_event_code == 102: # Show Choices
                self._index += 1
                pass
            elif next_event_code == 103: # Input Number
                self._index += 1
                pass
            elif next_event_code == 104: # Select Item
                self._index += 1
                pass
        except:
            pass

        # wait_for_message
        # TODO: this should be removed later
        JRPG.objects.show_text(text_lines)

        

    def command_201(self, params: List[Any]):
        """Transfer Player"""
        if params[0] == 0: # Direct designation
            map_id, x, y = params[1], params[2], params[3]
        else: # Designation with variables (not implemented)
            map_id, x, y = 0, 0, 0
        
        if JRPG.objects and JRPG.objects.player:
            JRPG.objects.player.reserve_transfer(map_id, x, y)
    
    # TODO: add more 