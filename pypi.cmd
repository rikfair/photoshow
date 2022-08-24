@echo off
REM # Updated 13:56 24/08/2022
REM # ###

cd %~dp0 | exit 1

setlocal

set HOME=.
set PYTHONHOME=c:\python\3.7\
set PYTHONPATH=%HOME%\src
for %%I in (.) do set REPOS=%%~nI%%~xI

rem =============================================

%PYTHONHOME%\python -c "import %REPOS% as x; print(f'Release Version: {x.__version__}')"

echo Confirm all files are saved and closed.
pause

rem =============================================

echo Removing old distribution files

rmdir /s /q .\dist

cd .\src
forfiles /P . /M *.egg-info /C "cmd /c rmdir /s /q @file"
cd ..

rem =============================================

echo Uninstalling %REPOS%
%PYTHONHOME%\scripts\pip uninstall -y %REPOS%

rem =============================================

echo Installing required packages

%PYTHONHOME%\python -m pip install --upgrade  --no-warn-script-location pip
%PYTHONHOME%\python -m pip install --upgrade build
%PYTHONHOME%\python -m pip install --upgrade  --no-warn-script-location pylint
%PYTHONHOME%\python -m pip install --upgrade twine
%PYTHONHOME%\python -m pip install -r "%HOME%/src/requirements.txt"

rem =============================================

echo Running pylint
%PYTHONHOME%\python -m pylint "%HOME%/src"
echo Confirm pylint was successful
pause

rem =============================================

echo Building project
%PYTHONHOME%\python -m build

echo Check build is correct before proceeding
pause

rem =============================================

echo Uploading to testpypi
%PYTHONHOME%\python -m twine upload --verbose --repository testpypi dist/*
echo Confirm upload to testpypi
pause

echo Install from testpypi
%PYTHONHOME%\python -m pip install --upgrade --index-url https://test.pypi.org/simple/ %REPOS%
echo Confirm install from testpypi
pause

echo Uninstalling %REPOS%
%PYTHONHOME%\scripts\pip uninstall -y %REPOS%

rem =============================================

%PYTHONHOME%\python -c "import %REPOS% as x; print(f'Confirm all code submitted to GitHub with version: v{x.__version__}')"
pause

rem =============================================

echo Uploading to pypi
%PYTHONHOME%\python -m twine upload --verbose --repository pypi dist/*
echo Confirm upload to pypi
pause

echo Install from pypi
%PYTHONHOME%\python -m pip install --upgrade %REPOS%
echo Confirm install from pypi
pause

rem =============================================

echo Completed.
pause

endlocal
