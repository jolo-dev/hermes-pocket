# Install Hermes Pocket on a Phone (Development Preview)

> **Current status:** Hermes Pocket is an in-development React Native project, not a released or pairable consumer app. There is no signed public APK, TestFlight build, deployed pairing service, or production AgentCore endpoint. The current build is a local shell with generated contracts and privacy-safe TypeScript/native boundaries.

Hermes Pocket uses its committed `mobile/android/` and `mobile/ios/` projects. Expo Go is not supported.

## Shared setup

Install the pinned Node.js version from [`.tool-versions`](../.tool-versions), then run:

```bash
cd hermes-pocket/mobile
npm ci
npm run generate:api
npm run typecheck
npm test
```

## Android development build

Install JDK 17, Android Studio, Android SDK platform 37, Android build tools 37.0.0, and the Android command-line tools. Set `ANDROID_HOME` according to the React Native environment guide.

1. Enable Developer options and USB debugging on the phone.
2. Connect and authorize the phone, then verify it with `adb devices`.
3. Start Metro with `npm start`.
4. In another terminal under `mobile/`, run `npm run android`.

The owned native build can also be checked directly:

```bash
cd android
./gradlew assembleDebug
```

Android Screen Help remains disabled in this build. Do not attempt to enable accessibility, overlay, or screen-capture access until its onboarding, sanitizer, preview, and device tests are implemented.

For a complete physical-device walkthrough, see [Run Hermes Pocket on a Google Pixel](run-on-google-pixel.md).

## iPhone development build

An iPhone build requires macOS, Xcode, CocoaPods, an Apple ID, and a connected iPhone. It cannot be built or signed from a Linux host.

```bash
cd hermes-pocket/mobile
npm ci
bundle install
bundle exec pod install --project-directory=ios
open ios/HermesPocket.xcworkspace
```

In Xcode, select the `HermesPocket` scheme, choose an Apple Development Team for both `HermesPocket` and `HermesPocketShare`, replace the example App Group if required by your team, select the device, and run. The Share Extension target is present but intentionally stages nothing in this development build.

iOS does not support arbitrary cross-app inspection or a system-wide Hermes Pocket overlay. Context must come from an explicit share, screenshot/file import, browser extension, or direct integration.

## Safety

- Do not add AWS, AgentCore, model-provider, APNs/FCM, signing, or backend credentials to mobile source or pairing payloads.
- Do not enter passwords, OTPs, recovery codes, card details, or bank identifiers into development fixtures or configuration.
- Credential use must remain inside Android Credential Manager or iOS AuthenticationServices/Password AutoFill.
- Pairing and remote agent features are unavailable until their unchecked OpenSpec tasks are implemented and verified.
