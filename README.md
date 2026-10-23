# Android-RAT

**Android-RAT** is an educational Android security-testing project. The repository contains tooling for APK inspection/patching/signing and a lab environment validator. Any testing must be limited to devices you own or have explicit authorization to test.

---

## ⚠️ Disclaimer

Use this project only for authorized security research and your own lab devices. Do not deploy software from this repository to devices without the owner's explicit permission.

---

## Repository components

- `cli.py` - command-line entry point.
- `builder/apk_signer.py` - APK signing helper.
- `builder/apk_patch.py` - APK patch/build helper.
- `builder/apk_patcher.py` - legacy APK patching helper.
- `builder/lab_validator.py` - **safe local lab check** for required tools and an explicitly connected Android device.
- `builder/payload_generator.py` and `builder/metasploit_handler.py` - security-research components retained in the repository; use only within an authorized lab.

---

## Safe lab validation

Before testing any APK on a second phone, verify the local environment first:

```bash
python3 builder/lab_validator.py
```

The validator only checks whether these local tools are available:

- Python 3
- ADB
- apktool
- zipalign
- apksigner
- keytool

It then runs the read-only `adb devices` check and reports whether an authorized Android device is connected. It does **not** collect device data, start a listener, generate a payload, or execute remote commands.

### Two-phone lab setup

For an authorized two-phone lab, keep the test device physically under your control and verify the device appears as `device` in `adb devices` before installing or testing any APK. Disconnect USB/Wi-Fi debugging after the test is complete.

---

## General requirements

A Linux environment is recommended for the existing build helpers. Depending on the specific helper being used, tools such as Python 3, apktool, zipalign, apksigner, Java/keytool, and Android SDK platform tools may be required.

### Debug keystore

For ordinary APK signing tests, a debug keystore can be created with:

```bash
mkdir -p ~/.android
keytool -genkey -v -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
```

---

## License

[MIT](./LICENSE)
