from modes.screenshot import ScreenshotMode
from modes.screenshot_region import ScreenshotRegionMode
import sys
from textwrap import dedent

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

class HelpMode(BaseMode):
    def __init__(self, args):
        pass

    def prepare(self):
        print (dedent("""
               available modes:

               screenshot: create a screenshot of the whole screen.
               this is the most portable way as it uses pyscreenshot
               internally.

               screenshot_region: create a screenshot of a screen
               region. this will allow you to chose a screen region.
               it uses scrot internally and thus only works on linux.
               """))
        sys.exit(0)

def factory(name, args):
    """
    factory for the mode classes
    """
    if name == "screenshot":
        return ScreenshotMode(args)
    if name == "screenshot_region":
        return ScreenshotRegionMode(args)
    elif name == "help":
        return HelpMode(args)
    else:
        raise ValueError("Unknown mode")
