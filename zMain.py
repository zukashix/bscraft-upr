# BSCraft 2.0 Updater (modified version of zukashix-modpack-loader)
# Author(s): zukashix, BraxtonElmer

import requests
import os
import json
import subprocess
import zipfile
import shutil
from sys import argv

DATA_DICT = {
    "new_install": True,
    "current_mp_version": 0,
    "launcher": None
}

LNCHER = None
APPDATA = os.getenv('APPDATA')

def write_json(new_data, filename):
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside profiles
        file_data["profiles"]["BSCraft 2.0"] = new_data
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def downloadFile(file_url):
    r = requests.get(file_url, stream = True)
  
    with open(APPDATA + "\\zukashix.mpu\\patch.zip","wb") as ufile:
        for chunk in r.iter_content(chunk_size=1024):
  
           # Writing one chunk at a time to file (No excessive memory usage on large-size files)
            if chunk:
                ufile.write(chunk)

def checkForUpdate():
    def install():
        # Extract the ZIP
        with zipfile.ZipFile(APPDATA + "\\zukashix.mpu\\patch.zip","r") as zipf:
            zipf.extractall(APPDATA + "\\zukashix.mpu\\")

        # Run Installer BAT
        subprocess.call([APPDATA + "\\zukashix.mpu\\client\\patcher.bat"])

        # Change local data version integer
        new_version = json.load(open(APPDATA + '\\zukashix.mpu\\client\\thisversion.json', 'r'))
        global DATA_DICT
        DATA_DICT = {
            "new_install": False,
            "current_mp_version": new_version['new_version'],
            "launcher": LNCHER
        }

        # Save new data
        json.dump(DATA_DICT, open(APPDATA + '\\zukashix.mpu\\local_data.json', 'w'))

        # Cleanup
        shutil.rmtree(APPDATA + "\\zukashix.mpu\\client\\")
        os.remove(APPDATA + '\\zukashix.mpu\\patch.zip')

        # Create profile if using SKL
        if LNCHER == 'skl':
            profile_data = {
                "name": "BSCraft 2.0",
                "gameDir": APPDATA + "\\.minecraft\\profiles\\BSCraft-2",
                "lastVersionId": "1.16.5-forge-36.2.0",
                "resolution": {
                    "width": 854,
                    "height": 480,
                    "fullscreen": False
                },
                "launcherVisibilityOnGameClose": "hide launcher and re-open when game closes",
                "memoryMax": 3144
            }

            write_json(profile_data, APPDATA + '\\.minecraft\\launcher_profiles.json')

    # Fetch version data from repo
    data = requests.get("https://raw.githubusercontent.com/zukashix/bscraft-upr/main/repo/version_data.json").json()

    # If modpack is not installed download Base Modpack
    if DATA_DICT['new_install'] == True:
        # Download by launcher
        if LNCHER == 'skl':
            downloadFile(data['new_install_url'])
        elif LNCHER == 'tl':
            downloadFile(data['new_install_url_tl'])
        # Install
        install()
    
    if DATA_DICT['new_install'] == False:
        # Check for updates by matching integer
        # Latest version
        if DATA_DICT['current_mp_version'] == data['latest_version']:
            print('You\'re up to date!')
        
        # Higher than stable
        elif DATA_DICT['current_mp_version'] > data['latest_version']:
            print('You\'re running an unstable release of BSCraft.')

        # Lower than latest
        elif DATA_DICT['current_mp_version'] < data['latest_version']:
            print('Updates are available!')
            # Download patch by launcher
            if LNCHER == 'skl':
                downloadFile(data['latest_url'])
            elif LNCHER == 'tl':
                downloadFile(data['latest_url_tl'])
            # Install Patch
            install()
        

def firstRun():
    if '--reset' or '-r' in argv:
        shutil.rmtree(APPDATA + '\\zukashix.mpu\\')

    try:
        # Load version data file
        local_data = json.load(open(APPDATA + '\\zukashix.mpu\\local_data.json', 'r'))

        # Update file in memory
        global DATA_DICT
        DATA_DICT = local_data

        # Check for updates
        checkForUpdate()

    except FileNotFoundError:
        # Create Application WorkDIR
        os.mkdir(APPDATA + '\\zukashix.mpu')

        # Ask for launcher and save the data
        launcher = None
        while launcher != 'skl' or 'tl':
            launcher = str(input("What launcher do you use? (Type \"tl\" for TLauncher or \"skl\" for any other launcher): "))

        global DATA_DICT, LNCHER
        DATA_DICT['launcher'] = launcher
        LNCHER = launcher
        # Save the data file locally
        json.dump(DATA_DICT, open(APPDATA + '\\zukashix.mpu\\local_data.json', 'w'))
        # Check for updates
        checkForUpdate()
