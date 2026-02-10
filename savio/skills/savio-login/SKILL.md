---
name: savio-login
description: Guide for logging into Savio HPC and establishing stable SSH connections
user-invocable: true
allowed-tools: Bash, Read
---

# Savio Login Helper

Help the user establish SSH connections to Savio HPC cluster.

## Usage

```
/savio-login [action]
```

Actions:
- `status` - Check if certificate exists and is valid
- `renew` - Guide through certificate renewal
- `config` - Show/setup SSH config
- (no argument) - Full connection guide

## Key Facts

- Username: `maxkagan`
- **The user runs PowerShell as their primary terminal.** All commands given to the user MUST be PowerShell-compatible. Use `& "C:\Program Files\Git\bin\bash.exe" -c "..."` to wrap bash commands when needed. Never use `&&` (use `;` in PowerShell) or bare bash syntax.
- This is a Windows machine using WSL. Two separate filesystems matter:
  - **Windows**: `C:\Users\kagan\.ssh\ssh_certs\` (used by VS Code and PowerShell SSH)
  - **WSL**: `/home/mkagan/.ssh/ssh_certs/` (used by WSL bash)
- VS Code Remote-SSH uses the **Windows** SSH client and config at `C:\Users\kagan\.ssh\config`
- The cert renewal script is interactive (requires PIN+OTP) and cannot be run from Claude's Bash tool

## Connection Methods

### 1. SSH Certificate (Recommended)

Certificates enable passwordless login for 12 hours. The setup script is at `~/repos/lrc-scripts/request_cert.sh`.

**Check certificate status (check BOTH locations):**
```bash
# Windows side (what VS Code uses)
ssh-keygen -L -f /c/Users/kagan/.ssh/ssh_certs/brc_cert-cert.pub 2>/dev/null | grep Valid

# WSL side
wsl -e bash -c "ssh-keygen -L -f ~/.ssh/ssh_certs/brc_cert-cert.pub 2>/dev/null | grep Valid"
```

**Renew certificate:**

IMPORTANT: The renewal script requires interactive input. Tell the user to run it themselves. Always give PowerShell-compatible commands.

Option A — From PowerShell via Git Bash (recommended, saves directly to Windows path):
```powershell
& "C:\Program Files\Git\bin\bash.exe" -c "cd ~/repos/lrc-scripts && ./request_cert.sh -p brc"
```

Option B — From PowerShell via WSL (saves to WSL path, MUST copy to Windows after):
```powershell
wsl -e bash -c "cd ~/repos/lrc-scripts && ./request_cert.sh -p brc && cp ~/.ssh/ssh_certs/brc_cert* /mnt/c/Users/kagan/.ssh/ssh_certs/"
```

Option C — Copy from WSL to Windows (if renewed in WSL already):
```powershell
wsl -e bash -c "cp ~/.ssh/ssh_certs/brc_cert* /mnt/c/Users/kagan/.ssh/ssh_certs/"
```

If the script repo doesn't exist:
```powershell
& "C:\Program Files\Git\bin\bash.exe" -c "git clone https://github.com/lbnl-science-it/lrc-scripts.git ~/repos/lrc-scripts"
```

### 2. Standard Login (PIN + OTP)

```powershell
ssh maxkagan@hpc.brc.berkeley.edu
```

Password format: `PIN` + `OTP` concatenated without spaces (e.g., `9999123456`).

## SSH Config Setup

The Windows SSH config at `C:\Users\kagan\.ssh\config` should contain (per official BRC docs):

```ssh-config
Host savio
    LogLevel QUIET
    User maxkagan
    HostName hpc.brc.berkeley.edu
    IdentityFile ~/.ssh/ssh_certs/brc_cert
    ForwardAgent yes
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host n????.savio?
    LogLevel QUIET
    User maxkagan
    StrictHostKeyChecking no
    ProxyJump savio
    HostName %h
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Notes:
- `LogLevel QUIET` per official BRC docs
- `ServerAliveInterval`/`ServerAliveCountMax` prevent idle disconnects
- Do NOT use `ControlMaster`/`ControlPath`/`ControlPersist` — they don't work on Windows OpenSSH
- Do NOT use `RequestTTY force` — it breaks VS Code Remote-SSH

## VS Code Remote-SSH

After SSH config is set up:
1. VS Code will show `savio` as a remote host
2. For compute nodes, first find your allocated node: `squeue -u maxkagan`
3. Connect to node like `n0001.savio2` via Remote-SSH

## Running Claude Code on Savio

- Use **Git Bash** (not PowerShell) to SSH into Savio when running Claude Code
- Windows OpenSSH in PowerShell doesn't handle TUI apps properly over SSH (cursor won't move)
- `ssh -tt savio` may also help force proper TTY allocation

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Certificate expired | Re-run `./request_cert.sh -p brc` — from Git Bash for Windows use |
| VS Code asks for password | Cert is expired or was renewed in WSL only — copy to Windows path |
| Claude Code can't take input | SSH from Git Bash instead of PowerShell |
| Login fails | Verify PIN+OTP concatenation (no spaces) |
| OTP rejected | Wait for timer reset, try fresh OTP |
| Token issues | Reset at https://identity.lbl.gov/otptokens/hpccluster |

## Behavior

When invoked:
1. Check certificate status on BOTH Windows and WSL paths, show validity
2. If certs are mismatched (WSL newer than Windows), offer to copy
3. If `status`: Show certificate status only
4. If `renew`: Guide renewal — remind user to run interactively, and to copy if using WSL
5. If `config`: Show current SSH config for savio hosts
6. If no argument: Provide full connection guidance based on current state
