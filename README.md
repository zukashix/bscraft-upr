# BSCraft Updater (This description and the repository itself is not complete at all)
Updater Source Code And Version Checker for BSCraft 2.0 Modpack

## For Players
Please download a release from the releases page and launch to install the modpack.

## For Devs
To modify the source code, clone this git/download as zip <br>
`$ git clone https://github.com/zukashix/bscraft-upr.git`
<br>
Install the required modules (It's recommended to use Python 3.6+)<br>
`$ python3 -m pip install -r requirements.txt`
<br>
Make required changes and build with your favorite EXE converter (PyInstaller Recommended)<br>
`$ pyinstaller --onefile --exclude-module tkinter`
