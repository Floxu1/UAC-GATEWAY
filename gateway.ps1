param(
    [ValidateSet('start','stop')][string]$Action,
    [string]$ConfigPath = '',
    [switch]$Internal
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$DataDir = Join-Path $Root 'data'
$StatePath = Join-Path $DataDir 'gateway-state.json'
$ResultPath = Join-Path $DataDir 'gateway-result.json'
$NatName = 'UACGatewayNAT'
$FirewallRule = 'UAC Gateway LAN Forwarding'

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = [Security.Principal.WindowsPrincipal]::new($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

function Convert-PrefixToMask([int]$Prefix) {
    $bits = ('1' * $Prefix).PadRight(32, '0')
    return (0..3 | ForEach-Object { [Convert]::ToInt32($bits.Substring($_ * 8, 8), 2) }) -join '.'
}

function Get-NetworkPrefix([string]$Ip, [int]$Prefix) {
    $bytes = [System.Net.IPAddress]::Parse($Ip).GetAddressBytes()
    $remaining = $Prefix
    for ($i = 0; $i -lt 4; $i++) {
        $take = [Math]::Min([Math]::Max($remaining, 0), 8)
        $mask = if ($take -eq 0) { 0 } else { (256 - [Math]::Pow(2, 8 - $take)) }
        $bytes[$i] = $bytes[$i] -band [int]$mask
        $remaining -= 8
    }
    return ([System.Net.IPAddress]::new($bytes)).ToString() + "/$Prefix"
}

function Write-Result([bool]$Ok, [string]$Message, $Extra = $null) {
    $result = [ordered]@{ ok = $Ok; message = $Message; at = (Get-Date).ToString('o') }
    if ($Extra) { foreach ($p in $Extra.PSObject.Properties) { $result[$p.Name] = $p.Value } }
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ResultPath -Encoding ASCII
}

function Restore-Gateway($state) {
    Get-NetFirewallRule -DisplayName $FirewallRule -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    Get-NetNat -Name $NatName -ErrorAction SilentlyContinue | Remove-NetNat -Confirm:$false
    if ($state) {
        if ($state.created_tun) {
            Remove-NetRoute -DestinationPrefix '0.0.0.0/1','128.0.0.0/1' -InterfaceAlias $state.tun_alias -Confirm:$false -ErrorAction SilentlyContinue
            foreach ($ip in @($state.bypass_ips)) {
                Remove-NetRoute -DestinationPrefix "$ip/32" -Confirm:$false -ErrorAction SilentlyContinue
            }
            if ($state.tun_pid) { Stop-Process -Id ([int]$state.tun_pid) -Force -ErrorAction SilentlyContinue }
            foreach ($route in @($state.previous_split_routes)) {
                if ($route -and $route.DestinationPrefix -and $route.InterfaceIndex) {
                    New-NetRoute -DestinationPrefix $route.DestinationPrefix -InterfaceIndex ([int]$route.InterfaceIndex) `
                        -NextHop $route.NextHop -RouteMetric ([int]$route.RouteMetric) -PolicyStore ActiveStore -ErrorAction SilentlyContinue | Out-Null
                }
            }
        }
        Set-NetIPInterface -InterfaceIndex ([int]$state.lan_index) -AddressFamily IPv4 `
            -Forwarding $state.old_lan_forwarding -WeakHostSend $state.old_lan_weak_send `
            -WeakHostReceive $state.old_lan_weak_receive -ErrorAction SilentlyContinue
        if ($state.vpn_index) {
            Set-NetIPInterface -InterfaceIndex ([int]$state.vpn_index) -AddressFamily IPv4 `
                -Forwarding $state.old_vpn_forwarding -WeakHostSend $state.old_vpn_weak_send `
                -WeakHostReceive $state.old_vpn_weak_receive -ErrorAction SilentlyContinue
        }
        Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' `
            -Name IPEnableRouter -Type DWord -Value ([int]$state.old_ip_router) -ErrorAction SilentlyContinue
        if ($state.watchdog_pid -and [int]$state.watchdog_pid -ne $PID) {
            Stop-Process -Id ([int]$state.watchdog_pid) -Force -ErrorAction SilentlyContinue
        }
    }
    Remove-Item -LiteralPath $StatePath -Force -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
if (-not (Test-Admin) -and -not $Internal) {
    $params = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action $Action"
    if ($ConfigPath) { $params += " -ConfigPath `"$ConfigPath`"" }
    $code = [Diagnostics.Process]::Start((New-Object Diagnostics.ProcessStartInfo -Property @{
        FileName='powershell.exe'; Arguments=$params; Verb='runas'; UseShellExecute=$true
    }))
    exit
}

try {
    if ($Action -eq 'stop') {
        $state = if (Test-Path $StatePath) { Get-Content $StatePath -Raw | ConvertFrom-Json } else { $null }
        Restore-Gateway $state
        Write-Result $true 'Gateway stopped and Windows settings were restored.'
        exit
    }

    if (-not (Test-Path $ConfigPath)) { throw 'Gateway configuration file was not found.' }
    if (Test-Path $StatePath) { throw 'Gateway is already active. Stop it before starting again.' }
    $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    $sourceMode = if ($config.mode) { [string]$config.mode } else { 'adapter' }
    $lanIndex = [int]$config.lan_index
    $vpnIndex = if ($config.vpn_index) { [int]$config.vpn_index } else { 0 }
    if ($sourceMode -eq 'adapter' -and $lanIndex -eq $vpnIndex) { throw 'LAN and VPN adapters must be different.' }

    $lan = Get-NetIPInterface -InterfaceIndex $lanIndex -AddressFamily IPv4 -ErrorAction Stop
    $lanIp = Get-NetIPAddress -InterfaceIndex $lanIndex -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.IPAddress -notlike '169.254.*' } | Select-Object -First 1
    if (-not $lanIp) { throw 'Selected LAN adapter has no usable IPv4 address.' }

    $createdTun = $false
    $tunPid = 0
    $tunAlias = 'UACGatewayTun'
    $bypassIps = @()
    $previousSplitRoutes = @()
    $proxyOwnerPid = 0
    $originalRoute = Get-NetRoute -InterfaceIndex $lanIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue |
        Where-Object { $_.NextHop -and $_.NextHop -ne '0.0.0.0' } | Sort-Object RouteMetric | Select-Object -First 1
    if (-not $originalRoute) { throw 'The LAN adapter has no default gateway.' }

    if ($sourceMode -eq 'proxy') {
        $proxyHost = [string]$config.proxy_host; $proxyPort = [int]$config.proxy_port
        $listener = Get-NetTCPConnection -LocalAddress $proxyHost -LocalPort $proxyPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $listener) { throw "SOCKS5 proxy is not listening on ${proxyHost}:${proxyPort}." }
        $proxyOwnerPid = [int]$listener.OwningProcess
        $knownNames = @('xray','v2ray','v2rayN','sing-box','mihomo','clash','hysteria','tuic','naive','nekobox','hiddify','python')
        $knownPids = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $knownNames -contains $_.ProcessName } | Select-Object -ExpandProperty Id)
        $knownPids += $proxyOwnerPid
        $bypassIps = @(Get-NetTCPConnection -ErrorAction SilentlyContinue |
            Where-Object { $_.OwningProcess -in $knownPids -and $_.RemoteAddress -match '^\d+\.\d+\.\d+\.\d+$' -and $_.RemoteAddress -notlike '127.*' } |
            Select-Object -ExpandProperty RemoteAddress -Unique)
        foreach ($ip in $bypassIps) {
            Remove-NetRoute -DestinationPrefix "$ip/32" -Confirm:$false -ErrorAction SilentlyContinue
            New-NetRoute -DestinationPrefix "$ip/32" -InterfaceIndex $lanIndex -NextHop $originalRoute.NextHop -RouteMetric 1 -PolicyStore ActiveStore | Out-Null
        }

        $bin = Join-Path $Root 'bin'; $tun2socks = Join-Path $bin 'tun2socks.exe'
        if (-not (Test-Path $tun2socks) -or -not (Test-Path (Join-Path $bin 'wintun.dll'))) { throw 'Bundled tun2socks/Wintun files are missing.' }
        Get-Process tun2socks -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$Root*" } | Stop-Process -Force -ErrorAction SilentlyContinue
        $process = Start-Process $tun2socks -WorkingDirectory $bin -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $DataDir 'tun2socks.out.log') -RedirectStandardError (Join-Path $DataDir 'tun2socks.err.log') `
            -ArgumentList @('-device',"tun://$tunAlias",'-proxy',"socks5://${proxyHost}:${proxyPort}",'-mtu','1420','-udp-timeout','20s','-loglevel','info')
        $tunPid = $process.Id
        $tunAdapter = $null
        for ($i=0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 400; $tunAdapter = Get-NetAdapter -Name $tunAlias -ErrorAction SilentlyContinue; if ($tunAdapter) { break } }
        if (-not $tunAdapter) { throw "TUN adapter $tunAlias was not created." }
        netsh interface ipv4 set address name="$tunAlias" source=static addr=10.97.0.1 mask=255.255.255.0 | Out-Null
        Set-NetIPInterface -InterfaceAlias $tunAlias -AddressFamily IPv4 -InterfaceMetric 1
        $vpnIndex = [int]$tunAdapter.ifIndex
        $createdTun = $true
        $previousSplitRoutes = @(Get-NetRoute -DestinationPrefix '0.0.0.0/1','128.0.0.0/1' -ErrorAction SilentlyContinue |
            Select-Object DestinationPrefix,@{n='InterfaceIndex';e={$_.ifIndex}},NextHop,RouteMetric)
        Remove-NetRoute -DestinationPrefix '0.0.0.0/1','128.0.0.0/1' -Confirm:$false -ErrorAction SilentlyContinue
        New-NetRoute -DestinationPrefix '0.0.0.0/1' -InterfaceAlias $tunAlias -NextHop '0.0.0.0' -RouteMetric 1 -PolicyStore ActiveStore | Out-Null
        New-NetRoute -DestinationPrefix '128.0.0.0/1' -InterfaceAlias $tunAlias -NextHop '0.0.0.0' -RouteMetric 1 -PolicyStore ActiveStore | Out-Null
    } else {
        $vpnRoutes = @(Get-NetRoute -InterfaceIndex $vpnIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object { $_.DestinationPrefix -in @('0.0.0.0/0','0.0.0.0/1','128.0.0.0/1') })
        if ($vpnRoutes.Count -eq 0) { throw 'Selected VPN has no full-tunnel route. Connect it first.' }
    }
    $vpn = Get-NetIPInterface -InterfaceIndex $vpnIndex -AddressFamily IPv4 -ErrorAction Stop

    $oldRouter = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' `
        -Name IPEnableRouter -ErrorAction SilentlyContinue).IPEnableRouter
    $prefix = [int]$lanIp.PrefixLength
    $networkPrefix = Get-NetworkPrefix $lanIp.IPAddress $prefix
    $parts = $lanIp.IPAddress -split '\.'
    $tvIp = "$($parts[0]).$($parts[1]).$($parts[2]).200"
    $warnings = @()

    $state = [ordered]@{
        lan_index = $lanIndex; lan_alias = [string]$lan.InterfaceAlias; lan_ip = [string]$lanIp.IPAddress
        source_mode = $sourceMode; vpn_index = $vpnIndex; vpn_alias = [string]$vpn.InterfaceAlias
        proxy_host = if ($sourceMode -eq 'proxy') { [string]$config.proxy_host } else { '' }
        proxy_port = if ($sourceMode -eq 'proxy') { [int]$config.proxy_port } else { 0 }
        proxy_owner_pid = $proxyOwnerPid; created_tun = $createdTun; tun_alias = $tunAlias; tun_pid = $tunPid
        bypass_ips = @($bypassIps); previous_split_routes = @($previousSplitRoutes)
        original_gateway = [string]$originalRoute.NextHop; original_interface_index = $lanIndex
        prefix = $prefix; subnet_mask = Convert-PrefixToMask $prefix; network_prefix = $networkPrefix
        tv_ip = $tvIp; dns1 = '9.9.9.9'; dns2 = '208.67.222.222'
        old_lan_forwarding = [string]$lan.Forwarding; old_lan_weak_send = [string]$lan.WeakHostSend
        old_lan_weak_receive = [string]$lan.WeakHostReceive
        old_vpn_forwarding = [string]$vpn.Forwarding; old_vpn_weak_send = [string]$vpn.WeakHostSend
        old_vpn_weak_receive = [string]$vpn.WeakHostReceive
        old_ip_router = if ($null -eq $oldRouter) { 0 } else { [int]$oldRouter }
        nat_enabled = $false; kill_switch = [bool]$config.kill_switch; warnings = @(); started_at = (Get-Date).ToString('o')
    }
    # Persist recovery information before changing forwarding/NAT settings.
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatePath -Encoding ASCII

    Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name IPEnableRouter -Type DWord -Value 1
    Set-NetIPInterface -InterfaceIndex $lanIndex -AddressFamily IPv4 -Forwarding Enabled -WeakHostSend Enabled -WeakHostReceive Enabled
    Set-NetIPInterface -InterfaceIndex $vpnIndex -AddressFamily IPv4 -Forwarding Enabled -WeakHostSend Enabled -WeakHostReceive Enabled
    Get-NetFirewallRule -DisplayName $FirewallRule -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -DisplayName $FirewallRule -Direction Inbound -Action Allow -Profile Any `
        -InterfaceAlias $lan.InterfaceAlias -RemoteAddress LocalSubnet | Out-Null

    if ([bool]$config.use_nat) {
        try {
            Get-NetNat -Name $NatName -ErrorAction SilentlyContinue | Remove-NetNat -Confirm:$false
            New-NetNat -Name $NatName -InternalIPInterfaceAddressPrefix $networkPrefix | Out-Null
            $state.nat_enabled = $true
        } catch {
            $warnings += "WinNAT unavailable; forwarding-only mode is active: $($_.Exception.Message)"
        }
    }
    $state.warnings = @($warnings)
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatePath -Encoding ASCII

    if ([bool]$config.kill_switch) {
        $watchdog = Join-Path $Root 'watchdog.ps1'
        $p = Start-Process powershell.exe -WindowStyle Hidden -PassThru -ArgumentList @(
            '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$watchdog`"",'-StatePath',"`"$StatePath`"",'-GatewayScript',"`"$PSCommandPath`""
        )
        $state.watchdog_pid = $p.Id
        $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatePath -Encoding ASCII
    }
    Write-Result $true 'Gateway started.' ([pscustomobject]$state)
} catch {
    $state = if (Test-Path $StatePath) { Get-Content $StatePath -Raw | ConvertFrom-Json } else { $null }
    Restore-Gateway $state
    Write-Result $false $_.Exception.Message
    exit 1
}
