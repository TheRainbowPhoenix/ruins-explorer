# cpgame/engine/text_parser.py
# A utility for parsing RPG-style control codes in text strings.

try:
    from typing import Optional
except:
    pass

from cpgame.systems.jrpg import JRPG

def _resolve_code(code: str, param: Optional[int]) -> str:
    """Helper function to convert a parsed code and param into a string."""
    code = code.upper()
    
    if code == 'V':
        if JRPG.objects and JRPG.objects.variables and param:
            return str(JRPG.objects.variables.value(param))
            
    elif code == 'S':
        if JRPG.objects and JRPG.objects.switches and param:
            # Switches return "True" or "False"
            return "ON" if JRPG.objects.switches.value(param) else "OFF"
    elif code == 'N':
        if JRPG.objects and JRPG.objects.actors and param:
            actor = JRPG.objects.actors[param]
            return actor.name if actor else ""
    elif code == 'HP':
        if JRPG.objects and JRPG.objects.actors and param:
            actor = JRPG.objects.actors[param]
            return str(actor.hp) if actor else "0"
    elif code == 'G':
        # Assumes no parameter for Gold, as is common
        if JRPG.objects and JRPG.objects.party:
            return str(JRPG.objects.party.gold) + " E" # Using Euro as per request
    
    # If code is unrecognized, return it literally
    return "\\" + code + ("[{}]".format(param) if param is not None else "")

def parse_text_codes(text: str) -> str:
    """
    Parses a string containing RPG-style control codes and replaces them
    with their corresponding game data values.
    """
    if '\\' not in text:
        return text

    result = ""
    pos = 0
    
    while pos < len(text):
        escape_pos = text.find('\\', pos)
        
        if escape_pos == -1:
            result += text[pos:]
            break
            
        # Append the plain text before the escape code
        result += text[pos:escape_pos]
        pos = escape_pos + 1

        # Check for special single-character codes like \G
        if text[pos] == 'G' or text[pos] == 'g':
            result += _resolve_code('G', None)
            pos += 1
            continue

        # Find the start of the command code
        code_start = pos
        while pos < len(text) and 'a' <= text[pos].lower() <= 'z':
            pos += 1
        
        code = text[code_start:pos]
        
        # Check for the opening bracket
        if pos < len(text) and text[pos] == '[':
            bracket_open_pos = pos
            bracket_close_pos = text.find(']', bracket_open_pos)
            
            if bracket_close_pos != -1:
                param_str = text[bracket_open_pos + 1 : bracket_close_pos]
                try:
                    param = int(param_str)
                    result += _resolve_code(code, param)
                    pos = bracket_close_pos + 1
                    continue
                except ValueError:
                    # Malformed parameter, treat as literal text
                    pass
        
        # If we fall through, it was a malformed code. Append literally.
        result += text[escape_pos:pos]

    return result