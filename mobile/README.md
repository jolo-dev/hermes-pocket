# Hermes Pocket Mobile

This is the owned React Native 0.87 and TypeScript mobile project. It contains committed Android and iOS projects and does not use Expo Go.

## Shared checks

```bash
npm ci
npm run generate:api
npm run typecheck
npm run lint
npm test
npm run codegen
```

`src/generated/api/` is generated from `../contracts/openapi/v1.yaml` and `../contracts/schemas/v1/mobile-api.schema.json`. Do not edit it by hand.

## Android

Install JDK 17 and the React Native Android SDK prerequisites, then run:

```bash
npm run android
```

The committed Gradle wrapper is the native build entry point. Android Screen Help is only a disabled service scaffold: it retrieves no window content and cannot be enabled by the current app.

## iOS

iOS requires macOS and Xcode. Install dependencies and build the committed workspace:

```bash
bundle install
bundle exec pod install --project-directory=ios
npm run ios
```

The `HermesPocket` scheme embeds the committed `HermesPocketShare` target. The current Share Extension deliberately cancels without staging content; task 8.3 remains incomplete.

Never add service credentials, push-provider credentials, signing material, passwords, OTPs, recovery codes, card data, or bank identifiers to this project.
