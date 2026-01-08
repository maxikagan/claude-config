# Register a custom protocol handler for Claude Code notifications
# Run this once to enable click-to-focus functionality

$protocolName = "claude-focus"
$scriptPath = "C:\Users\kagan\.claude\hooks\focus-window.ps1"

# Create VBScript wrapper to run PowerShell completely hidden (no window flash)
$vbsPath = "C:\Users\kagan\.claude\hooks\focus-window.vbs"
$vbsContent = @"
Set objShell = CreateObject("WScript.Shell")
objShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""$scriptPath"" """ & WScript.Arguments(0) & """", 0, False
"@
$vbsContent | Out-File -FilePath $vbsPath -Encoding ASCII -Force

# Create the protocol handler in registry
$regPath = "HKCU:\Software\Classes\$protocolName"

# Create the protocol key
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "(Default)" -Value "URL:Claude Focus Protocol"
Set-ItemProperty -Path $regPath -Name "URL Protocol" -Value ""

# Create shell\open\command key
New-Item -Path "$regPath\shell\open\command" -Force | Out-Null
$command = "wscript.exe `"$vbsPath`" `"%1`""
Set-ItemProperty -Path "$regPath\shell\open\command" -Name "(Default)" -Value $command

Write-Host "Protocol handler 'claude-focus:' registered successfully!"
Write-Host "Click-to-focus will now run completely hidden."
