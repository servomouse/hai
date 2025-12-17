
class OutputProcessor:
    def __init__(self):
        pass

class TextOutput(OutputProcessor):
    def __init__(self):
        pass

class AudioOutput(OutputProcessor):
    def __init__(self):
        pass

class HardwareOutput(OutputProcessor):
    def __init__(self):
        pass


class OutputHub:
    def __init__(self, input_hub):
        self.text_input = TextOutput()
        self.audio_input = AudioOutput()
        self.hw_input = HardwareOutput()
        self.input_hub = input_hub
