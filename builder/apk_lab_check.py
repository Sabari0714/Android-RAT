"""Safe APK validation for an Android lab.

This module inspects an APK and verifies alignment/signature when the
corresponding Android SDK tools are installed. It does not patch, generate,
or remotely control an APK.
"""

import os
import shutil
import subprocess
import zipfile


def tool_path(name):
    return shutil.which(name)


def run(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        output = (result.stdout or result.stderr).strip()
        return result.returncode == 0, output
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)


def validate_apk(apk_path):
    """Return a structured validation report for a local APK file."""
    report = {
        "path": apk_path,
        "exists": os.path.isfile(apk_path),
        "zip_valid": False,
        "aligned": None,
        "signed": None,
        "details": [],
    }

    if not report["exists"]:
        report["details"].append("APK file was not found.")
        return report

    try:
        with zipfile.ZipFile(apk_path, "r") as archive:
            bad_member = archive.testzip()
            report["zip_valid"] = bad_member is None
            if bad_member:
                report["details"].append(f"Corrupt ZIP member: {bad_member}")
            else:
                report["details"].append("APK ZIP structure is readable.")
    except (OSError, zipfile.BadZipFile) as exc:
        report["details"].append(f"Invalid APK/ZIP: {exc}")
        return report

    zipalign = tool_path("zipalign")
    if zipalign:
        ok, output = run([zipalign, "-c", "-v", "4", apk_path])
        report["aligned"] = ok
        report["details"].append("zipalign: " + ("valid" if ok else output or "check failed"))
    else:
        report["details"].append("zipalign not installed; alignment check skipped.")

    apksigner = tool_path("apksigner")
    if apksigner:
        ok, output = run([apksigner, "verify", "--verbose", apk_path])
        report["signed"] = ok
        report["details"].append("apksigner: " + ("valid" if ok else output or "verification failed"))
    else:
        report["details"].append("apksigner not installed; signature check skipped.")

    return report


def print_report(apk_path):
    report = validate_apk(apk_path)
    print("\n--- Android APK Lab Check ---")
    print(f"Path:       {report['path']}")
    print(f"Exists:     {report['exists']}")
    print(f"ZIP valid:  {report['zip_valid']}")
    print(f"Aligned:    {report['aligned']}")
    print(f"Signed:     {report['signed']}")
    for detail in report["details"]:
        print(f"- {detail}")
    return report["exists"] and report["zip_valid"] and report["signed"] is not False and report["aligned"] is not False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate a local APK for Android lab testing.")
    parser.add_argument("apk", help="Path to the APK file")
    args = parser.parse_args()
    raise SystemExit(0 if print_report(args.apk) else 1)
