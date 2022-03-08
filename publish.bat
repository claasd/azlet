rmdir /s /q dist
rmdir /s /q build
rmdir /s /q azlet.egg-info
pause
python setup.py sdist bdist_wheel
pause
python -m twine upload dist/*