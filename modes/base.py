from modes.screenshot import ScreenshotMode

class BaseMode(object):

    def prepare(self):
        """
        always called before get_filepath

        implementations may chose to show GUI elements...
        """
        pass

    def get_filepath(self):
        raise NotImplemented()
    
    def cleanup(self):
        """
        cleanup after upload

        implementations shoud delete temporary files etc. here
        """
        pass

def factory(name, args):
    """
    factory for the mode classes
    """
    if name == "screenshot":
        return ScreenshotMode(args)
    else:
        raise ValueError("Unknown mode")
