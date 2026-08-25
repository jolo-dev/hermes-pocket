// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Vietnamese (`vi`).
class AppLocalizationsVi extends AppLocalizations {
  AppLocalizationsVi([String locale = 'vi']) : super(locale);

  @override
  String get appName => 'Hermes Pocket';

  @override
  String get navigationHome => 'Cuoc tro chuyen';

  @override
  String get navigationInbox => 'Hop thu';

  @override
  String get navigationSettings => 'Quyen rieng tu';

  @override
  String get primaryNavigationLabel => 'Dieu huong chinh';

  @override
  String get homePrivacyMessage => 'Tro giup rieng tu, do ban kiem soat.';

  @override
  String get inboxEmptyMessage =>
      'Phe duyet, cau hoi, ban nhap va ket qua se xuat hien o day.';

  @override
  String get settingsPrivacyMessage =>
      'Kiem tra quyen, thiet bi da ghep noi, bo nho va du lieu.';

  @override
  String get languageSettingsTitle => 'Tuy chon ngon ngu';

  @override
  String get interfaceLanguageLabel => 'Ngon ngu giao dien';

  @override
  String get replyLanguageLabel => 'Ngon ngu tra loi cua tac nhan';

  @override
  String get replyLanguageHelp =>
      'Tuy chon nay khong thay doi ngon ngu giao dien.';

  @override
  String get languageEnglish => 'Tieng Anh';

  @override
  String get languageVietnamese => 'Tieng Viet';

  @override
  String get languageGerman => 'Tieng Duc';
}
