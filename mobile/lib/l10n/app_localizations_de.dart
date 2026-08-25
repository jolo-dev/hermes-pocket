// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for German (`de`).
class AppLocalizationsDe extends AppLocalizations {
  AppLocalizationsDe([String locale = 'de']) : super(locale);

  @override
  String get appName => 'Hermes Pocket';

  @override
  String get navigationHome => 'Unterhaltungen';

  @override
  String get navigationInbox => 'Posteingang';

  @override
  String get navigationSettings => 'Datenschutz';

  @override
  String get primaryNavigationLabel => 'Hauptnavigation';

  @override
  String get homePrivacyMessage => 'Private Hilfe unter Ihrer Kontrolle.';

  @override
  String get inboxEmptyMessage =>
      'Freigaben, Fragen, Entwurfe und Ergebnisse erscheinen hier.';

  @override
  String get settingsPrivacyMessage =>
      'Berechtigungen, gekoppelte Gerate, Speicher und Daten prufen.';

  @override
  String get languageSettingsTitle => 'Spracheinstellungen';

  @override
  String get interfaceLanguageLabel => 'Oberflachensprache';

  @override
  String get replyLanguageLabel => 'Antwortsprache des Agenten';

  @override
  String get replyLanguageHelp => 'Dies andert die Oberflachensprache nicht.';

  @override
  String get languageEnglish => 'Englisch';

  @override
  String get languageVietnamese => 'Vietnamesisch';

  @override
  String get languageGerman => 'Deutsch';
}
