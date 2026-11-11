' run-hunter.vbs - hidden runner for AI-Hunter autostart task
Set shell = CreateObject("WScript.Shell")
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\user\Documents\agent-memory\projects\client-search\hunter\start-hunter.ps1""", 0, False
