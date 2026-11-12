@echo off
title M4DI~UciH4 PROXY CHECKER ELITE v4.0
chcp 65001 >nul
cd /d "%~dp0"
cls
echo =====================================================================
echo           ⚡ M4DI~UciH4 PROXY CHECKER ELITE v4.0 ⚡
echo             [ CYBER SHARINGAN MULTI-PROTOCOL SUITE ]
echo =====================================================================
echo.
echo   [1] Launch Modern Dark-Theme GUI (Tkinter)
echo   [2] Launch Interactive CLI Console
echo   [3] Auto-Scrape & Audit Public Proxies (CLI High-Speed)
echo   [4] Exit
echo.
echo =====================================================================
set /p choice="Select Option [1-4] (Default: 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto launch_gui
if "%choice%"=="2" goto launch_cli
if "%choice%"=="3" goto launch_scrape
if "%choice%"=="4" goto exit_app

:launch_gui
echo.
echo Starting M4DI~UciH4 Cyber GUI...
python gui.py
goto end

:launch_cli
echo.
python checker.py
goto end

:launch_scrape
echo.
python checker.py --scrape --scrape-limit 150 -t 50
goto end

:exit_app
exit

:end
echo.
pause
