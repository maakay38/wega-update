import os, winshell
from win32com.client import Dispatch

desktop = winshell.desktop()
path = os.path.join(desktop, "Teknisyen Portal.lnk")
target = os.path.abspath("TeknisyenPortal.exe")

shell = Dispatch('WScript.Shell')
s = shell.CreateShortCut(path)
s.Targetpath = target
s.WorkingDirectory = os.getcwd()
s.IconLocation = target
s.save()
