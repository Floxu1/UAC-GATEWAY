param([string]$StatePath, [string]$GatewayScript)
$ErrorActionPreference = 'SilentlyContinue'

while (Test-Path $StatePath) {
    $state = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
    $healthy = $true
    if ($state.source_mode -eq 'proxy') {
        $listener = Get-NetTCPConnection -LocalAddress $state.proxy_host -LocalPort ([int]$state.proxy_port) -State Listen -ErrorAction SilentlyContinue
        $tunProcess = Get-Process -Id ([int]$state.tun_pid) -ErrorAction SilentlyContinue
        $healthy = [bool]$listener -and [bool]$tunProcess
        if ($healthy) {
            $knownNames = @('xray','v2ray','v2rayN','sing-box','mihomo','clash','hysteria','tuic','naive','nekobox','hiddify','python')
            $knownPids = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $knownNames -contains $_.ProcessName } | Select-Object -ExpandProperty Id)
            $knownPids += [int]$state.proxy_owner_pid
            $remoteIps = @(Get-NetTCPConnection -ErrorAction SilentlyContinue |
                Where-Object { $_.OwningProcess -in $knownPids -and $_.RemoteAddress -match '^\d+\.\d+\.\d+\.\d+$' -and $_.RemoteAddress -notlike '127.*' } |
                Select-Object -ExpandProperty RemoteAddress -Unique)
            foreach ($ip in $remoteIps) {
                if ($ip -notin @($state.bypass_ips)) {
                    New-NetRoute -DestinationPrefix "$ip/32" -InterfaceIndex ([int]$state.original_interface_index) `
                        -NextHop $state.original_gateway -RouteMetric 1 -PolicyStore ActiveStore -ErrorAction SilentlyContinue | Out-Null
                    $state.bypass_ips += $ip
                }
            }
            $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatePath -Encoding ASCII
        }
    } else {
        $adapter = Get-NetAdapter -InterfaceIndex ([int]$state.vpn_index) -ErrorAction SilentlyContinue
        $routes = @(Get-NetRoute -InterfaceIndex ([int]$state.vpn_index) -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object { $_.DestinationPrefix -in @('0.0.0.0/0','0.0.0.0/1','128.0.0.0/1') })
        $healthy = [bool]$adapter -and $adapter.Status -eq 'Up' -and $routes.Count -gt 0
    }
    if (-not $healthy) {
        & $GatewayScript -Action stop -Internal
        break
    }
    Start-Sleep -Seconds 3
}
