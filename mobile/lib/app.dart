import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hermes_pocket/l10n/app_localizations.dart';
import 'package:hermes_pocket/navigation/app_router.dart';
import 'package:hermes_pocket/settings/language_preferences.dart';

class HermesPocketApp extends ConsumerWidget {
  const HermesPocketApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final languagePreferences = ref.watch(languagePreferencesProvider);
    return MaterialApp.router(
      onGenerateTitle: (context) => AppLocalizations.of(context)!.appName,
      debugShowCheckedModeBanner: false,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: languagePreferences.interfaceLocale,
      routerConfig: router,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF155B52),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF62D6C3),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
    );
  }
}
