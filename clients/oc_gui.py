from __future__ import print_function
import wx
import os
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
        self._previous_bytes = 0

        wx.App.__init__(self)

    def updateProgress(self, event):
        self._dialog.UpdatePulse()

    def OnInit(self):
        self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)

        #self._frame = wx.Frame(None, -1, 'simple.py')
        #self._frame.Show()
        #self.SetTopWindow(self._frame)

        pd_style = wx.PD_SMOOTH
        self._dialog = wx.ProgressDialog(title="Uploading...",
                                         message="Uploading screenshot...",
                                         style=pd_style)
        self._dialog.UpdatePulse(newmsg="Preparing...")
        self._dialog.SetFocus()

        self._timer = wx.Timer()
        self.Bind(wx.EVT_TIMER, self.updateProgress, self._timer)
        self._timer.Start(50)

        return True
    
    def OnResult(self, event):
        if not event.data is None:
            if event.data == self._filesz:
                self._dialog.UpdatePulse(newmsg="Sharing...")
                self._timer.Start(50)
            elif event.data == "finished":
                self._dialog.Destroy()
                #self._frame.Close()
                self.ExitMainLoop()
                wx.WakeUpMainThread()
            else:
                self._timer.Stop()
                bytes_sent = event.data
                value = (float(bytes_sent) / self._filesz) * 100.0
                if (bytes_sent - self._previous_bytes) >= 256:
                    msg = ("Uploading (%d %%, %d/%d)" % (value,
                                                         bytes_sent,
                                                         self._filesz))
                    self._dialog.Update(value=value, newmsg=msg)
                    self._previous_bytes = bytes_sent
                else:
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
        data = self._decoratee.read(10)
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
        filesz = os.path.getsize(filepath)

        self._app = GuiApp(filesz)
        thread = AppThread(self._app)
        thread.start()

        result = self._share(filehandle, filepath)
        wx.PostEvent(self._app, ResultEvent("finished"))
        return result

    def _open_file_to_upload(self, filepath):
        self._progress = 0
        filehandle = open(filepath, 'rb')

        read_callback = self._read_progress
        fileprogress = FileReadDecorator(filehandle, read_callback)

        return fileprogress
    
    def __getattr__(self, name):
        return getattr(self._decoratee, name)
