$ErrorActionPreference = "Stop"
$inst = Get-CimInstance -Namespace root\wmi -ClassName AWCCWmiMethodFunction

function Invoke-Awcc($name, [hashtable]$args) {
    Invoke-CimMethod -InputObject $inst -MethodName $name -Arguments $args | Out-Null
}

# GPIO 0: DFU mode. LOW keeps normal firmware mode.
# GPIO 1: NRST. LOW then HIGH resets/starts the RGB MCU.
Invoke-Awcc "FWUpdateGPIOtoggle" @{ arg2 = 0x0000 }
Start-Sleep -Milliseconds 300
Invoke-Awcc "FWUpdateGPIOtoggle" @{ arg2 = 0x0001 }
Start-Sleep -Seconds 1
Invoke-Awcc "FWUpdateGPIOtoggle" @{ arg2 = 0x0101 }
Start-Sleep -Seconds 2
pnputil /scan-devices | Out-Null
Write-Host "RGB controller wake sequence complete."
