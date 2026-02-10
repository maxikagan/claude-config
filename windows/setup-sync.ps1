# Claude Config Sync Setup Script (Windows PowerShell)
# Run this after cloning your claude-config repo to set up symlinks

param(
    [string]$RepoPath = "$env:USERPROFILE\repos\claude-config"
)

$ClaudeDir = "$env:USERPROFILE\.claude"

# Check if repo exists
if (-not (Test-Path $RepoPath)) {
    Write-Host "Error: Repo not found at $RepoPath" -ForegroundColor Red
    Write-Host "Clone your repo first, or specify path: .\setup-sync.ps1 -RepoPath 'C:\path\to\repo'"
    exit 1
}

# Remove existing directories/files and create symlinks
$items = @("commands", "skills", "agents")

foreach ($item in $items) {
    $target = "$ClaudeDir\$item"
    $source = "$RepoPath\$item"

    if (Test-Path $target) {
        Write-Host "Removing existing $target..."
        Remove-Item $target -Recurse -Force
    }

    Write-Host "Creating symlink: $target -> $source"
    New-Item -ItemType SymbolicLink -Path $target -Target $source -Force
}

# Symlink settings.json
$settingsTarget = "$ClaudeDir\settings.json"
$settingsSource = "$RepoPath\settings.json"

if (Test-Path $settingsTarget) {
    Remove-Item $settingsTarget -Force
}
Write-Host "Creating symlink: $settingsTarget -> $settingsSource"
New-Item -ItemType SymbolicLink -Path $settingsTarget -Target $settingsSource -Force

Write-Host "`nSync setup complete!" -ForegroundColor Green
