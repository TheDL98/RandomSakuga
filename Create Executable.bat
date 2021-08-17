@echo off
python -OO -m PyInstaller RandomSakuga.py -i FILE.ico --onefile --version-file=file_version_info.txt
