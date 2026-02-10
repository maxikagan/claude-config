# Savio HPC Setup Guide

## SSH Login Methods

### Standard Login (PIN + OTP)
```bash
ssh yourusername@hpc.brc.berkeley.edu
```

At the password prompt, concatenate your PIN and Google Authenticator OTP **without spaces**:
```
Password: PIN_hereOTP_here
```
Example: If PIN is `9999` and OTP is `123456`, enter `9999123456`.

### SSH Certificate Authentication (Recommended)

SSH certificates enable passwordless login after initial setup. Certificates expire after 12 hours.

**Setup Steps:**

1. Clone the LRC scripts repository (one-time):
```bash
git clone https://github.com/lbnl-science-it/lrc-scripts.git ~/repos/lrc-scripts
```

2. Generate a certificate (repeat when expired):
```bash
cd ~/repos/lrc-scripts
./request_cert.sh -p brc
```
When prompted, provide your Savio username, PIN, and OTP. Certificate saves to `~/.ssh/ssh_certs/brc_cert`.

3. Add to `~/.ssh/config`:
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

4. Login with: `ssh savio`

### Windows Setup (WSL)

Run the certificate script from within WSL/Ubuntu. In your **Windows** SSH config, reference the certificate as:
```ssh-config
IdentityFile //wsl$/Ubuntu/home/<username>/.ssh/ssh_certs/brc_cert
```

## VS Code Remote-SSH

After configuring SSH certificates:
1. Install "Remote - SSH" extension in VS Code
2. `savio` will appear as an available remote host
3. To connect to compute nodes, find your allocated node with `squeue -u <username>`, then connect to `n0001.savio2` (example)

## Troubleshooting

- **Login fails**: Ensure PIN and OTP are concatenated without spaces
- **OTP expired**: Wait for countdown to reset before entering new OTP
- **Wrong username**: Use your Linux account name, not SLURM account names (`fc_`, `co_`)
- **Certificate expired**: Re-run `./request_cert.sh -p brc`
- **Token issues**: Reset via [Non-LBL Token Management](https://identity.lbl.gov/otptokens/hpccluster)

---

## Claude Code Configuration Sync

Run these commands to sync your Claude Code configuration on Savio:

```bash
# 1. Create repos directory if it doesn't exist
mkdir -p ~/repos

# 2. Clone your config repo
git clone https://github.com/maxikagan/claude-config.git ~/repos/claude-config

# 3. Create .claude directory if needed
mkdir -p ~/.claude

# 4. Create symlinks
ln -sf ~/repos/claude-config/commands ~/.claude/commands
ln -sf ~/repos/claude-config/skills ~/.claude/skills
ln -sf ~/repos/claude-config/agents ~/.claude/agents
ln -sf ~/repos/claude-config/settings.json ~/.claude/settings.json

# 5. Verify setup
ls -la ~/.claude/
```

Done! Your commands (`/conda`, `/jupyter`) and skills are now available.

To update after making changes on another machine:
```bash
cd ~/repos/claude-config && git pull
```
