@echo off
cd /d "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\rgb.ps1" zones -Zone1 "#bd00ff" -Zone2 "#bd00ff" -Zone3 "#bd00ff" -Zone4 "#b6ff00" -Zone1Brightness 100 -Zone2Brightness 100 -Zone3Brightness 100 -Zone4Brightness 100
