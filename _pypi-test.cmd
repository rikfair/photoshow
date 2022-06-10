cd %~dp0

c:\python\3.7\python -m pip install --upgrade build
c:\python\3.7\python -m build

c:\python\3.7\python -m pip install --upgrade twine
echo Username: "__token__", Password: API Key
c:\python\3.7\python -m twine upload --verbose --repository testpypi dist/*

pause
