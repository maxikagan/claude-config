#!/usr/bin/env pwsh
# Git status hook for Claude Code configuration sync
# Checks if claude-config repo is out of sync with remote

$ErrorActionPreference = "SilentlyContinue"

# Path to the claude-config repo
$RepoPath = "$env:USERPROFILE\repos\claude-config"

# Check if repo exists
if (-not (Test-Path "$RepoPath\.git")) {
    Write-Output "WARNING: claude-config repo not found at $RepoPath"
    exit 0
}

$output = @()
$output += "=== Claude Config Sync Status ==="

# Get current branch
$branch = git -C $RepoPath branch --show-current 2>$null
if ($branch) {
    $output += "Branch: $branch"
} else {
    $output += "Branch: (detached HEAD)"
}

# Fetch from remote (silently)
git -C $RepoPath fetch --quiet 2>$null

# Check if we're behind/ahead of remote
$tracking = git -C $RepoPath rev-parse --abbrev-ref "@{upstream}" 2>$null
if ($tracking) {
    $behind = git -C $RepoPath rev-list --count "HEAD..$tracking" 2>$null
    $ahead = git -C $RepoPath rev-list --count "$tracking..HEAD" 2>$null

    if ([int]$behind -gt 0) {
        $output += "WARNING: $behind commit(s) behind remote - consider pulling!"
    }
    if ([int]$ahead -gt 0) {
        $output += "INFO: $ahead commit(s) ahead of remote (unpushed)"
    }
    if ([int]$behind -eq 0 -and [int]$ahead -eq 0) {
        $output += "Up to date with $tracking"
    }
} else {
    $output += "No upstream tracking branch set"
}

# Show working tree status summary
$status = git -C $RepoPath status --porcelain 2>$null
if ($status) {
    $modified = ($status | Where-Object { $_ -match "^ M|^M" }).Count
    $added = ($status | Where-Object { $_ -match "^A" }).Count
    $deleted = ($status | Where-Object { $_ -match "^ D|^D" }).Count
    $untracked = ($status | Where-Object { $_ -match "^\?\?" }).Count

    $changes = @()
    if ($modified -gt 0) { $changes += "$modified modified" }
    if ($added -gt 0) { $changes += "$added staged" }
    if ($deleted -gt 0) { $changes += "$deleted deleted" }
    if ($untracked -gt 0) { $changes += "$untracked untracked" }

    $output += "Local changes: $($changes -join ', ')"
} else {
    $output += "Working tree: clean"
}

$output += "================================="

# Output to stdout for Claude's context
$output | ForEach-Object { Write-Output $_ }
