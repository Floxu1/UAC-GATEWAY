$ErrorActionPreference = 'Stop'
$items = @()
$proxies = @()
$routeTargets = @('0.0.0.0/0', '0.0.0.0/1', '128.0.0.0/1')

foreach ($adapter in Get-NetAdapter -IncludeHidden | Where-Object { $_.Status -eq 'Up' }) {
    $ip = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -ne '127.0.0.1' } |
        Select-Object -First 1
    if (-not $ip) { continue }

    $routes = @(Get-NetRoute -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.DestinationPrefix -in $routeTargets })
    $gatewayRoute = $routes | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' -and $_.NextHop -ne '0.0.0.0' } |
        Sort-Object RouteMetric | Select-Object -First 1
    $text = "$($adapter.Name) $($adapter.InterfaceDescription)"
    $vpnHint = $text -match '(?i)vpn|tun|tap|wireguard|warp|openvpn|rout|tailscale|zerotier|outline|proton|nord|express|xray|sing-box'
    $hasVpnRoute = @($routes | Where-Object { $_.DestinationPrefix -in @('0.0.0.0/1','128.0.0.0/1') }).Count -gt 0 -or
        ($vpnHint -and @($routes | Where-Object DestinationPrefix -eq '0.0.0.0/0').Count -gt 0)
    $hardware = $adapter.HardwareInterface -eq $true

    $items += [ordered]@{
        index = [int]$adapter.ifIndex
        alias = [string]$adapter.Name
        description = [string]$adapter.InterfaceDescription
        ipv4 = [string]$ip.IPAddress
        prefix = [int]$ip.PrefixLength
        gateway = if ($gatewayRoute) { [string]$gatewayRoute.NextHop } else { '' }
        hardware = $hardware
        vpn_hint = [bool]$vpnHint
        vpn_route = [bool]$hasVpnRoute
        route_count = @($routes).Count
    }
}

function Test-Socks5([string]$HostName, [int]$Port) {
    $client = $null
    try {
        $client = [Net.Sockets.TcpClient]::new()
        $task = $client.ConnectAsync($HostName, $Port)
        if (-not $task.Wait(500)) { return $false }
        $stream = $client.GetStream(); $stream.ReadTimeout = 700; $stream.WriteTimeout = 700
        [byte[]]$hello = 5,1,0
        $stream.Write($hello,0,$hello.Length)
        [byte[]]$reply = 0,0
        $read = $stream.Read($reply,0,2)
        return $read -eq 2 -and $reply[0] -eq 5 -and $reply[1] -eq 0
    } catch { return $false } finally { if ($client) { $client.Dispose() } }
}

$internet = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction SilentlyContinue
$candidatePorts = @()
if ($internet.ProxyEnable -eq 1 -and $internet.ProxyServer) {
    $raw = [string]$internet.ProxyServer
    foreach ($entry in $raw -split ';') {
        $value = if ($entry -match '=') { ($entry -split '=',2)[1] } else { $entry }
        if ($value -match '^(?:https?://)?([^:]+):(\d+)$') {
            $candidatePorts += [int]$Matches[2]
            if ([int]$Matches[2] -gt 1) { $candidatePorts += ([int]$Matches[2] - 1) }
        }
    }
}
$candidatePorts += @(10808,1080,7890,7891)
foreach ($port in $candidatePorts | Select-Object -Unique) {
    if (-not (Test-Socks5 '127.0.0.1' $port)) { continue }
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    $owner = if ($listener) { Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue } else { $null }
    $proxies += [ordered]@{
        mode = 'proxy'; host = '127.0.0.1'; port = [int]$port
        owner_pid = if ($listener) { [int]$listener.OwningProcess } else { 0 }
        owner_name = if ($owner) { [string]$owner.ProcessName } else { 'unknown' }
        label = "SOCKS5 127.0.0.1:$port"
    }
}

@{ adapters = @($items); proxies = @($proxies) } | ConvertTo-Json -Depth 5 -Compress
