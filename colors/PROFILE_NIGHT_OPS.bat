@echo off
cd /d "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\rgb.ps1" zones -Zone1 "#0066ff" -Zone2 "#0066ff" -Zone3 "#0066ff" -Zone4 "#00e5ff" -Zone1Brightness 100 -Zone2Brightness 100 -Zone3Brightness 100 -Zone4Brightness 100
