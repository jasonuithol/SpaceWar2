################################################################################
# input.py - Input Handler
################################################################################

from pyglet.window import key

class InputHandler:
    def __init__(self):
        self.inputs = {
            "thrust": False,
            "rotate_left": False,
            "rotate_right": False,
            "shoot": False,
            "respawn": False
        }
        
    def on_key_press(self, symbol, modifiers):
        """Handle key press"""
        if symbol == key.UP or symbol == key.W:
            self.inputs["thrust"] = True
        elif symbol == key.LEFT or symbol == key.A:
            self.inputs["rotate_left"] = True
        elif symbol == key.RIGHT or symbol == key.D:
            self.inputs["rotate_right"] = True
        elif symbol == key.SPACE:
            self.inputs["shoot"] = True
        elif symbol == key.R:
            self.inputs["respawn"] = True
    
    def on_key_release(self, symbol, modifiers):
        """Handle key release"""
        if symbol == key.UP or symbol == key.W:
            self.inputs["thrust"] = False
        elif symbol == key.LEFT or symbol == key.A:
            self.inputs["rotate_left"] = False
        elif symbol == key.RIGHT or symbol == key.D:
            self.inputs["rotate_right"] = False
        elif symbol == key.SPACE:
            self.inputs["shoot"] = False
        elif symbol == key.R:
            self.inputs["respawn"] = False
    
    def get_inputs(self) -> dict:
        """Get current input state"""
        return self.inputs.copy()
