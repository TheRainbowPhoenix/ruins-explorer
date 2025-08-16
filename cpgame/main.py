# main.py
# The main entry point for the entire game. Clean and simple.
import time
from gint import dclear, dtext, dupdate, C_WHITE, C_BLACK
from cpgame.engine.game import Game
from cpgame.game_scenes.menu_scene import MenuScene

def main():
    """Initializes and runs the game, starting with the MenuScene."""
    game = Game()
    try:
        game.start(MenuScene)
    except Exception as e:
        # This provides a clean crash screen on PC for easier debugging.
        dclear(C_WHITE)
        dtext(5, 5, C_BLACK, "FATAL ERROR:")
        # Try to print the error message line by line
        try:
            error_lines = str(e).split('\n')
            for i, line in enumerate(error_lines):
                dtext(5, 25 + i * 15, C_BLACK, line)
        except:
            dtext(5, 25, C_BLACK, "Could not display error.")
        dupdate()
        time.sleep(10)


main()