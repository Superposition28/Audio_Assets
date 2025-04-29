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

def run(
    audio_source_dir: Path,
    audio_target_dir: Path,
    vgmstream_cli_ref: Path | str, # Can be name or path
    source_ext: str,
    target_ext: str
    ) -> None:
    """Contains the main logic for finding and processing audio files using pathlib."""

    def resolve_vgmstream_cli_path(cli_ref: Path | str) -> str:
        """Resolve the full path of the vgmstream-cli executable."""
        vgmstream_cli_full_path_str = shutil.which(str(cli_ref))
        if vgmstream_cli_full_path_str:
            print(f"Found vgmstream-cli in PATH: {vgmstream_cli_full_path_str}")
            return vgmstream_cli_full_path_str

        cli_path = Path(cli_ref)
        if cli_path.is_file():
            vgmstream_cli_full_path_str = str(cli_path.resolve())
            print(f"Using specified vgmstream-cli path: {vgmstream_cli_full_path_str}")
            return vgmstream_cli_full_path_str

        script_dir = Path(__file__).resolve().parent
        potential_path = script_dir / cli_path
        if potential_path.is_file():
            vgmstream_cli_full_path_str = str(potential_path.resolve())
            print(f"Found vgmstream-cli relative to script: {vgmstream_cli_full_path_str}")
            return vgmstream_cli_full_path_str

        print(f"Error: vgmstream-cli executable not found via PATH, specified path, or relative to script: {cli_ref}", file=sys.stderr)
        sys.exit(1)

    vgmstream_cli_full_path_str = resolve_vgmstream_cli_path(vgmstream_cli_ref)

    def prepare_directories(source_dir: Path, target_dir: Path) -> tuple[Path, Path]:
        """Prepare and validate source and target directories."""
        audio_source_dir_full = source_dir.resolve()
        if not audio_source_dir_full.is_dir():
            print(f"Error: Audio source directory does not exist: {audio_source_dir_full}", file=sys.stderr)
            sys.exit(1)
        audio_target_dir_full = target_dir.resolve()
        audio_target_dir_full.mkdir(parents=True, exist_ok=True)
        return audio_source_dir_full, audio_target_dir_full

    audio_source_dir_full, audio_target_dir_full = prepare_directories(audio_source_dir, audio_target_dir)

    def process_audio_files(
            source_dir_full: Path,
            target_dir_full: Path,
            cli_full_path_str: str,
            src_ext: str,
            tgt_ext: str
        ) -> None:
        """Process audio files by converting them from source_ext to target_ext."""
        source_files = list(source_dir_full.rglob(f'*{src_ext}'))
        if not source_files:
            print(f"No {src_ext} files found in the source directory: {source_dir_full}")
            return
        print(f"Found {len(source_files)} {src_ext} files.")

        target_files = list(target_dir_full.rglob(f'*{tgt_ext}'))
        if not target_files:
            print(f"No {tgt_ext} files found in the target directory: {target_dir_full}")
            return
        print(f"Found {len(target_files)} {tgt_ext} files.")

        if len(target_files) == len(source_files):
            print("All files already converted. No action needed.")
            return

        skip_count = 0
        success_count = 0
        error_count = 0
        for source_file_path in source_files:
            relative_path = source_file_path.relative_to(source_dir_full)
            audio_target_path = target_dir_full / relative_path
            audio_target_directory = audio_target_path.parent
            audio_target_directory.mkdir(parents=True, exist_ok=True)
            target_file = audio_target_path.with_suffix(tgt_ext)

            if target_file.exists():
                skip_count += 1
                continue

            print(f"Converting '{relative_path}' to '{target_file.relative_to(target_dir_full)}'")
            command = [
                cli_full_path_str,
                "-o", str(target_file),
                str(source_file_path)
            ]
            try:
                subprocess.run(command, check=True, text=True)
                success_count += 1
            except subprocess.CalledProcessError as e:
                print(f"Error converting {relative_path}: vgmstream-cli failed.", file=sys.stderr)
                print(f"  Command: {' '.join(e.cmd)}", file=sys.stderr)
                print(f"  Return code: {e.returncode}", file=sys.stderr)
                print(f"  Stderr: {e.stderr}", file=sys.stderr)
                if target_file.exists():
                    try:
                        target_file.unlink()
                    except OSError as unlink_err:
                        print(f"  Warning: Could not remove potentially incomplete file {target_file}: {unlink_err}", file=sys.stderr)
                error_count += 1
            except FileNotFoundError:
                print(f"Error: Command not found '{cli_full_path_str}'. Ensure vgmstream-cli is installed and accessible.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Unexpected error during conversion of {relative_path}: {e}", file=sys.stderr)
                error_count += 1

        print("Processing complete.")
        print(f"Summary: Success={success_count}, Skipped={skip_count}, Errors={error_count}, Total Found={len(source_files)}")
        if error_count > 0:
            print("Please check the error messages above for details on failed conversions.")

    process_audio_files(
        audio_source_dir_full,
        audio_target_dir_full,
        vgmstream_cli_full_path_str,
        source_ext,
        target_ext
        )

def main(config: configparser.ConfigParser) -> None:
    """Entry point of the script, using the provided config."""
    audio_source_dir_str = config.get('Directories', 'AUDIO_SOURCE_DIR', fallback=None)
    audio_target_dir_str = config.get('Directories', 'AUDIO_TARGET_DIR', fallback=None)
    vgmstream_cli_ref_str = config.get('Tools', 'vgmstream-cli', fallback=None)
    source_ext = config.get('Extensions', 'SOURCE_EXT', fallback=".snu")
    target_ext = config.get('Extensions', 'TARGET_EXT', fallback=".wav")

    if not all([audio_source_dir_str, audio_target_dir_str, vgmstream_cli_ref_str]):
        print("Error: Missing required configuration in [Directories] or [Tools] section.", file=sys.stderr)
        print(f"  AUDIO_SOURCE_DIR: {audio_source_dir_str}")
        print(f"  AUDIO_TARGET_DIR: {audio_target_dir_str}")
        print(f"  vgmstream-cli: {vgmstream_cli_ref_str}")
        sys.exit(1)

    audio_source_dir = Path(audio_source_dir_str)
    audio_target_dir = Path(audio_target_dir_str)
    vgmstream_cli_ref = vgmstream_cli_ref_str

    if not source_ext.startswith('.'):
        source_ext = '.' + source_ext
    if not target_ext.startswith('.'):
        target_ext = '.' + target_ext

    print(f"Using Audio Source Dir: {audio_source_dir}")
    print(f"Using Audio Target Dir: {audio_target_dir}")
    print(f"Using vgmstream-cli reference: {vgmstream_cli_ref}")
    print(f"Using Source Ext: {source_ext}")
    print(f"Using Target Ext: {target_ext}")

    run(audio_source_dir, audio_target_dir, vgmstream_cli_ref, source_ext, target_ext)
    print("Audio processing task finished.")
