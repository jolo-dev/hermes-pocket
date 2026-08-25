import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hermes_pocket/l10n/app_localizations.dart';
import 'package:hermes_pocket/settings/language_preferences.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/home',
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            AppNavigationShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/home',
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/inbox',
                builder: (context, state) => const InboxScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) => const SettingsScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

class AppNavigationShell extends StatelessWidget {
  const AppNavigationShell({required this.navigationShell, super.key});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final labels = [
      localizations.navigationHome,
      localizations.navigationInbox,
      localizations.navigationSettings,
    ];
    const icons = [Icons.chat_bubble_outline, Icons.inbox_outlined, Icons.tune];

    void selectDestination(int index) {
      navigationShell.goBranch(
        index,
        initialLocation: index == navigationShell.currentIndex,
      );
    }

    final navigation = switch (Theme.of(context).platform) {
      TargetPlatform.iOS || TargetPlatform.macOS => CupertinoTabBar(
        currentIndex: navigationShell.currentIndex,
        onTap: selectDestination,
        items: [
          for (var index = 0; index < labels.length; index++)
            BottomNavigationBarItem(
              icon: Icon(icons[index], semanticLabel: labels[index]),
              label: labels[index],
            ),
        ],
      ),
      _ => NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: selectDestination,
        destinations: [
          for (var index = 0; index < labels.length; index++)
            NavigationDestination(
              icon: Icon(icons[index]),
              label: labels[index],
              tooltip: labels[index],
            ),
        ],
      ),
    };

    return Scaffold(
      body: SafeArea(child: navigationShell),
      bottomNavigationBar: Semantics(
        container: true,
        label: localizations.primaryNavigationLabel,
        child: navigation,
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return _DestinationPage(
      title: localizations.navigationHome,
      body: localizations.homePrivacyMessage,
      icon: Icons.lock_outline,
    );
  }
}

class InboxScreen extends StatelessWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return _DestinationPage(
      title: localizations.navigationInbox,
      body: localizations.inboxEmptyMessage,
      icon: Icons.inbox_outlined,
    );
  }
}

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final localizations = AppLocalizations.of(context)!;
    final preferences = ref.watch(languagePreferencesProvider);
    final controller = ref.read(languagePreferencesProvider.notifier);
    final localeLabels = {
      'en': localizations.languageEnglish,
      'vi': localizations.languageVietnamese,
      'de': localizations.languageGerman,
    };
    return Scaffold(
      appBar: AppBar(title: Text(localizations.navigationSettings)),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            localizations.settingsPrivacyMessage,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 32),
          Text(
            localizations.languageSettingsTitle,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<Locale>(
            key: const ValueKey('interface-language'),
            initialValue: preferences.interfaceLocale,
            decoration: InputDecoration(
              labelText: localizations.interfaceLanguageLabel,
            ),
            items: [
              for (final code in supportedLanguageCodes)
                DropdownMenuItem(
                  value: Locale(code),
                  child: Text(localeLabels[code]!),
                ),
            ],
            onChanged: (locale) {
              if (locale != null) controller.setInterfaceLocale(locale);
            },
          ),
          const SizedBox(height: 20),
          DropdownButtonFormField<Locale>(
            key: const ValueKey('reply-language'),
            initialValue: preferences.replyLocale,
            decoration: InputDecoration(
              labelText: localizations.replyLanguageLabel,
              helperText: localizations.replyLanguageHelp,
            ),
            items: [
              for (final code in supportedLanguageCodes)
                DropdownMenuItem(
                  value: Locale(code),
                  child: Text(localeLabels[code]!),
                ),
            ],
            onChanged: (locale) {
              if (locale != null) controller.setReplyLocale(locale);
            },
          ),
        ],
      ),
    );
  }
}

class _DestinationPage extends StatelessWidget {
  const _DestinationPage({
    required this.title,
    required this.body,
    required this.icon,
  });

  final String title;
  final String body;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 40, semanticLabel: title),
                const SizedBox(height: 16),
                Text(
                  body,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
