from inputs import InputHub
from outputs import OutputHub


class Memory:
    def __init__(self):
        pass

class Scratchpad:
    def __init__(self):
        pass

class ThinkingCore:
    def __init__(self):
        pass


class Brain:
    def __init__(self):
        self.inputs = {
            "text": [],
            "image": None
        }
        self.ihub = InputHub()
        self.scrpad = Scratchpad()
        self.memory = Memory()
        self.tcore = ThinkingCore()
        self.ohub = OutputHub(self.ihub)

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
