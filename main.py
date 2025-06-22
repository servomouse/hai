from motions import Motions
from history import History
from memory import Memory
from semantic import SemanticCore


class Brain(History, Memory, Motions, SemanticCore):
    def __init__(self):
        self.inputs = {
            "text": [],
            "image": None
        }

    def tick(self):
        pass

    def text_input(self, text):
        pass

    def text_output(self, text):
        pass

    def image_input(self, image):
        pass

    def move(self, value):
        action = (value >> 8) & 0xFF
        param = value & 0xFF
        self.do_motion(action, param)
