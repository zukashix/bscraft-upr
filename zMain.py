# BSCraft 3.0 Updater (modified version of zukashix-modpack-loader)
# Author(s): zukashix, BraxtonElmer

import subprocess
import requests
import os
import json
import zipfile
import shutil
import sys
import time
import psutil
from clint.textui import progress

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
        file_data["profiles"]["BSCraft 3"] = new_data
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def downloadFile(file_url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    r = requests.get(file_url, stream = True, headers=headers, verify=False)
    print('# fetch {}'.format(file_url))
    with open(APPDATA + "\\zukashix.mpu\\patch.zip","wb") as ufile:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
  
           # Writing one chunk at a time to file (No excessive memory usage on large-size files)
            if chunk:
                ufile.write(chunk)
                ufile.flush()
    

def checkForUpdate():
    print('Checking for updates...')
    def install():
        # Extract the ZIP
        print('Extracting...')
        with zipfile.ZipFile(APPDATA + "\\zukashix.mpu\\patch.zip","r") as zipf:
            zipf.extractall(APPDATA + "\\zukashix.mpu\\")

        # Run Installer BAT
        print('Installing...')
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
        
        print('Cleaning Up...')
        # Cleanup
        shutil.rmtree(APPDATA + "\\zukashix.mpu\\client\\")
        os.remove(APPDATA + '\\zukashix.mpu\\patch.zip')

        # Create profile if using SKL
        if LNCHER == 'skl':
            print('Creating profile...')
            user_ram = round(psutil.virtual_memory().total/1000000000, 2)
            if user_ram < 5:
                alloc_ram= 3144
            elif user_ram < 9:
                alloc_ram= 5100
            elif user_ram < 17:
                alloc_ram= 9000
            else:
                alloc_ram = input("Enter allocated ram in MB to run BSCraft 2: ")
            profile_data = {
                "name": "BSCraft 3",
                "gameDir": APPDATA + "\\.minecraft\\profiles\\BSCraft-2",
                "lastVersionId": "1.16.5-forge-36.2.0",
                "resolution": {
                    "width": 854,
                    "height": 480,
                    "fullscreen": False
                },
                "launcherVisibilityOnGameClose": "hide launcher and re-open when game closes",
                "memoryMax": alloc_ram
            }

            write_json(profile_data, APPDATA + '\\.minecraft\\launcher_profiles.json')

    # Fetch version data from repo
    data = requests.get("https://raw.githubusercontent.com/zukashix/bscraft-upr/main/repo/version_data.json").json()

    # If modpack is not installed download Base Modpack
    if DATA_DICT['new_install'] == True:
        print('Downloading Modpack...')
        # Download by launcher
        if LNCHER == 'skl':
            downloadFile(data['new_install_url'])
        if LNCHER == 'tl':
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
            print('Updates are available! Downloading...')
            # Download patch by launcher
            if LNCHER == 'skl':
                downloadFile(data['latest_url'])
            if LNCHER == 'tl':
                downloadFile(data['latest_url_tl'])
            # Install Patch
            install()
    print('Updates Installed, Program will exit in 5 seconds.')
    time.sleep(5)
    sys.exit(0)
        

def firstRun():
    print('Initializing...')
    global DATA_DICT, LNCHER

    if '--reset' in sys.argv:
        shutil.rmtree(APPDATA + '\\zukashix.mpu\\')

    try:
        # Load version data file
        local_data = json.load(open(APPDATA + '\\zukashix.mpu\\local_data.json', 'r'))

        # Update file in memory
        DATA_DICT = local_data
        LNCHER = local_data['launcher']

    except FileNotFoundError:
        # Create Application WorkDIR
        os.mkdir(APPDATA + '\\zukashix.mpu')

        # Ask for launcher and save the data
        while True:
            launcher = str(input("What launcher do you use? (Type \"tl\" for TLauncher or \"skl\" for any other launcher): "))
            if launcher == 'tl' or 'skl':
                break
            else:
                print('Incorrect Launcher Key.')
                continue

        DATA_DICT['launcher'] = launcher
        LNCHER = launcher
        # Save the data file locally
        json.dump(DATA_DICT, open(APPDATA + '\\zukashix.mpu\\local_data.json', 'w'))

    # Check for updates
    checkForUpdate()

if __name__ == '__main__':
    firstRun()
