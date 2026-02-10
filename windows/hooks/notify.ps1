# Claude Code Windows Toast Notification Hook
# Uses BurntToast to display Windows toast notifications when Claude needs attention
# Install BurntToast: Install-Module -Name BurntToast -Scope CurrentUser -Force

$ErrorActionPreference = "SilentlyContinue"

# Add FlashWindow API for taskbar flashing (more reliable than toasts)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FlashWindow {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool FlashWindowEx(ref FLASHWINFO pwfi);

    [StructLayout(LayoutKind.Sequential)]
    public struct FLASHWINFO {
        public uint cbSize;
        public IntPtr hwnd;
        public uint dwFlags;
        public uint uCount;
        public uint dwTimeout;
    }

    public const uint FLASHW_ALL = 3;
    public const uint FLASHW_TIMERNOFG = 12;

    public static void Flash(IntPtr hwnd) {
        FLASHWINFO fi = new FLASHWINFO();
        fi.cbSize = (uint)Marshal.SizeOf(fi);
        fi.hwnd = hwnd;
        fi.dwFlags = FLASHW_ALL | FLASHW_TIMERNOFG;
        fi.uCount = 0;
        fi.dwTimeout = 0;
        FlashWindowEx(ref fi);
    }
}
"@

# Read JSON input from stdin
$jsonInput = ""
while ($line = [Console]::ReadLine()) {
    if ($null -eq $line) { break }
    $jsonInput += $line
}

if ([string]::IsNullOrWhiteSpace($jsonInput)) {
    exit 0
}

try {
    Import-Module BurntToast -ErrorAction Stop

    $data = $jsonInput | ConvertFrom-Json
    $message = if ($data.message) { $data.message } else { "Claude needs your attention" }
    $notificationType = $data.notification_type
    $cwd = $data.cwd
    $sessionId = $data.session_id

    # Create a friendly session name from session_id
    # Uses a persistent mapping file so the same session always gets the same number
    $sessionName = $null
    if ($sessionId) {
        $mappingFile = "$env:USERPROFILE\.claude\session-names.json"
        $mapping = @{}
        if (Test-Path $mappingFile) {
            try {
                $content = Get-Content $mappingFile -Raw -Encoding UTF8
                $parsed = $content | ConvertFrom-Json
                # Convert PSObject to hashtable
                $parsed.PSObject.Properties | ForEach-Object { $mapping[$_.Name] = $_.Value }
            } catch { $mapping = @{} }
        }

        if ($mapping.ContainsKey($sessionId)) {
            $sessionName = $mapping[$sessionId]
        } else {
            # Assign next available number
            $existingNums = @()
            foreach ($val in $mapping.Values) {
                if ($val -match "^session-(\d+)$") {
                    $existingNums += [int]$Matches[1]
                }
            }
            $nextNum = if ($existingNums.Count -gt 0) { ($existingNums | Measure-Object -Maximum).Maximum + 1 } else { 1 }
            $sessionName = "session-$nextNum"
            $mapping[$sessionId] = $sessionName
            $mapping | ConvertTo-Json | Set-Content $mappingFile -Encoding UTF8 -NoNewline
        }
    }

    # Try to get the terminal/console window info by walking up the process tree
    $tabName = $null
    $terminalPid = $null
    try {
        $currentPid = $PID
        $maxDepth = 10
        $depth = 0

        while ($currentPid -and $depth -lt $maxDepth) {
            $proc = Get-Process -Id $currentPid -ErrorAction SilentlyContinue
            if ($proc) {
                # Check if this is Windows Terminal or a console host with a title
                if ($proc.MainWindowTitle -and $proc.MainWindowTitle -ne "") {
                    $tabName = $proc.MainWindowTitle
                    $terminalPid = $proc.Id
                    break
                }
                # Move to parent process
                $parentQuery = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $currentPid" -ErrorAction SilentlyContinue
                if ($parentQuery) {
                    $currentPid = $parentQuery.ParentProcessId
                } else {
                    break
                }
            } else {
                break
            }
            $depth++
        }
    } catch {
        # Ignore errors in window title detection
    }

    # Priority for identifying the session:
    # 1. Session name (from session_id mapping) - most reliable
    # 2. Folder name from cwd - fallback
    # 3. "Claude Code" - last resort
    if ($sessionName) {
        $tabName = $sessionName
    } elseif ($cwd) {
        $tabName = Split-Path -Leaf $cwd
    } elseif (-not $tabName) {
        $tabName = "Claude Code"
    }

    # Format the title based on notification type
    $titlePrefix = switch ($notificationType) {
        "permission_prompt" { "Permission Needed" }
        "idle_prompt" { "Waiting for Input" }
        "elicitation_dialog" { "Input Required" }
        default { "Attention Needed" }
    }

    # Title format: [TabName] Permission Needed
    $title = "[$tabName] $titlePrefix"

    # Truncate message if too long for toast display
    if ($message.Length -gt 200) {
        $message = $message.Substring(0, 197) + "..."
    }

    # Flash the taskbar icon (most reliable attention-getter)
    if ($terminalPid) {
        try {
            $proc = Get-Process -Id $terminalPid -ErrorAction SilentlyContinue
            if ($proc -and $proc.MainWindowHandle -ne [IntPtr]::Zero) {
                [FlashWindow]::Flash($proc.MainWindowHandle)
            }
        } catch { }
    }

    # Play system notification sound (audible even when looking away)
    [System.Media.SystemSounds]::Exclamation.Play()

    # Create toast with click action to focus the terminal window
    if ($terminalPid) {
        # Save PID to temp file and use protocol to focus window when clicked
        $protocolUrl = "claude-focus:$terminalPid"

        # Build toast with protocol activation
        $text1 = New-BTText -Content $title
        $text2 = New-BTText -Content $message
        $binding = New-BTBinding -Children $text1, $text2
        $visual = New-BTVisual -BindingGeneric $binding
        $audio = New-BTAudio -Source "ms-winsoundevent:Notification.Default"

        # Create content with activation
        $content = New-BTContent -Visual $visual -Audio $audio -Launch $protocolUrl -ActivationType Protocol

        Submit-BTNotification -Content $content
    } else {
        # No terminal PID found, just show notification without click action
        New-BurntToastNotification -Text $title, $message -Sound "Default"
    }

} catch {
    # Silent failure - don't block Claude Code
}

exit 0
