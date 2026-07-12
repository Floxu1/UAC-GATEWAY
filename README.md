# UAC Gateway

**Language / زبان:** **English** | [فارسی](README.fa.md)

UAC Gateway is a Windows desktop tool for sharing an active VPN route or a configured local proxy source with TVs and other LAN devices that do not support VPN clients directly.

The app provides a PySide6 GUI, detects VPN/LAN interfaces, requests administrator elevation only when Windows routing changes are required, and shows the manual network settings that should be entered on the target TV or LAN device.

> This project changes Windows routing, IP forwarding and optionally NAT settings. Use it only on networks and devices you own or are authorized to manage.

---

## Features

- Share a Windows VPN connection with a TV or LAN device.
- Detect route-based VPN adapters and tunnels.
- Detect supported local proxy sources when configured.
- Automatically detect VPN and LAN adapters.
- Generate manual IP settings for the target TV/device.
- Optional WinNAT compatibility mode.
- Optional kill-switch behavior when the VPN disconnects.
- Start/stop actions through Windows UAC elevation.
- Runtime state and result files for restore/recovery.

---

## How it works

Typical flow:

1. The VPN is already connected on the Windows PC.
2. The TV or LAN device is connected to the same Wi-Fi/LAN as the PC.
3. UAC Gateway enables a routing path from the selected LAN adapter to the selected VPN/source adapter.
4. The app displays manual IP settings for the TV/device.
5. The TV/device uses the Windows PC as its gateway.

Example TV/device settings from a successful run:

```text
IP Address: 192.168.70.200
Subnet Mask: 255.255.255.0
Gateway: 192.168.70.151
DNS: 9.9.9.9
Backup DNS: 208.67.222.222
```

---

## Screenshot

Place your screenshot at `assets/uac_gateway_preview.png` and GitHub will show it here:

```md
![UAC Gateway preview](assets/uac_gateway_preview.png)
```

---

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- PowerShell available as `powershell.exe`
- Administrator permission for start/stop actions
- An active VPN adapter, route-based tunnel, or supported local proxy source
- TV/LAN device connected to the same local network as the Windows PC

Python dependency:

```text
PySide6>=6.7
```

---

## Required project files

Recommended repository layout:

```text
UAC-Gateway/
  README.md
  README.fa.md
  LICENSE
  main.py
  backend.py
  requirements.txt
  UAC Gateway.bat
  discover.ps1
  gateway.ps1
  assets/
    uac_gateway_preview.png
  data/                   # generated at runtime; do not commit
```

Important: `backend.py` expects these PowerShell helper scripts to exist in the same folder as `main.py`:

```text
discover.ps1
gateway.ps1
```

Without these files, the GUI may open, but adapter discovery and gateway start/stop operations will fail.

---

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Add the PowerShell helper scripts

Make sure these files exist next to `main.py`:

```text
discover.ps1
gateway.ps1
```

### 5. Start the app

Recommended:

```powershell
."UAC Gateway.bat"
```

Alternative:

```powershell
python main.py
```

---

## Usage

1. Connect the VPN on Windows first.
2. Open UAC Gateway.
3. Click **AUTO DETECT** if adapters are not listed.
4. In **ACTIVE VPN / TUNNEL**, select the VPN route or source adapter.
5. In **TV NETWORK / LAN**, select the LAN/Wi-Fi adapter used by the TV/device.
6. Keep **Enable WinNAT compatibility mode** enabled unless it causes issues.
7. Keep **Stop sharing automatically if VPN disconnects** enabled for safer operation.
8. Click **START GATEWAY**.
9. Accept the Windows UAC prompt.
10. Copy the TV/device settings shown by the app.
11. Enter those values in the TV/device **Manual IP / Static IP** settings. If you are not sure where to enter them, use the device-specific guide below.
12. Test internet access from the TV/device.

---

## Manual TV/device settings

After the gateway starts, the app shows the network values that must be entered on the **target TV, phone, tablet, console, or LAN device**.

Use the values exactly as shown by UAC Gateway:

- **IP Address**: the new IP address for the target device
- **Subnet Mask**: the subnet mask of your local network
- **Gateway**: the Windows PC LAN IP address shown by the app
- **DNS**: the DNS server shown by the app
- **Backup DNS**: optional secondary DNS server

Important notes:

