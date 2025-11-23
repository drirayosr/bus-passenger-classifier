@echo off
REM Windows batch script to compile LaTeX report

echo Compiling Bus Passenger Classification Report...
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

REM First pass
echo [1/4] Running pdflatex (first pass)...
pdflatex -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: First pdflatex pass failed!
    pause
    exit /b 1
)

REM Bibliography
echo [2/4] Running bibtex...
bibtex main
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: bibtex failed (might be normal if no citations yet)
)

REM Second pass
echo [3/4] Running pdflatex (second pass)...
pdflatex -interaction=nonstopmode main.tex

REM Third pass
echo [4/4] Running pdflatex (third pass)...
pdflatex -interaction=nonstopmode main.tex

echo.
echo Compilation complete!
echo Output file: main.pdf
echo.

REM Open PDF if compilation succeeded
if exist main.pdf (
    echo Opening PDF...
    start main.pdf
) else (
    echo ERROR: PDF file not created!
)

REM Clean up auxiliary files (optional)
echo.
set /p cleanup="Delete auxiliary files? (y/n): "
if /i "%cleanup%"=="y" (
    echo Cleaning up...
    del /q *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fls *.fdb_latexmk 2>nul
    del /q sections\*.aux 2>nul
    echo Cleanup complete!
)

echo.
pause
