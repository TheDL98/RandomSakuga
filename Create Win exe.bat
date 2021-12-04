@echo off
python -OO -m PyInstaller random_sakuga.py -i FILE.ico --onefile --name "RandomSakuga" --version-file=file_version_info.txt
