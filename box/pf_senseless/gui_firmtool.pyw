#!/usr/bin/env python
import struct
import os
import threading
import socket

import wx

PORT = 6969
MAGIC = struct.pack('>I', 0x69420)
REQ_UPGRADE = b'\0'

class DiscoverThread(threading.Thread):
    def __init__(self, cb):
        threading.Thread.__init__(self)

        self.callback = cb
        self.start()

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(0.5)
            self.sock.bind(('', PORT))

            self.running = True
            while self.running:
                try:
                    data, src = self.sock.recvfrom(4)
                except socket.timeout:
                    continue

                if not data:
                    break
                if data != MAGIC:
                    continue

                wx.CallAfter(self.callback, src[0])
        except OSError as e:
            wx.CallAfter(self.callback, None, e=e)

    def stop(self):
        self.running = False

class UpgradeThread(threading.Thread):
    def __init__(self, file, router, cb):
        threading.Thread.__init__(self)

        self.file = file
        self.router = router

        self.callback = cb
        self.start()

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.router, PORT))

            sock.send(REQ_UPGRADE)

            with open(self.file, 'rb') as file:
                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0, os.SEEK_SET)

                pos = 0
                while sent := sock.sendfile(file, offset=pos, count=65536):
                    pos += sent
                    wx.CallAfter(self.callback, file.tell() / size)

            sock.close()
        except OSError as e:
            print(e)
            wx.CallAfter(self.callback, None, e=e)


class UpgradeWindow(wx.Frame):
    def __init__(self, parent):
        self.fw_path = ''
        self.dirname = ''
        self.router_list = set()
        self.router = ''

        wx.Frame.__init__(self, parent, title='Firmware upgrade',
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), size=(335, 255))

        pnl = wx.Panel(self)

        browse_button = wx.Button(pnl, wx.ID_ANY, label='Browse', pos=(10, 10))
        browse_button.Bind(wx.EVT_BUTTON, self.OnOpen)
        self.file_info = wx.StaticText(pnl, wx.ID_FILE, 'No file selected', pos=(105, 17))

        wx.StaticText(pnl, wx.ID_ANY, 'Routers:', pos=(10, 50))
        self.router_list_box = wx.ListBox(pnl, style=wx.LB_SINGLE | wx.LB_SORT, pos=(10, 73), size=(300, 100))
        self.router_list_box.Bind(wx.EVT_LISTBOX, self.OnRouterSelect)

        self.upgrade_button = wx.Button(pnl, wx.ID_SETUP, 'Upgrade', pos=(10, 180))
        self.upgrade_button.Disable()
        self.upgrade_button.Bind(wx.EVT_BUTTON, self.OnUpgrade)
        self.Show(True)

        self.discover_thread = DiscoverThread(self.OnRouter)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def Error(self, e, parent=None):
        wx.MessageDialog(parent if parent else self, f'Error: {e}', style=wx.OK | wx.ICON_ERROR).ShowModal()

    def OnClose(self, e):
        self.discover_thread.stop()
        self.Destroy()

    def OnOpen(self, e):
        dlg = wx.FileDialog(self, 'Choose firmware', self.dirname, '', 'pfSenseless firmware (*.fw)|*.fw',
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.fw_path = dlg.GetPath()
            self.dirname = dlg.GetDirectory()
            self.file_info.SetLabelText(dlg.GetFilename())

            if self.router:
                self.upgrade_button.Enable()
        dlg.Destroy()

    def OnRouter(self, addr, e=None):
        if e:
            self.Error(e)
            return

        if addr not in self.router_list:
            self.router_list.add(addr)
            self.router_list_box.Append(addr)

    def OnRouterSelect(self, e):
        self.router = e.GetString()
        if self.fw_path:
            self.upgrade_button.Enable()

    def OnUpgrade(self, e):
        self.progress = wx.ProgressDialog('Upgrading...', 'Sending firmware upgrade',
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
        self.upgrade_thread = UpgradeThread(self.fw_path, self.router, self.OnUpgradeProgress)

    def OnUpgradeProgress(self, progress, e=None):
        if e:
            self.Error(e, parent=self.progress)
            self.progress.Destroy()
            return

        self.progress.Update(int(progress * 100))
        if progress >= 1:
            self.progress.Destroy()
            self.progress = None

app = wx.App(False)
frame = UpgradeWindow(None)
app.MainLoop()
