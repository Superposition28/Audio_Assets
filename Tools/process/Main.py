"""
This script handles the core audio processing task. It reads configuration
from 'Audconf.ini', finds audio files with a specified source extension
(e.g., .snu) in a source directory, converts them to a target extension
(e.g., .wav) using the vgmstream-cli tool, and saves them to a target
directory while preserving the relative folder structure.
"""
import subprocess
import sys
import shutil
import configparser
from pathlib import Path

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

global audio_source_dir, audio_target_dir, vgmstream_cli_path, source_ext, target_ext

# Define global variables with type hints for Path objects
audio_source_dir: Path | None = None
audio_target_dir: Path | None = None
vgmstream_cli_path: Path | None = None # Store as Path if it represents a file path
source_ext: str = ".snu"
target_ext: str = ".wav"

def read_config(file_path: Path) -> None:
    """Reads and displays the contents of a configuration file using pathlib."""
    config = configparser.ConfigParser()

    print(f"Config file path: {file_path}")

    if not file_path.exists():
        print(f"Error: Configuration file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    config.read(file_path)

    print(f"Config file sections found: {config.sections()}")

    global audio_source_dir, audio_target_dir, vgmstream_cli_path, source_ext, target_ext

    # Read paths and store them as Path objects
    audio_source_dir_str = config.get('Directories', 'AUDIO_SOURCE_DIR', fallback=None)
    audio_target_dir_str = config.get('Directories', 'AUDIO_TARGET_DIR', fallback=None)
    vgmstream_cli_path_str = config.get('Tools', 'vgmstream-cli', fallback=None)
    source_ext = config.get('Extensions', 'SOURCE_EXT', fallback=".snu") # e.g., .snu
    target_ext = config.get('Extensions', 'TARGET_EXT', fallback=".wav") # e.g., .wav

    if audio_source_dir_str:
        audio_source_dir = Path(audio_source_dir_str)
    if audio_target_dir_str:
        audio_target_dir = Path(audio_target_dir_str)
    if vgmstream_cli_path_str:
        # Treat vgmstream-cli path as Path, but it might just be a command name
        # We'll resolve it later in run()
        vgmstream_cli_path = Path(vgmstream_cli_path_str)
    else:
        print("Error: 'vgmstream-cli' path not found in [Tools] section of config file.", file=sys.stderr)
        sys.exit(1)

    # Ensure extensions start with a dot
    if not source_ext.startswith('.'):
        source_ext = '.' + source_ext
    if not target_ext.startswith('.'):
        target_ext = '.' + target_ext

    print(f"Using Audio Source Dir: {audio_source_dir}")
    print(f"Using Audio Target Dir: {audio_target_dir}")
    print(f"Using vgmstream-cli reference: {vgmstream_cli_path}")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run():
    """Contains the main logic for finding and processing audio files using pathlib."""
    global audio_source_dir, audio_target_dir, vgmstream_cli_path, source_ext, target_ext

    # Ensure paths were loaded
    if not audio_source_dir or not audio_target_dir or not vgmstream_cli_path:
        print("Error: Configuration paths not loaded correctly.", file=sys.stderr)
        sys.exit(1)

    # Output the result from the script
    print(f"vgmstream-cli path from config: {vgmstream_cli_path}")

    # Resolve vgmstream-cli path
    vgmstream_cli_full_path_str = shutil.which(str(vgmstream_cli_path))
    if not vgmstream_cli_full_path_str:
        # Check if the path specified in config exists (relative or absolute)
        if vgmstream_cli_path.exists():
             vgmstream_cli_full_path_str = str(vgmstream_cli_path.resolve())
        else:
            # Try resolving relative to the script directory
            script_dir = Path(__file__).resolve().parent
            potential_path = script_dir / vgmstream_cli_path
            if potential_path.exists():
                vgmstream_cli_full_path_str = str(potential_path.resolve())
            else:
                print(f"Error: vgmstream-cli executable not found via PATH or at specified path: {vgmstream_cli_path}", file=sys.stderr)
                sys.exit(1)

    print(f"Resolved vgmstream-cli full path: {vgmstream_cli_full_path_str}")


    # Get the full path of the source directory
    audio_source_dir_full = audio_source_dir.resolve()
    print(f"Absolute Audio Source Dir: {audio_source_dir_full}")
    if not audio_source_dir_full.is_dir():
        print(f"Error: Audio source directory does not exist: {audio_source_dir_full}", file=sys.stderr)
        sys.exit(1)

    # Ensure the target directory exists
    audio_target_dir_full = audio_target_dir.resolve()
    print(f"Absolute Audio Target Dir: {audio_target_dir_full}")
    audio_target_dir_full.mkdir(parents=True, exist_ok=True)


    # Find all source_ext files recursively using rglob
    print(f"Searching for *{source_ext} files in: {audio_source_dir_full}")
    # Use lower() on suffix for case-insensitive matching if needed, though rglob pattern handles it
    snu_files = list(audio_source_dir_full.rglob(f'*{source_ext}'))

    if not snu_files:
        print(f"No {source_ext} files found in the source directory.")
        return # Exit run() gracefully if no files found

    print(f"Found {len(snu_files)} {source_ext} files.")

    skip_count = 0
    loop_count = 0

    # Iterate through each source_ext file (which are Path objects)
    for target_file_path in snu_files:
        loop_count += 1
        # Get the relative path from the base of the source directory
        relative_path = target_file_path.relative_to(audio_source_dir_full)
        # Construct the target path using the resolved absolute target directory path
        audio_target_path = audio_target_dir_full / relative_path

        # Make sure the directory exists in the target folder
        audio_target_directory = audio_target_path.parent
        audio_target_directory.mkdir(parents=True, exist_ok=True)

        # Set the target filename with target_ext extension
        wav_file = audio_target_path.with_suffix(target_ext)

        # Check if the output file already exists
        if wav_file.exists():
            skip_count += 1
            # print(f"Skipping conversion for '{target_file_path.name}' as '{wav_file.name}' already exists.")
            continue

        # Print the paths being used
        print(f"Converting '{relative_path}' to '{wav_file.relative_to(audio_target_dir_full)}'")

        # Construct the command arguments (ensure paths are strings for subprocess)
        command = [
            vgmstream_cli_full_path_str,
            "-f", "1",  # Fade time in seconds
            "-l", "10", # Loop count
            "-o", str(wav_file),
            str(target_file_path)
        ]
        # print(f"Executing: {' '.join(command)}") # Debugging command

        # Run the vgmstream-cli to decode the source_ext file to target_ext
        try:
            # Pass command elements as strings
            result = subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {relative_path}: vgmstream-cli returned non-zero exit status {e.returncode}.", file=sys.stderr)
            print(f"Command: {' '.join(map(str, e.cmd))}", file=sys.stderr) # Ensure command parts are strings for join
        except FileNotFoundError:
            print(f"Error: Command not found '{vgmstream_cli_full_path_str}'. Make sure it's executable and in the correct path.", file=sys.stderr)
            sys.exit(1) # Exit if the tool itself is missing
        except Exception as e:
            print(f"An unexpected error occurred during conversion of {relative_path}: {e}", file=sys.stderr)

    print("Processing complete.")
    if skip_count > 0:
        print(f"Skipped {skip_count} files that already exist in the target directory.")
    else:
        print(f"All {len(snu_files)} processed successfully.")
    print(f"Processed {loop_count} files in total.")

def main(module_dir_str: str) -> None:
    """Entry point of the script."""
    module_dir = Path(module_dir_str) # Convert input string to Path
    config_file = module_dir / "Audconf.ini" # Use Path operator

    read_config(config_file)

    run()
    print("Audio processing complete.")

if __name__ == "__main__":
    # Assuming the script is run from a context where the module dir needs to be determined
    # If this script is always in the 'process' dir relative to 'Audconf.ini'
    script_dir = Path(__file__).resolve().parent
    module_dir = script_dir.parent # Go up one level from 'process' to 'Tools'
    # If Audconf.ini is in the 'Tools' directory alongside 'process'
    # main(str(module_dir))
    # If Audconf.ini is one level higher (e.g., in Audio_Assets)
    audio_assets_dir = module_dir.parent
    main(str(audio_assets_dir)) # Pass the path as a string
