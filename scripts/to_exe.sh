pyinstaller --onefile src/__init__.py -n style-guide --additional-hooks-dir=hooks --add-data "src/data/Packages.zip;data/"