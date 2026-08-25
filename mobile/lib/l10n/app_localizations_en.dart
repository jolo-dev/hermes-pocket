// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'Hermes Pocket';

  @override
  String get navigationHome => 'Conversations';

  @override
  String get navigationInbox => 'Inbox';

  @override
  String get navigationSettings => 'Privacy';

  @override
  String get primaryNavigationLabel => 'Primary navigation';

  @override
  String get homePrivacyMessage => 'Private assistance, under your control.';

  @override
  String get inboxEmptyMessage =>
      'Approvals, questions, drafts, and outcomes will appear here.';

  @override
  String get settingsPrivacyMessage =>
      'Inspect permissions, paired devices, memory, and retained data.';

  @override
  String get languageSettingsTitle => 'Language preferences';

  @override
  String get interfaceLanguageLabel => 'Interface language';

  @override
  String get replyLanguageLabel => 'Agent reply language';

  @override
  String get replyLanguageHelp =>
      'This does not change the interface language.';

  @override
  String get languageEnglish => 'English';

  @override
  String get languageVietnamese => 'Vietnamese';

  @override
  String get languageGerman => 'German';
}
