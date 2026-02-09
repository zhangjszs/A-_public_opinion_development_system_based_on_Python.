@echo off
chcp 65001 >nul
echo 正在停止所有服务...

taskkill /FI "WINDOWTITLE eq Backend - Flask" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend - Vite" /F >nul 2>&1

echo 所有服务已停止
pause
