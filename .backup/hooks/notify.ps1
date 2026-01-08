# Claude Code Windows Toast Notification Hook
# Uses BurntToast to display Windows toast notifications when Claude needs attention
# Install BurntToast: Install-Module -Name BurntToast -Scope CurrentUser -Force

$ErrorActionPreference = "SilentlyContinue"

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

    # Try to get the terminal/console window title by walking up the process tree
    $tabName = $null
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

    # Fallback to folder name if no tab name found
    if (-not $tabName) {
        if ($cwd) {
            $tabName = Split-Path -Leaf $cwd
        } else {
            $tabName = "Claude Code"
        }
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

    # Create and show the toast notification with sound
    New-BurntToastNotification -Text $title, $message -Sound "Default"

} catch {
    # Silent failure - don't block Claude Code
}

exit 0
