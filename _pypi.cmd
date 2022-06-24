@echo off
REM # Updated 09:17 24/06/2022
REM # ###

echo Confirm version number updated?
pause

cd %~dp0 | exit 1

set HOME=.
set PYTHONHOME=c:\python\3.7\

rmdir /s /q .\dist

cd .\src
forfiles /P . /M *.egg-info /C "cmd /c rmdir /s /q @file"
cd ..

%PYTHONHOME%\python -m pip install --upgrade build
%PYTHONHOME%\python -m pip install --upgrade twine

%PYTHONHOME%\python -m build

echo Check build is correct before proceeding
pause

echo Uploading to testpypi
%PYTHONHOME%\python -m twine upload --verbose --repository testpypi dist/*

echo "%PYTHONHOME%\python -m pip install --upgrade --index-url https://test.pypi.org/simple/ photoshow"
echo Install from testpypi and confirm package is working
pause

echo Confirm all code submitted to GitHub with version
pause

echo Uploading to pypi
%PYTHONHOME%\python -m twine upload --verbose --repository pypi dist/*

echo "%PYTHONHOME%\python -m pip uninstall photoshow"
echo "%PYTHONHOME%\python -m pip install --upgrade photoshow"
echo Uninstall and reinstall from pypi and confirm package is working
pause

echo Completed.
pause
