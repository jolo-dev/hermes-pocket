import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

const supportedLanguageCodes = {'en', 'vi', 'de'};

class LanguagePreferences {
  const LanguagePreferences({
    required this.interfaceLocale,
    required this.replyLocale,
  });

  final Locale interfaceLocale;
  final Locale replyLocale;

  LanguagePreferences copyWith({Locale? interfaceLocale, Locale? replyLocale}) {
    return LanguagePreferences(
      interfaceLocale: interfaceLocale ?? this.interfaceLocale,
      replyLocale: replyLocale ?? this.replyLocale,
    );
  }
}

class LanguagePreferencesController extends Notifier<LanguagePreferences> {
  @override
  LanguagePreferences build() {
    return const LanguagePreferences(
      interfaceLocale: Locale('en'),
      replyLocale: Locale('en'),
    );
  }

  void setInterfaceLocale(Locale locale) {
    _requireSupported(locale);
    state = state.copyWith(interfaceLocale: locale);
  }

  void setReplyLocale(Locale locale) {
    _requireSupported(locale);
    state = state.copyWith(replyLocale: locale);
  }

  void _requireSupported(Locale locale) {
    if (!supportedLanguageCodes.contains(locale.languageCode)) {
      throw ArgumentError.value(locale, 'locale', 'Unsupported language');
    }
  }
}

final languagePreferencesProvider =
    NotifierProvider<LanguagePreferencesController, LanguagePreferences>(
      LanguagePreferencesController.new,
    );