- Enter these values on the **target device**, not on the Windows PC.
- The target device must stay connected to the same Wi-Fi/LAN as the Windows PC.
- The generated device IP must not already be used by another device on the network.
- Different devices use different names for the same setting: **Manual IP**, **Static IP**, **IP Settings**, **Configure IP**, or **Advanced network settings**.
- To undo the manual setup later, change the device back to **Automatic**, **DHCP**, or **Auto IP**.

### LG TV / LG webOS

1. Open **Settings** using the remote.
2. Go to **All Settings**.
3. Open **General** > **Network**.
4. Choose the active connection: **Wi-Fi Connection** or **Wired Connection**.
5. Open **Advanced Wi-Fi Settings**, **Edit**, or **Other Network Settings**. The exact name may differ by webOS version.
6. Turn off **Set Automatically**, **Auto IP**, or **IP Auto Setting**.
7. Enter the values from UAC Gateway:
   - **IP Address** = `IP Address`
   - **Subnet Mask** = `Subnet Mask`
   - **Gateway** = `Gateway`
   - **DNS Server** = `DNS`
8. Save the settings and reconnect if the TV asks.
9. Open an app such as YouTube, Netflix, or the TV browser and test the connection.

### Samsung Smart TV / Tizen

1. Open **Settings**.
2. Go to **General** > **Network**.
3. Open **Network Status**.
4. Select **IP Settings**.
5. Set **IP Setting** to **Enter manually**.
6. Set **DNS Setting** to **Enter manually**.
7. Enter the values from UAC Gateway:
   - **IP Address** = `IP Address`
   - **Subnet Mask** = `Subnet Mask`
   - **Gateway** = `Gateway`
   - **DNS Server** = `DNS`
8. Save and run the TV network test.

### Android TV / Google TV / Chromecast with Google TV / Mi Box

1. Open **Settings**.
2. Go to **Network & Internet**.
3. Select the Wi-Fi network that is currently connected.
4. Open **IP settings** and choose **Static**.
5. If you do not see this option, choose **Forget network**, connect again, open **Advanced options**, then set **IP settings** to **Static**.
6. Enter the values from UAC Gateway:
   - **IP address** = `IP Address`
   - **Gateway** = `Gateway`
   - **Network prefix length** = use `24` when the subnet mask is `255.255.255.0`
   - **DNS 1** = `DNS`
   - **DNS 2** = `Backup DNS`, if available
7. Save and test YouTube or a browser app.

### Amazon Fire TV / Fire TV Stick

1. Open **Settings**.
2. Go to **Network**.
3. Select your Wi-Fi network.
4. Open **Advanced** if available. On some Fire TV versions, you may need to choose **Forget This Network**, reconnect, enter the Wi-Fi password, then choose **Advanced**.
5. Choose **Static** or manual IP setup.
6. Enter the values from UAC Gateway:
   - **IP Address** = `IP Address`
   - **Gateway** = `Gateway`
   - **Network Prefix Length** = use `24` when the subnet mask is `255.255.255.0`
   - **DNS 1** = `DNS`
   - **DNS 2** = `Backup DNS`, if available
7. Save and test an app.

### Android phone or tablet

1. Open **Settings**.
2. Go to **Network & Internet** or **Connections**.
3. Open **Wi-Fi**.
4. Tap the connected Wi-Fi network, or long-press it and choose **Modify network**.
5. Open **Advanced options**.
6. Change **IP settings** from **DHCP** to **Static**.
7. Enter the values from UAC Gateway:
   - **IP address** = `IP Address`
   - **Gateway** = `Gateway`
   - **Network prefix length** = use `24` when the subnet mask is `255.255.255.0`
   - **DNS 1** = `DNS`
   - **DNS 2** = `Backup DNS`, if available
8. Save, disconnect/reconnect Wi-Fi if needed, and test the browser.

### iPhone or iPad

1. Open **Settings**.
2. Open **Wi-Fi**.
3. Tap the **ⓘ** button next to the connected Wi-Fi network.
4. Under **IPv4 Address**, tap **Configure IP**.
5. Select **Manual**.
6. Enter:
   - **IP Address** = `IP Address`
   - **Subnet Mask** = `Subnet Mask`
   - **Router** = `Gateway`
