# Run Hermes Pocket on a Google Pixel (Development Build)

> **Development preview only.** The current app is a local React Native shell. It has no deployed pairing/backend service and cannot yet perform remote agent actions. Android Screen Help is disabled; do not try to enable its accessibility service or overlay.

This guide installs a debug build on a Google Pixel using the repository's committed Android project. **Expo Go is not used.**

## 1. Prepare the development machine

Install the versions pinned in [`.tool-versions`](../.tool-versions):

- Node.js `22.23.2`
- JDK 17
- Android Studio, including Android SDK Platform 37, Build Tools 37.0.0, Android SDK Command-line Tools, and Platform Tools (`adb`)

Set the Android SDK location for the shell, for example on Linux:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
```

Add those exports to your shell profile if they work for your Android Studio installation. Confirm the tooling is available:

```bash
java -version
adb version
```

Clone the repository and prepare the app:

```bash
git clone https://github.com/jolo-dev/hermes-pocket.git
cd hermes-pocket/mobile
npm ci
npm run generate:api
npm run typecheck
npm test
```

## 2. Enable Pixel developer access

On the Pixel:

1. Open **Settings → About phone**.
2. Tap **Build number** seven times and authenticate when prompted.
3. Return to **Settings → System → Developer options**.
4. Turn on **USB debugging** and accept the warning.
5. Connect the Pixel to the development machine with a data-capable USB cable.
6. When the Pixel asks to allow USB debugging for the computer, choose **Allow**. For a trusted personal machine, you may choose **Always allow from this computer**.

On the development machine, verify that the phone is authorized:

```bash
adb devices
```

Expected shape:

```text
List of devices attached
PIXEL_SERIAL_NUMBER    device
```

If the state is `unauthorized`, unlock the Pixel and accept the debugging prompt. If it is absent, try a different USB cable/port and select **File transfer** from the Pixel USB notification.

## 3. Build and install the debug app

From `hermes-pocket/mobile`, start Metro in one terminal:

```bash
npm start
```

Keep Metro running. In a second terminal, still in `hermes-pocket/mobile`, build, install, and launch the committed Android project:

```bash
npm run android
```

This uses the owned Gradle project under `mobile/android/`, installs the debug package `com.hermespocket` on the connected Pixel, and starts Hermes Pocket.

### Alternative: build/install explicitly

Use this when the React Native CLI cannot select the connected device:

```bash
cd hermes-pocket/mobile/android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell monkey -p com.hermespocket 1
```

For a fresh install, replace `adb install -r` with `adb install`. To remove the debug app and its local data:

```bash
adb uninstall com.hermespocket
```

## 4. Daily development loop

With the Pixel connected and Metro running:

- Press `r` in the Metro terminal to reload the app.
- Press `d` in the Metro terminal to open the Android developer menu.
- Use `adb logcat` to inspect device logs. Avoid pasting real documents, credentials, OTPs, card data, or bank data into bug reports/log captures.

If Metro cannot reach the phone over USB, run:

```bash
adb reverse tcp:8081 tcp:8081
```

Then reload the app.

## 5. Current capability boundaries

The installed app is safe only as a development preview:

- it has no configured production backend, credentials, pairing claim, push provider, or AgentCore endpoint;
- Android Screen Help is declared but **disabled** in the manifest and must not be enabled manually;
- do not grant Accessibility, overlay, screen capture, or unrelated app permissions;
- never put passwords, OTPs, recovery codes, payment-card data, bank identifiers, API keys, AWS credentials, or signing keys into app settings, source, fixtures, logs, or test messages.

See [Install Hermes Pocket on a Phone](install-on-phone.md) for the cross-platform development overview.
