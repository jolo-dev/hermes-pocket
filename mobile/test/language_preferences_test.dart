import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hermes_pocket/app.dart';
import 'package:hermes_pocket/settings/language_preferences.dart';

void main() {
  testWidgets('interface and reply languages change independently', (
    tester,
  ) async {
    final container = ProviderContainer();
    addTearDown(container.dispose);
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const HermesPocketApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Privacy'));
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('reply-language')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Vietnamese').last);
    await tester.pumpAndSettle();

    var preferences = container.read(languagePreferencesProvider);
    expect(preferences.interfaceLocale.languageCode, 'en');
    expect(preferences.replyLocale.languageCode, 'vi');
    expect(find.text('Interface language'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('interface-language')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('German').last);
    await tester.pumpAndSettle();

    preferences = container.read(languagePreferencesProvider);
    expect(preferences.interfaceLocale.languageCode, 'de');
    expect(preferences.replyLocale.languageCode, 'vi');
    expect(find.text('Oberflachensprache'), findsOneWidget);
  });
}
