# Install Hermes Pocket on a Phone (Development Preview)

> **Current status:** Hermes Pocket is an in-development scaffold, not a released end-user app. There is no signed public APK, TestFlight build, deployed pairing service, or production AgentCore endpoint yet. The steps below install a local development build so you can inspect the current app shell. Chat, pairing, document assistance, approvals, and Android Screen Help are not complete product features yet.

## Before you begin

You need a checkout of this repository and the pinned toolchain versions in [`.tool-versions`](../.tool-versions).

```bash
git clone https://github.com/jolo-dev/hermes-pocket.git
cd hermes-pocket/mobile
```

Install Flutter at the repository's pinned version and run:

```bash
flutter doctor
flutter pub get
```

Resolve every required Android or iOS issue reported by `flutter doctor` before continuing.

## Android: install on a physical phone

1. On the phone, open **Settings → About phone** and tap **Build number** seven times to enable Developer options.
2. Open **Settings → System → Developer options** and enable **USB debugging**.
3. Connect the phone to the development computer with USB. Accept the phone's **Allow USB debugging** confirmation when it appears.
4. From `hermes-pocket/mobile`, verify that Flutter can see the device:

   ```bash
   flutter devices
   ```

5. Run the development build:

   ```bash
   flutter run
   ```

   Flutter installs the debug build and starts it on the selected device. If several devices are listed, pass the desired identifier:

   ```bash
   flutter run -d <device-id>
   ```

6. To create an installable release APK after release signing is configured, run:

   ```bash
   flutter build apk --release
   ```

   The APK is written under `build/app/outputs/flutter-apk/`. Install it with Android Debug Bridge:

   ```bash
   adb install -r build/app/outputs/flutter-apk/app-release.apk
   ```

### Android safety notes

- Do not enable an AccessibilityService, overlay permission, or screen capture permission for Hermes Pocket until the dedicated **Android Screen Help** feature is implemented, reviewed, and clearly presented in the app.
- Never paste AWS credentials, agent API keys, passwords, OTPs, recovery codes, or banking/card details into the app or APK configuration.

## iPhone: install on a physical device

An iPhone build requires a **Mac**, Xcode, an Apple ID, and a USB-connected iPhone. It cannot be built or signed from this Linux development host.

1. On a Mac, install Xcode and open it once to accept its license.
2. Install the pinned Flutter version, clone the repository, then run:

   ```bash
   cd hermes-pocket/mobile
   flutter doctor
   flutter pub get
   open ios/Runner.xcworkspace
   ```

3. In Xcode, select the **Runner** target.
4. Under **Signing & Capabilities**, select your Apple Development Team and choose a unique bundle identifier if Xcode asks for one.
5. Connect and unlock the iPhone. Select it as the Xcode run destination and click **Run**.
6. If prompted on the phone, trust the developer certificate under **Settings → General → VPN & Device Management**.

For a command-line run after signing is configured:

```bash
flutter run -d <iphone-device-id>
```

### iOS safety and capability notes

- iOS does not permit a system-wide floating agent bubble or arbitrary inspection of other apps' screens. The intended iOS context-sharing route is a Share Extension, screenshot/file upload, browser extension, or direct integration.
- Password use must remain within iOS AuthenticationServices/Password AutoFill; Hermes Pocket must never receive or retain the credential itself.

## Pairing an installed build (not available yet)

The final app will pair to an owner-controlled service using a one-time QR/device code. A phone will not connect directly to Amazon Bedrock AgentCore and will never hold AWS credentials.

Until the AgentCore-backed facade and pairing flow are deployed, the development app is only a local UI preview. See the active implementation plan in [`openspec/changes/hermes-pocket-cross-platform/`](../openspec/changes/hermes-pocket-cross-platform/) for the remaining work.

## Troubleshooting

| Problem | What to check |
|---|---|
| `flutter` is not found | Install Flutter and put it on `PATH`; then run `flutter doctor`. |
| Android phone is not listed | Reconnect USB, unlock the phone, approve USB debugging, then run `adb devices` and `flutter devices`. |
| iPhone is not listed | Use macOS/Xcode, unlock and trust the phone, select a signing team, then run `flutter devices`. |
| Build fails because dependencies are missing | Run `flutter pub get` from `mobile/`; do not copy credentials into `pubspec.yaml`. |
| The app has no agent connection | Expected for now: pairing, deployment, and integrations remain incomplete. |
