import pyscreenshot
import tempfile
import os

class ScreenshotMode(object):
    EXTENSION = ".png"

    def __init__(self, args):
        self._args = args
        self._current_file = None

    def _make_screenshot(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=False,
                                              suffix=self.EXTENSION)
        pyscreenshot.grab_to_file(tmpfile.name)

        return tmpfile

    def prepare(self):
        self._current_file = self._make_screenshot()

    def get_filepath(self):
        if self._current_file == None:
            raise "prepare not called before get_filepath"

        return self._current_file.name

    def cleanup(self):
        if self._current_file == None:
            raise "prepare not called before cleanup"

        self._current_file.close()
        os.remove(self._current_file.name)
