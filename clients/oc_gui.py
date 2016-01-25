from __future__ import print_function
import wx
import os
import time
from threading import Thread

EVT_RESULT_ID = wx.NewId()

class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class GuiApp(wx.App):
    def __init__(self, filesz):
        self._filesz = filesz
        wx.App.__init__(self)

    def OnInit(self):
        self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)

        #self._frame = wx.Frame(None, -1, 'simple.py')
        #self._frame.Show()
        #self.SetTopWindow(self._frame)

        pd_style = wx.PD_SMOOTH
        self._dialog = wx.ProgressDialog(title="Uploading...",
                                         message="Uploading screenshot...",
                                         style=pd_style)
        self._dialog.Pulse(newmsg="Preparing...")
        self._dialog.SetFocus()


        return True
    
    def OnResult(self, event):
        if not event.data is None:
            if event.data == self._filesz:
                self._dialog.Destroy()
                #self._frame.Close()
                self.ExitMainLoop()
                wx.WakeUpMainThread()
            else:
                value = (event.data / self._filesz) * 100
                self._dialog.Update(value=value)

class AppThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self._app = app

    def run(self):
        self._app.MainLoop()

class FileReadDecorator(object):
    def __init__(self, decoratee, read_callback):
        self._decoratee = decoratee
        self._read_callback = read_callback

    def read(self, size = -1):
        data = self._decoratee.read(size)
        self._read_callback(data)

        return data

    def __getattr__(self, name):
        return getattr(self._decoratee, name)

class OcClientGuiDecorator(object):
    def __init__(self, decoratee):
        self._decoratee = decoratee

    def _read_progress(self, data):
        self._progress += len(data)
        wx.PostEvent(self._app, ResultEvent(self._progress))

    def share(self, filepath):
        filehandle = self._open_file_to_upload(filepath)
        filepath = filepath
        filesz = os.path.getsize(filepath)

        self._app = GuiApp(filesz)
        thread = AppThread(self._app)
        thread.start()

        return self._share(filehandle, filepath)

    def _open_file_to_upload(self, filepath):
        print ("upload!")
        self._progress = 0

        filehandle = open(filepath, 'rb')

        read_callback = self._read_progress
        fileprogress = FileReadDecorator(filehandle, read_callback)

        return fileprogress
    
    def __getattr__(self, name):
        return getattr(self._decoratee, name)
