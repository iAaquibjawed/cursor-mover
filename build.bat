@echo off
REM Build script for Windows
REM Builds Windows executable

echo ============================================
echo Building Random Cursor Mover for Windows
echo ============================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

echo Building Windows executable...
echo.

pyinstaller --name="CursorMover" ^
            --windowed ^
            --onefile ^
            --clean ^
            --noconfirm ^
            cursor_mover.py

echo.
echo ============================================
echo Build complete!
echo ============================================
echo.
echo Executable: dist\CursorMover.exe
echo.
echo To run the app, double-click dist\CursorMover.exe
echo.

pause