7. Go back, then tap **Configure DNS**.
8. Select **Manual**.
9. Remove old DNS servers if needed and add:
   - **DNS Server** = `DNS`
   - Add `Backup DNS` as a second server if available
10. Save and test Safari or another app.

### Windows device as the target

1. Open **Settings**.
2. Go to **Network & Internet**.
3. Open **Wi-Fi** or **Ethernet**, depending on the active connection.
4. Open the active network properties.
5. Find **IP assignment** and click **Edit**.
6. Choose **Manual** and enable **IPv4**.
7. Enter the values from UAC Gateway:
   - **IP address** = `IP Address`
   - **Subnet mask** = `Subnet Mask`
   - **Gateway** = `Gateway`
   - **Preferred DNS** = `DNS`
   - **Alternate DNS** = `Backup DNS`, if available
8. Save and test the browser.

### How to test after manual setup

After saving the manual IP settings:

1. Disconnect and reconnect Wi-Fi on the target device, or restart the device.
2. Open a browser or an app such as YouTube.
3. If the internet does not work, change the device back to **Automatic/DHCP**, reconnect, then check the troubleshooting section below.

---

## Stop and restore

Use **STOP & RESTORE** from the app.

This restores the Windows routing/forwarding settings saved before the gateway was started.

If the app was closed or crashed:

1. Open UAC Gateway again.
2. Click **STOP & RESTORE**.
3. Accept the UAC prompt.
4. If routing is still broken, reboot Windows and manually remove temporary routes/NAT rules created by `gateway.ps1`.

---

## Runtime files

The app may create runtime files such as:

```text
data/gateway-config.json
data/gateway-state.json
data/gateway-result.json
*.log
```

These files may contain local IP addresses, interface indexes, DNS settings, process IDs and runtime state. Do not commit them to a public repository.

---

## Suggested `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
*.log

# Runtime data
data/
gateway-config.json
gateway-state.json
gateway-result.json

# Local builds
build/
dist/
*.spec
```

---

## Troubleshooting

### The app opens but no adapters are detected

Check that `discover.ps1` exists next to `main.py` and can be executed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\discover.ps1
```

### Start fails immediately

Check that `gateway.ps1` exists next to `main.py` and supports the expected parameters:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\gateway.ps1 -Action start -ConfigPath .\data\gateway-config.json
```

### UAC prompt does not appear

Run the app from a normal Windows user session and check whether Windows Security, antivirus software or group policy is blocking elevation prompts.

### TV/device has no internet

Check these items:

- The PC and TV/device are on the same LAN/subnet.
- The TV/device IP address is unused by any other device.
- The TV/device gateway is set to the PC LAN IP shown by the app.
- DNS is set to the DNS value shown by the app.
- The selected source adapter and selected LAN adapter are not the same adapter.
- The VPN still works on the PC.
- Windows Firewall or third-party security software is not blocking forwarding.

### Warning: WinNAT unavailable

If the result contains a warning like:

```text
WinNAT unavailable; forwarding-only mode is active
```

Windows NAT was not enabled and the app is using forwarding-only mode. Some networks may still work, but NAT-dependent traffic may fail.

Try:

- Running stop/start again as administrator.
- Rebooting Windows.
- Checking whether another VPN, VM, container or security product owns NAT configuration.
- Testing with WinNAT compatibility mode disabled.

---

## Development

Run a syntax check:

```powershell
python -m py_compile main.py backend.py
```

Run the GUI directly:

```powershell
python main.py
```

---

## Security notes

- Start/stop actions request administrator elevation because Windows routing and forwarding settings are changed.
- Do not run unknown PowerShell scripts, EXE files or DLL files from untrusted sources.
- Do not commit runtime state files, logs or machine-specific configuration.
- Review the licenses for any third-party runtime components before publishing them.
- For public releases, code-sign binaries/scripts where possible and publish checksums.

---

## Known limitations

- Windows-only.
- Requires PowerShell helper scripts for discovery and routing actions.
- Requires manual IP configuration on the TV/device.
- Network interface indexes are machine-specific and may change after reboot or adapter changes.
- The GUI does not include advanced route diagnostics.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Third-party components, if bundled, remain under their own licenses.

---

## Disclaimer

This tool is intended for internal testing and legitimate local network administration. Use it only on networks and devices you own or are authorized to manage. The author is not responsible for network misconfiguration, data loss or misuse.
