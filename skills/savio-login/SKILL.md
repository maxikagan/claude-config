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

## Connection Methods

### 1. SSH Certificate (Recommended)

Certificates enable passwordless login for 12 hours. The setup script is at `~/repos/lrc-scripts/request_cert.sh`.

**Check certificate status:**
```bash
# Check if certificate exists and show expiry
if [ -f ~/.ssh/ssh_certs/brc_cert ]; then
    ssh-keygen -L -f ~/.ssh/ssh_certs/brc_cert 2>/dev/null | grep -E "(Valid|Type)"
else
    echo "No certificate found"
fi
```

**Renew certificate:**
```bash
cd ~/repos/lrc-scripts && ./request_cert.sh -p brc
```

If the script repo doesn't exist:
```bash
git clone https://github.com/lbnl-science-it/lrc-scripts.git ~/repos/lrc-scripts
```

### 2. Standard Login (PIN + OTP)

```bash
ssh <username>@hpc.brc.berkeley.edu
```

Password format: `PIN` + `OTP` concatenated without spaces (e.g., `9999123456`).

## SSH Config Setup

The user's `~/.ssh/config` should contain:

```ssh-config
Host savio
    User <username>
    HostName hpc.brc.berkeley.edu
    IdentityFile ~/.ssh/ssh_certs/brc_cert
    ForwardAgent yes
    IdentitiesOnly yes

# For direct compute node access (VS Code Remote-SSH)
Host n????.savio?
    User <username>
    StrictHostKeyChecking no
    ProxyJump savio
    HostName %h
```

### Windows (WSL) Users

The IdentityFile path should be:
```
IdentityFile //wsl$/Ubuntu/home/<username>/.ssh/ssh_certs/brc_cert
```

## VS Code Remote-SSH

After SSH config is set up:
1. VS Code will show `savio` as a remote host
2. For compute nodes, first find your allocated node: `squeue -u <username>`
3. Connect to node like `n0001.savio2` via Remote-SSH

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Certificate expired | Re-run `./request_cert.sh -p brc` |
| Login fails | Verify PIN+OTP concatenation (no spaces) |
| OTP rejected | Wait for timer reset, try fresh OTP |
| Token issues | Reset at https://identity.lbl.gov/otptokens/hpccluster |

## Behavior

When invoked:
1. Check if certificate exists and show validity
2. If `status`: Show certificate status only
3. If `renew`: Check if lrc-scripts exists, then guide renewal
4. If `config`: Show current SSH config for savio hosts
5. If no argument: Provide full connection guidance based on current state
