# cpgame/game_objects/interpreter.py
# An interpreter for executing event command lists.

from cpgame.systems.jrpg import JRPG
from cpgame.engine.logger import log

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
        self._branch: Dict[int, bool] = {}

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
        self._branch.clear()

    def clear(self):
        self._map_id = 0
        self._event_id = 0
        self._list = None
        self._index = 0
        self._wait_count = 0
        self._running = False
        self._branch.clear()

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
        indent = command.get("indent", 0)
        params = command.get("parameters", [])

        # Check if we are inside a skipped conditional branch
        if self._branch.get(indent, True) is False and code not in [111, 411, 412]:
            return True # Skip command

        if code == 101:   self.command_101(params); return False # Show Text
        elif code == 111: self.command_111(params, indent); return True # If
        elif code == 121: self.command_121(params); return True # Control Switches
        elif code == 122: self.command_122(params); return True # Control Variables
        elif code == 122: self.command_123(params); return True # Control Self Switch
        elif code == 122: self.command_124(params); return True # Control Timer
        elif code == 201: self.command_201(params); return False # Transfer Player
        elif code == 411: self.command_411(indent); return True # Else
        elif code == 412: return True # End If
        elif code == 501: self.command_501(params); return True # Set tile
        
        return True # Continue to next command immediately

    def _get_value_from_operand(self, operand_type, operand_param):
        """Helper to resolve different operand types to a single value."""
        if operand_type == 0: return operand_param # Constant
        if operand_type == 1 and JRPG.objects: return JRPG.objects.variables[operand_param] # Variable
        return 0

    def _get_event(self, event_id: int):
        """Helper to get an event by ID (0 means this event)."""
        target_id = self._event_id if event_id == 0 else event_id
        if JRPG.objects and JRPG.objects.map:
            for ev in JRPG.objects.map.events.values():
                if ev.id == target_id:
                    return ev
        
    
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

    def command_111(self, params: List[Any], indent: int):
        """Conditional Branch"""
        result = False
        branch_type = params[0]
        
        if JRPG.objects:
            if branch_type == 0: # Switch
                switch_id, value = params[1], params[2]
                result = (JRPG.objects.switches[switch_id] == (value == 0))
            elif branch_type == 1: # Variable
                var1_id, operand_type, operand, op = params[1], params[2], params[3], params[4]
                val1 = JRPG.objects.variables[var1_id]
                val2 = self._get_value_from_operand(operand_type, operand)
                
                if op == 0: result = (val1 == val2)
                elif op == 1: result = (val1 >= val2)
                elif op == 2: result = (val1 <= val2)
                elif op == 3: result = (val1 > val2)
                elif op == 4: result = (val1 < val2)
                elif op == 5: result = (val1 != val2)
                
            self._branch[indent] = result
        if not result:
            self.skip_branch()

    def command_411(self, indent: int):
        """Else"""
        # If the previous IF was true, then this ELSE block should be skipped.
        if self._branch.get(indent, False) is True:
            self.skip_branch()
    
    def skip_branch(self):
        """Skips commands until the indentation level decreases."""
        if self._list:
            start_indent = self._list[self._index]['indent']
            while self._index + 1 < len(self._list):
                next_command = self._list[self._index + 1]
                if next_command['indent'] <= start_indent:
                    break
                self._index += 1

    def command_121(self, params: List[Any]):
        """Control Switches"""
        start_id, end_id, op = params[0], params[1], params[2]
        value = (op == 0) # 0 is ON (True), 1 is OFF (False)

        if JRPG.objects:
            for i in range(start_id, end_id + 1):
                JRPG.objects.switches[i] = value
                # log("Set Switch #{} to {}".format(i, value))

    def command_122(self, params: List[Any]):
        """Control Variables"""
        start_id, end_id, op_type, operand_type = params[0], params[1], params[2], params[3]
        
        if JRPG.objects and JRPG.objects.variables:
            value = 0
            # Determine the value to operate with
            if operand_type == 0:  # Constant
                value = params[4]
            elif operand_type == 1: # Variable
                value = JRPG.objects.variables[params[4]]
            # TODO: Other operand types (Random, Game Data) can be added here
            
            # Iterate through the range of variables
            for i in range(start_id, end_id + 1):
                current_value = JRPG.objects.variables[i]
                # Perform the operation
                if op_type == 0: # Set
                    JRPG.objects.variables[i] = value
                elif op_type == 1: # Add
                    JRPG.objects.variables[i] = current_value + value
                elif op_type == 2: # Subtract
                    JRPG.objects.variables[i] = current_value - value
                # TODO: Other operations (Mul, Div, Mod) can be added here
    
    def command_123(self, params: List[Any]):
        """Control Self Switch"""
        switch_char, op = params[0], params[1]
        if self._event_id > 0:
            key = (self._map_id, self._event_id, switch_char)
            value = (op == 0) # 0 is ON, 1 is OFF
            if JRPG.objects:
                JRPG.objects.self_switches[key] = value
                log("Set Self Switch ({}) for Event {} to {}".format(key, self._event_id, value))

    def command_124(self, params: List[Any]):
        """Control Timer"""
        if JRPG.objects and JRPG.objects.timer:
            if params[0] == 0:  # Start
                seconds = params[1]
                JRPG.objects.timer.start(seconds)
            else:  # Stop
                JRPG.objects.timer.stop()

    def command_201(self, params: List[Any]):
        """Transfer Player"""
        if params[0] == 0: # Direct designation
            map_id, x, y = params[1], params[2], params[3]
        else: # Designation with variables (not implemented)
            map_id, x, y = 0, 0, 0
        
        if JRPG.objects and JRPG.objects.player:
            JRPG.objects.player.reserve_transfer(map_id, x, y)

    def command_501(self, params: List[Any]):
        """Change Event Graphic. Params: [event_id, tile_id_or_variable_id, is_variable]"""
        event_id, value, is_variable = params[0], params[1], params[2]
        event = self._get_event(event_id)
        if event and JRPG.objects:
            tile_id = JRPG.objects.variables[value] if is_variable else value
            event.set_graphic(tile_id)
    
    # TODO: add more 