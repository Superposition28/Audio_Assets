"""
This script prepares the audio source directory for processing.
It reads the source directory path from 'Audconf.ini' and organizes
subdirectories within it into 'EN' (English) and 'Global' folders
based on predefined lists, skipping specified language code directories.
"""
import sys
import os
import configparser
from pathlib import Path
import shutil # Added import

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Global variables to store config values
audio_source_dir = ""
language_blacklist = set()
global_dirs = set()

def read_config(file_path: str) -> None: # Return type changed to None
    """Reads and displays the contents of a configuration file."""
    global audio_source_dir, language_blacklist, global_dirs # Declare globals
    config = configparser.ConfigParser(allow_no_value=True)

    configPath = Path(file_path)
    print(f"Config file path: {configPath}")

    if not configPath.exists():
        print(f"Error: Configuration file not found at {configPath}", file=sys.stderr)
        sys.exit(1)

    config.read(configPath)

    print(f"Config file sections found: {config.sections()}")

    # Use .get with fallback to the initial values if not found in config
    audio_source_dir = config.get('Directories', 'AUDIO_SOURCE_DIR', fallback="")

    # Read LanguageBlacklist and GlobalDirs sections
    if 'LanguageBlacklist' in config:
        language_blacklist = set(config['LanguageBlacklist'].keys())
        print(f"Loaded Language Blacklist: {language_blacklist}")
    else:
        print("Warning: [LanguageBlacklist] section not found in config.", file=sys.stderr)
        language_blacklist = set() # Default to empty set

    if 'GlobalDirs' in config:
        global_dirs = set(config['GlobalDirs'].keys())
        print(f"Loaded Global Dirs: {global_dirs}")
    else:
        print("Warning: [GlobalDirs] section not found in config.", file=sys.stderr)
        global_dirs = set() # Default to empty set


    print(f"Using Audio Source Dir: {audio_source_dir}")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def organize_source_directories():
    """Moves subdirectories in source_dir to 'EN' or 'Global' subdirectories, excluding language codes."""
    global audio_source_dir, language_blacklist, global_dirs # Use globals
    source_path = Path(audio_source_dir) # Use Path object for consistency

    # Removed hardcoded lists - now read from config

    en_dir_name = 'EN'
    en_dir_path = source_path / en_dir_name

    global_dir_name = 'Global'
    global_dir_path = source_path / global_dir_name

    # Create the 'EN' and 'Global' subdirectories if they don't exist
    os.makedirs(en_dir_path, exist_ok=True)
    os.makedirs(global_dir_path, exist_ok=True)

    print(f"Organizing directories in '{source_path}' into '{en_dir_path}' and '{global_dir_path}'...")

    for item in source_path.iterdir():
        if item.is_dir():
            # Skip the target directories themselves and language directories
            if item.name == en_dir_name or item.name == global_dir_name or item.name in language_blacklist:
                print(f"Skipping directory: '{item.name}'")
                continue

            # Check if the directory should go into 'Global'
            if item.name in global_dirs:
                target_path = global_dir_path / item.name
                print(f"Moving '{item.name}' to '{target_path}'...")
                try:
                    shutil.move(str(item), str(target_path))
                except Exception as e:
                    print(f"Error moving directory {item.name} to Global: {e}", file=sys.stderr)
            # Otherwise, move it to 'EN'
            else:
                target_path = en_dir_path / item.name
                print(f"Moving '{item.name}' to '{target_path}'...")
                try:
                    shutil.move(str(item), str(target_path))
                except Exception as e:
                    print(f"Error moving directory {item.name} to EN: {e}", file=sys.stderr)

    print("Directory organization complete.")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main(module_dir: str) -> None:
    """Main function to run the setup process."""
    # Read the config file and get the paths and rules
    read_config(os.path.join(module_dir, "Audconf.ini"))

    # Organize the source directories using config values
    organize_source_directories()

    global audio_source_dir # Access global for printing
    # Print the final paths for verification
    print(f"Final Audio Source Dir: {audio_source_dir}")
