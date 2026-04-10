# Argonaut ↔ Citadel-Intel SSH Setup

Two-way SSH over Tailscale between `argonaut` (this Mac) and `citadel-intel`, with a Warp launch configuration for quick session recovery after reboots.

## Machines

| Name | Tailscale IP | User | OS |
|------|-------------|------|-----|
| argonaut | 100.88.173.121 | fm-argonaut | macOS |
| citadel-intel | 100.75.182.33 | machome | macOS |

## SSH Configuration

### From argonaut → citadel-intel

```
ssh intel
# or
ssh citadel-intel
```

Config: `~/.ssh/config` — uses key `~/.ssh/id_ed25519_citadel`, keepalive every 60s, 10 retries.

### From citadel-intel → argonaut

```
ssh argonaut
```

Config on citadel-intel: `~/.ssh/config` — uses Tailscale IP 100.88.173.121, user fm-argonaut.

## Warp Launch Configuration

**File:** `~/.warp/launch_configurations/argonaut-workspace.yaml`

Opens two tabs:
- **local** (blue) — shell at `/Users/fm-argonaut`
- **citadel-intel** (green) — auto-runs `ssh intel`

### How to launch after a reboot

1. Warp opens automatically on login (already configured).
2. Press `Cmd + P` to open the Command Palette.
3. Type `Argonaut Workspace` and select it.
4. Both tabs open; the SSH session connects automatically.

### Alternative: run from menu bar

**File → Launch Configurations → Argonaut Workspace**

## Agent Permissions (YOLO Mode)

To let the Warp agent run without approval prompts:

1. `Cmd + ,` → **AI → Agents → Profiles**
2. Set all permissions to **Always allow**
3. Clear the **Command denylist**

Or press `Cmd + Shift + I` during a session for one-time auto-approve.

## Troubleshooting

### SSH connection refused
- Verify Tailscale is running: `tailscale status`
- Verify Remote Login is enabled: **System Settings → General → Sharing → Remote Login**
- Test connectivity: `ping 100.75.182.33`

### SSH hangs or drops
- Keepalive is configured (60s interval, 10 max). If still dropping, check Tailscale relay vs direct: `tailscale status` should show `direct` for citadel-intel.

### Key authentication fails
- Verify key exists: `ls -la ~/.ssh/id_ed25519_citadel`
- Verify public key is in citadel-intel's `~/.ssh/authorized_keys`:
  ```
  ssh intel "grep -c ed25519_citadel ~/.ssh/authorized_keys"
  ```

### Launch config not showing in Warp
- Verify file exists: `ls ~/.warp/launch_configurations/argonaut-workspace.yaml`
- Verify YAML is valid: `python3 -c "import yaml; yaml.safe_load(open('$HOME/.warp/launch_configurations/argonaut-workspace.yaml'))"`
