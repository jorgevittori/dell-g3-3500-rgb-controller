@echo off
cd /d "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\rgb.ps1" zones -Zone1 "#39ff14" -Zone2 "#39ff14" -Zone3 "#39ff14" -Zone4 "#00ff8a" -Zone1Brightness 100 -Zone2Brightness 100 -Zone3Brightness 100 -Zone4Brightness 100
