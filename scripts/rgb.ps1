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
$RuntimeDir = Join-Path $PSScriptRoot "..\runtime\python"
$PythonDownloadUrl = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"

function Install-LocalPython {
    Write-Host ""
    Write-Host "Python was not found." -ForegroundColor Yellow
    Write-Host "Dell G3 RGB Controller will download a local portable Python into this folder."
    Write-Host "This does not install Python globally, does not change PATH, and does not require admin."
    Write-Host ""

    $tempZip = Join-Path ([System.IO.Path]::GetTempPath()) "dell-g3-rgb-python-3.12.10-embed-amd64.zip"

    New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Write-Host "Downloading portable Python..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $PythonDownloadUrl -OutFile $tempZip -UseBasicParsing

        Write-Host "Extracting runtime..." -ForegroundColor Cyan
        Expand-Archive -LiteralPath $tempZip -DestinationPath $RuntimeDir -Force

        if (-not (Test-Path -LiteralPath $BundledPython)) {
            Write-Error "Python runtime download finished, but python.exe was not found in runtime\python."
            exit 1
        }

        Write-Host "Local Python runtime is ready." -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Error "Could not download local Python runtime. Check your internet connection and try again. Details: $($_.Exception.Message)"
        exit 1
    } finally {
        if (Test-Path -LiteralPath $tempZip) {
            Remove-Item -LiteralPath $tempZip -Force
        }
    }
}

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
    Install-LocalPython
    $Python = $BundledPython
    $PythonArgs = @()
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
