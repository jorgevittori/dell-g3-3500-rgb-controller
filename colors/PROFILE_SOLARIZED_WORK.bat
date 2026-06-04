@echo off
cd /d "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\rgb.ps1" zones -Zone1 "#2aa198" -Zone2 "#2aa198" -Zone3 "#2aa198" -Zone4 "#268bd2" -Zone1Brightness 100 -Zone2Brightness 100 -Zone3Brightness 100 -Zone4Brightness 100
