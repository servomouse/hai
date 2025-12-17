

class InputProcessor:
    def __init__(self):
        pass

class TextProcessor(InputProcessor):
    def __init__(self):
        pass

class AudioProcessor(InputProcessor):
    def __init__(self):
        pass

class VideoProcessor(InputProcessor):
    def __init__(self):
        pass

class HardwareProcessor(InputProcessor):
    """ Hardware signals processor """
    def __init__(self):
        pass

class InputHub:
    def __init__(self):
        self.text_input = TextProcessor()
        self.audio_input = AudioProcessor()
        self.video_input = VideoProcessor()
        self.hw_input = HardwareProcessor()
        self.inputs = {
            "text": [],
            "image": None,
            "audio": None,
            "feedback": None,
            "hw_data": None
        }
