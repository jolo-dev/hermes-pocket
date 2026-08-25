import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hermes_pocket/app.dart';

void main() {
  for (final platform in [TargetPlatform.android, TargetPlatform.iOS]) {
    testWidgets('renders accessible navigation on ${platform.name}', (
      tester,
    ) async {
      debugDefaultTargetPlatformOverride = platform;

      await tester.pumpWidget(const ProviderScope(child: HermesPocketApp()));
      await tester.pumpAndSettle();

      expect(
        find.text('Private assistance, under your control.'),
        findsOneWidget,
      );
      expect(find.bySemanticsLabel('Primary navigation'), findsOneWidget);
      if (platform == TargetPlatform.iOS) {
        expect(find.byType(CupertinoTabBar), findsOneWidget);
      } else {
        expect(find.byType(NavigationBar), findsOneWidget);
      }

      await tester.tap(find.text('Inbox'));
      await tester.pumpAndSettle();

      expect(
        find.text(
          'Approvals, questions, drafts, and outcomes will appear here.',
        ),
        findsOneWidget,
      );
      debugDefaultTargetPlatformOverride = null;
    });
  }
}
