cd %~dp0

rmdir /s /q .\dist

cd .\src
forfiles /P . /M *.egg-info /C "cmd /c rmdir /s /q @file"
cd ..

c:\python\3.7\python -m pip install --upgrade build
c:\python\3.7\python -m pip install --upgrade twine

c:\python\3.7\python -m build

pause Check build is correct before proceeding
echo Username: "__token__", Password: API Key

c:\python\3.7\python -m twine upload --verbose dist/*

pause
