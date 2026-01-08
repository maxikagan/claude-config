Set objShell = CreateObject("WScript.Shell")
objShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\kagan\.claude\hooks\focus-window.ps1"" """ & WScript.Arguments(0) & """", 0, False
