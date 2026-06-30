@echo off
chcp 65001 >nul
title 股票数据导入工具

echo ==========================================
echo   正在启动股票数据导入流程...
echo ==========================================
echo.

REM 设置 Python 解释器和脚本路径
set PYTHON_EXE=D:\03-code\pycharm\stock\flaskJuanwang_es\venv\Scripts\python.exe
set SCRIPT_PATH=D:\03-code\pycharm\stock\flaskJuanwang_es\tool\run_all_tool.py

REM 检查 Python 是否存在
if not exist "%PYTHON_EXE%" (
    echo [错误] 找不到 Python 解释器：%PYTHON_EXE%
    echo 请检查虚拟环境路径是否正确。
    goto :end
)

REM 检查脚本是否存在
if not exist "%SCRIPT_PATH%" (
    echo [错误] 找不到运行脚本：%SCRIPT_PATH%
    goto :end
)

echo [信息] 正在执行: %SCRIPT_PATH%
echo.

REM 执行命令
"%PYTHON_EXE%" "%SCRIPT_PATH%"

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ==========================================
if %EXIT_CODE% EQU 0 (
    echo   执行成功！所有步骤已完成。
) else (
    echo   执行失败！请检查上方日志错误信息。
)
echo ==========================================

:end
REM 可选：延迟 2 秒关闭，方便看清最后一行状态（如果不需可删除下一行）
timeout /t 2 /nobreak >nul

REM 脚本结束，窗口将自动关闭
exit /b %EXIT_CODE%
