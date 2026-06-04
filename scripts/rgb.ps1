param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("on","off","color","zones","status")]
    [string]$Command,

    [string]$Value = "#ffffff",

    [int]$Brightness = 100,

    [string]$Zone1 = "#ffffff",
    [string]$Zone2 = "#ffffff",
    [string]$Zone3 = "#ffffff",
    [string]$Zone4 = "#ffffff",

    [int]$Zone1Brightness = 100,
    [int]$Zone2Brightness = 100,
    [int]$Zone3Brightness = 100,
    [int]$Zone4Brightness = 100
)

$Script = Join-Path $PSScriptRoot "..\src\core\dell_g3_rgb.py"
$BundledPython = Join-Path $PSScriptRoot "..\runtime\python\python.exe"

if (Test-Path -LiteralPath $BundledPython) {
    $Python = $BundledPython
    $PythonArgs = @()
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $Python = "py"
    $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $Python = "python"
    $PythonArgs = @()
} else {
    Write-Error "Python was not found. Install Python, add it to PATH, or place an embedded Python at runtime\python\python.exe."
    exit 1
}

if ($Command -eq "color") {
    & $Python @PythonArgs $Script color $Value --brightness $Brightness
} elseif ($Command -eq "on") {
    & $Python @PythonArgs $Script on --brightness $Brightness
} elseif ($Command -eq "off") {
    & $Python @PythonArgs $Script off
} elseif ($Command -eq "zones") {
    & $Python @PythonArgs $Script zones --zone1 $Zone1 --zone2 $Zone2 --zone3 $Zone3 --zone4 $Zone4 --zone1-brightness $Zone1Brightness --zone2-brightness $Zone2Brightness --zone3-brightness $Zone3Brightness --zone4-brightness $Zone4Brightness
} else {
    & $Python @PythonArgs $Script status
}
