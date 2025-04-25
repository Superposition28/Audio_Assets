import os
import subprocess
import sys
import shutil
import configparser
from pathlib import Path

global audio_source_dir, audio_target_dir
# Set the source and target directories
audio_source_dir = r".\GameFiles\Main\PS3_GAME\USRDIR\Assets_1_Audio_Streams"
audio_target_dir = r".\GameFiles\Main\PS3_GAME\AudioVideo_OUTPUT\Assets_1_Audio_Streams"

# Get the full path of the source directory
audio_source_dir_full_path = os.path.abspath(audio_source_dir)

# Find all .snu files recursively
snu_files = []
for root, dirs, files in os.walk(audio_source_dir_full_path):
    for file in files:
        if file.lower().endswith(".snu"):
            snu_files.append(os.path.join(root, file))

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

    global audio_source_dir, audio_target_dir

    # Use .get with fallback to the initial values if not found in config
    audio_source_dir = config.get('Directories', 'AUDIO_SOURCE_DIR', fallback=audio_source_dir)
    audio_target_dir = config.get('Directories', 'AUDIO_TARGET_DIR', fallback=audio_target_dir)
    vgmstream = config.get('Tools', 'vgmstream-cli', fallback=None)

    if vgmstream is None:
        print("Error: 'vgmstream-cli' path not found in [Tools] section of config file.", file=sys.stderr)
        sys.exit(1)

    print(f"Using Audio Source Dir: {audio_source_dir}")
    print(f"Using Audio Target Dir: {audio_target_dir}")
    print(f"Using vgmstream-cli: {vgmstream}")

    return vgmstream


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run():
    """Contains the main logic for finding and processing audio files."""
    global audio_source_dir, audio_target_dir # Needed because read_config modifies them

    vgmstream_cli_path = read_config("Audconf.ini")

    # Output the result from the script
    print(f"vgmstream-cli path from config: {vgmstream_cli_path}")

    # Ensure vgmstream-cli path exists (using shutil.which to find in PATH or current dir)
    vgmstream_cli_full_path = shutil.which(vgmstream_cli_path)
    if not vgmstream_cli_full_path:
        # Fallback: check if it exists exactly as specified (e.g., relative to script or absolute)
        if os.path.exists(vgmstream_cli_path):
            vgmstream_cli_full_path = os.path.abspath(vgmstream_cli_path)
        else:
            # Try resolving relative to the script directory
            script_dir = Path(__file__).resolve().parent
            potential_path = script_dir / vgmstream_cli_path
            if potential_path.exists():
                vgmstream_cli_full_path = str(potential_path.resolve())
            else:
                print(f"Error: vgmstream-cli executable not found via PATH or at specified path: {vgmstream_cli_path}", file=sys.stderr)
                sys.exit(1)

    print(f"Resolved vgmstream-cli full path: {vgmstream_cli_full_path}")


    # Get the full path of the source directory AFTER reading config
    audio_source_dir_full_path = os.path.abspath(audio_source_dir)
    print(f"Absolute Audio Source Dir: {audio_source_dir_full_path}")
    if not os.path.isdir(audio_source_dir_full_path):
        print(f"Error: Audio source directory does not exist: {audio_source_dir_full_path}", file=sys.stderr)
        sys.exit(1)

    # Ensure the target directory exists
    audio_target_dir_full_path = os.path.abspath(audio_target_dir)
    print(f"Absolute Audio Target Dir: {audio_target_dir_full_path}")
    os.makedirs(audio_target_dir_full_path, exist_ok=True)


    # Find all .snu files recursively
    snu_files = []
    print(f"Searching for .snu files in: {audio_source_dir_full_path}")
    for root, dirs, files in os.walk(audio_source_dir_full_path):
        for file in files:
            if file.lower().endswith(".snu"):
                snu_files.append(os.path.join(root, file))

    if not snu_files:
        print("No .snu files found in the source directory.")
        return # Exit run() gracefully if no files found

    print(f"Found {len(snu_files)} .snu files.")

    # Iterate through each .snu file
    for file_path in snu_files:
        # Get the relative path from the base of the source directory
        relative_path = os.path.relpath(file_path, audio_source_dir_full_path)
        # Use the resolved absolute target directory path
        audio_target_path = os.path.join(audio_target_dir_full_path, relative_path)

        # Make sure the directory exists in the target folder
        audio_target_directory = os.path.dirname(audio_target_path)
        os.makedirs(audio_target_directory, exist_ok=True)

        # Set the target filename with .wav extension
        wav_file = os.path.splitext(audio_target_path)[0] + ".wav"

        # Check if the output file already exists
        if os.path.exists(wav_file):
            print(f"Skipping conversion for '{os.path.basename(file_path)}' as '{os.path.basename(wav_file)}' already exists.")
            continue

        # Print the paths being used
        print(f"Converting '{relative_path}' to '{os.path.relpath(wav_file, audio_target_dir_full_path)}'")

        # Construct the command arguments
        command = [
            vgmstream_cli_full_path,
            "-f", "1",  # Fade time in seconds
            "-l", "10", # Loop count
            "-o", wav_file,
            file_path
        ]
        # print(f"Executing: {' '.join(command)}") # Debugging command

        # Run the vgmstream-cli to decode the .snu file to .wav
        try:
            # Use shell=False for better security and argument handling
            # Remove capture_output=True and text=True to let output go to terminal
            # Remove encoding and errors as they are related to text=True
            result = subprocess.run(command, check=True)
            # No need to print result.stdout or result.stderr as it's now directly in the terminal
        except subprocess.CalledProcessError as e:
            # Error message will still be printed, and vgmstream's stderr likely went to terminal already
            print(f"Error converting {relative_path}: vgmstream-cli returned non-zero exit status {e.returncode}.", file=sys.stderr)
            print(f"Command: {' '.join(e.cmd)}", file=sys.stderr)
            # Stderr from the tool should have already been printed to the console
        except FileNotFoundError:
            print(f"Error: Command not found '{vgmstream_cli_full_path}'. Make sure it's executable and in the correct path.", file=sys.stderr)
            sys.exit(1) # Exit if the tool itself is missing
        except Exception as e:
            print(f"An unexpected error occurred during conversion of {relative_path}: {e}", file=sys.stderr)


    print("Conversion process finished.")

def main():
    """Entry point of the script."""
    print("Starting audio processing...")
    run()
    print("Audio processing complete.")

if __name__ == "__main__":
    main()