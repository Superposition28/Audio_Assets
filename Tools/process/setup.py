import sys
import os
import configparser
from pathlib import Path
import shutil # Added import

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def read_config(file_path: str) -> str:
    """Reads and displays the contents of a configuration file."""
    config = configparser.ConfigParser()

    # Construct the absolute path to the config file relative to this script's location
    script_dir = Path(__file__).resolve().parent
    configPath = script_dir / ".." / ".." / file_path # Go up two levels from process/
    print(f"Config file path: {configPath}")

    if not configPath.exists():
        print(f"Error: Configuration file not found at {configPath}", file=sys.stderr)
        sys.exit(1)

    config.read(configPath)

    print(f"Config file sections found: {config.sections()}")

    global audio_source_dir
    # Use .get with fallback to the initial values if not found in config
    audio_source_dir = config.get('Directories', 'AUDIO_SOURCE_DIR')

    print(f"Using Audio Source Dir: {audio_source_dir}")



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def organize_source_directories():
    """Moves subdirectories in source_dir to 'EN' or 'Global' subdirectories, excluding language codes."""
    global audio_source_dir
    source_path = Path(audio_source_dir) # Use Path object for consistency

    # Directories to be skipped entirely (language codes)
    language_blacklist = {'IT', 'ES', 'FR'}

    # Directories to be moved into the 'Global' folder
    global_dirs = {
        '80b_crow', 'amb_airc', 'amb_chao', 'amb_cour', 'amb_dung', 'amb_ext_',
        'amb_fore', 'amb_fren', 'amb_gara', 'amb_int_', 'amb_mans', 'amb_nort',
        'amb_riot', 'amb_shir', 'amb_vent', 'bin_rev0', 'brt_dino', 'brt_dior',
        'brt_myst', 'brt_plan', 'brt_temp', 'bsh_air_', 'bsh_beac', 'bsh_figh',
        'bsh_fire', 'bsh_ice_', 'bsh_vill', 'bsh__air', 'che_cart', 'che_cent',
        'che_mark', 'che_mo_b', 'che_q_an', 'dod_aqua', 'dod_dock', 'gamehub_',
        'gts_full', 'gts_seas', 'gts_stat', 'gts_subu', 'gts_vent', 'gts_viol',
        'mtp_heav', 'mus_simp', 'sss_cont', 'sss_lab_', 'sss_mall'
    }

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

def main() -> None:
    """Main function to run the setup process."""
    # Read the config file and get the paths
    read_config("Audconf.ini")

    # Organize the source directories
    organize_source_directories()

    global audio_source_dir
    # Print the final paths for verification
    print(f"Final Audio Source Dir: {audio_source_dir}")
