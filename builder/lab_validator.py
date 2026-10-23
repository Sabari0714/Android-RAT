"""Safe local Android lab checks.

This module only validates the local build environment and an explicitly
connected Android device. It does not generate payloads, start listeners,
or access device data.
"""

import shutil
import subprocess


TOOLS = ("python3", "adb", "apktool", "zipalign", "apksigner", "keytool")


def check_tools():
    """Return a mapping of required local tools to their PATH locations."""
    return {tool: shutil.which(tool) for tool in TOOLS}


def run_command(command):
    """Run a read-only local command and return (ok, output)."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        output = (result.stdout or result.stderr).strip()
        return result.returncode == 0, output
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)


def print_report():
    print("\n--- Android Lab Environment Check ---")
    tools = check_tools()
    for tool, path in tools.items():
        status = "OK" if path else "MISSING"
        print(f"[{status:7}] {tool}: {path or '-'}")

    adb = tools.get("adb")
    if not adb:
        print("\nADB is missing, so the connected-device check was skipped.")
        return False

    ok, output = run_command([adb, "devices"])
    print("\n--- ADB Device Check ---")
    print(output or "No ADB output.")
    if not ok:
        print("ADB command failed.")
        return False

    # A line ending in '\tdevice' represents an authorized online device.
    online = any(line.endswith("\tdevice") for line in output.splitlines())
    if online:
        print("[OK     ] An authorized Android device is connected.")
    else:
        print("[INFO   ] No authorized online Android device detected.")

    return online


if __name__ == "__main__":
    print_report()
