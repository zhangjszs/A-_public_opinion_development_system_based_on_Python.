@echo off
chcp 65001 >nul
echo ================================
echo   微博舆情分析系统 - 一键启动
echo ================================
echo.

echo [1/2] 启动后端服务器 (端口 5000)...
start "Backend - Flask" cmd /k "cd /d %~dp0 && python run.py"

echo [2/2] 启动前端服务器 (端口 3000)...
timeout /t 3 /nobreak >nul
start "Frontend - Vite" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================
echo   启动完成！
echo   后端: http://127.0.0.1:5000
echo   前端: http://localhost:3000
echo ================================
echo.
echo 按任意键退出此窗口...
pause >nul
