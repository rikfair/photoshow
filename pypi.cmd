@echo off
REM # Updated 16:54 24/08/2022
REM # ###

cd %~dp0 | exit 1

setlocal

set PYTHONHOME=c:\python\3.7\

set HOME=%cd%
set PYTHONPATH_ORIG=%PYTHONPATH%
set PYTHONPATH_THIS=%HOME%\src 
for %%I in (.) do set REPOS=%%~nI%%~xI
echo Processing Repos: %REPOS%

rem =============================================

echo Uninstalling %REPOS%

set PYTHONPATH=%PYTHONPATH_ORIG%
"%PYTHONHOME%\python" -m pip uninstall -y %REPOS%

rem =============================================

set PYTHONPATH=%PYTHONPATH_THIS%
"%PYTHONHOME%\python" -c "import %REPOS% as x; print(f'Release Version: {x.__version__}')"
echo Confirm all files are saved and closed.
pause

rem =============================================

echo Removing old distribution files

rmdir /s /q .\dist

cd .\src | exit 2
forfiles /P . /M *.egg-info /C "cmd /c rmdir /s /q @file"
cd ..

rem =============================================

echo Installing required packages

set PYTHONPATH=%PYTHONPATH_ORIG%
"%PYTHONHOME%\python" -m pip install --upgrade  --no-warn-script-location pip
"%PYTHONHOME%\python" -m pip install --upgrade build
"%PYTHONHOME%\python" -m pip install --upgrade  --no-warn-script-location pylint
"%PYTHONHOME%\python" -m pip install --upgrade twine
"%PYTHONHOME%\python" -m pip install -r "%HOME%/requirements.txt"

rem =============================================

echo Running pylint

set PYTHONPATH=%PYTHONPATH_THIS%
"%PYTHONHOME%\python" -m pylint "%HOME%/src/%REPOS%"
echo Confirm pylint was successful
pause

rem =============================================

echo Building project

cd "%HOME%"
set PYTHONPATH=%PYTHONPATH_THIS%
"%PYTHONHOME%\python" -m build

echo Check build is correct before proceeding
pause

rem =============================================

echo Creating sphinx documentation

cd "%HOME%\docs"
%PYTHONHOME%\Scripts\sphinx-build.exe -a -b html . _build

echo Confirm sphinx documentation build was successful
pause

rem =============================================

echo Uploading to testpypi
cd "%HOME%"
%PYTHONHOME%\python -m twine upload --verbose --repository testpypi dist/*
echo Confirm upload to testpypi
pause

echo Install from testpypi
set PYTHONPATH=%PYTHONPATH_ORIG%
"%PYTHONHOME%\python" -m pip install --upgrade --index-url https://test.pypi.org/simple/ %REPOS%
echo Confirm install from testpypi
pause

echo Uninstalling %REPOS%
"%PYTHONHOME%\python" -m pip uninstall -y %REPOS%

rem =============================================

set PYTHONPATH=%PYTHONPATH_THIS%
"%PYTHONHOME%\python" -c "import %REPOS% as x; print(f'Confirm all code submitted to GitHub with version: v{x.__version__}')"
pause

rem =============================================

echo Uploading to pypi
%PYTHONHOME%\python -m twine upload --verbose --repository pypi dist/*
echo Confirm upload to pypi
pause

echo Install from pypi
set PYTHONPATH=%PYTHONPATH_ORIG%
"%PYTHONHOME%\python" -m pip install --upgrade %REPOS%
echo Confirm install from pypi
pause

rem =============================================

echo Completed.
pause

endlocal
