@echo off
chcp 65001 >nul
echo ========================================
echo  微博舆情分析系统 - 前端启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Node.js 环境...
node -v >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装，请先安装 Node.js
    pause
    exit /b 1
)
echo ✅ Node.js 版本: %node_version%

echo.
echo [2/3] 安装前端依赖...
call npm install

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 启动前端开发服务器...
echo.
echo ℹ️  前端服务将在 http://localhost:3000 启动
echo ℹ️  API 请求将代理到 http://127.0.0.1:5000
echo.
echo 按 Ctrl+C 停止服务
echo.

call npm run dev

pause
