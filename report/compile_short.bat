@echo off
REM Windows batch script to compile short report

echo Compiling Short Report (5 pages)...
echo.

REM Check if pdflatex is installed
where pdflatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pdflatex not found!
    echo Please install MiKTeX or TeX Live:
    echo - MiKTeX: https://miktex.org/download
    echo - TeX Live: https://www.tug.org/texlive/
    pause
    exit /b 1
)

REM Compile (no bibliography needed for short version)
echo [1/2] Running pdflatex (first pass)...
pdflatex -interaction=nonstopmode report_short.tex
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: First pdflatex pass failed!
    pause
    exit /b 1
)

REM Second pass for references
echo [2/2] Running pdflatex (second pass)...
pdflatex -interaction=nonstopmode report_short.tex

echo.
echo Compilation complete!
echo Output file: report_short.pdf
echo.

REM Open PDF if compilation succeeded
if exist report_short.pdf (
    echo Opening PDF...
    start report_short.pdf
) else (
    echo ERROR: PDF file not created!
)

REM Clean up auxiliary files
echo.
set /p cleanup="Delete auxiliary files? (y/n): "
if /i "%cleanup%"=="y" (
    echo Cleaning up...
    del /q report_short.aux report_short.log report_short.out report_short.synctex.gz 2>nul
    echo Cleanup complete!
)

echo.
pause
