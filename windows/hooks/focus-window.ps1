# Focus a window by process ID
# Called when clicking the Claude Code notification via protocol handler

param(
    [Parameter(Position=0)]
    [string]$Url
)

$ErrorActionPreference = "SilentlyContinue"

# Extract PID from URL (format: claude-focus:12345)
$targetPid = $null
if ($Url -match "claude-focus:(\d+)") {
    $targetPid = [int]$Matches[1]
} elseif ($Url -match "(\d+)") {
    $targetPid = [int]$Matches[1]
}

if (-not $targetPid) {
    exit 0
}

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WindowHelper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("user32.dll")]
    public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("kernel32.dll")]
    public static extern uint GetCurrentThreadId();
}
"@

try {
    $proc = Get-Process -Id $targetPid -ErrorAction Stop
    if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
        $hwnd = $proc.MainWindowHandle

        # Get foreground window's thread
        $foregroundHwnd = [WindowHelper]::GetForegroundWindow()
        $foregroundThreadId = [WindowHelper]::GetWindowThreadProcessId($foregroundHwnd, [ref]0)
        $currentThreadId = [WindowHelper]::GetCurrentThreadId()

        # Attach to foreground thread to allow SetForegroundWindow
        [WindowHelper]::AttachThreadInput($currentThreadId, $foregroundThreadId, $true)

        # Restore if minimized (SW_RESTORE = 9)
        if ([WindowHelper]::IsIconic($hwnd)) {
            [WindowHelper]::ShowWindow($hwnd, 9)
        }

        # Bring to foreground
        [WindowHelper]::SetForegroundWindow($hwnd)

        # Detach
        [WindowHelper]::AttachThreadInput($currentThreadId, $foregroundThreadId, $false)
    }
} catch {
    # Process may have ended
}
