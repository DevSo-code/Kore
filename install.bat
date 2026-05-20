@echo off
:: Kore Utility Suite — Windows Setup Script
:: Checks for Python 3 and runs the visual onboarding & installation setup.

title Kore Utility Suite Setup

echo ==============================================
echo       Kore Utility Suite — Setup Launcher      
echo ==============================================

:: Check if Python is in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python is not detected in your PATH.
    echo Checking standard installation paths...
    
    :: Check standard Windows AppData folder
    if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe" (
        set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe"
    ) else (
        echo [INFO] Python is not found. Downloading Python 3.11.8 installer...
        
        :: Download python using curl (built-in in Win10+)
        curl -L "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -o "%TEMP%\python_installer.exe"
        
        echo [INFO] Installing Python 3.11.8. Please wait...
        :: Install for current user without UAC prompt, prepend to PATH
        "%TEMP%\python_installer.exe" /quiet PrependPath=1 Include_test=0 Include_pip=1
        
        echo [INFO] Python installation complete. Cleaning up...
        del "%TEMP%\python_installer.exe"
        
        :: Attempt to find the newly installed python
        if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
            set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
        ) else (
            echo [ERROR] Python was installed but could not be located in standard paths.
            echo Please restart your terminal/PC and run install.bat again.
            pause
            exit /b 1
        )
    )
) else (
    set "PYTHON_EXE=python"
)

:: Run the visual onboarding setup
echo [SUCCESS] Starting visual setup tool...
"%PYTHON_EXE%" setup_gui.py

if %errorlevel% neq 0 (
    echo [ERROR] The installer exited with an error code.
    pause
    exit /b %errorlevel%
)
