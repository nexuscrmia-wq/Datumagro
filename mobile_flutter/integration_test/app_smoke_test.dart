import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:datumagro_mobile/main.dart' as app;
import 'package:datumagro_mobile/data/database.dart';

void main() {
  // Integration test binding

  testWidgets('App smoke test: login -> animals list',
      (WidgetTester tester) async {
    // Provide a real AppDatabase instance similar to main()
    final db = AppDatabase();
    await tester.pumpWidget(Provider<AppDatabase>.value(
      value: db,
      child: const app.DatumAgroApp(),
    ));

    await tester.pumpAndSettle();

    final emailField = find.byKey(const Key('login_email'));
    final passField = find.byKey(const Key('login_password'));
    final loginButton = find.byKey(const Key('login_button'));

    expect(emailField, findsOneWidget);
    expect(passField, findsOneWidget);
    expect(loginButton, findsOneWidget);

    await tester.enterText(emailField, 'demo@example.com');
    await tester.enterText(passField, 'Testpass123!');
    await tester.tap(loginButton);

    // wait for navigation / network
    await tester.pumpAndSettle(const Duration(seconds: 5));

    // verify we reached animals screen by finding the title
    final animalsTitle = find.byKey(const Key('animals_title'));
    expect(animalsTitle, findsOneWidget);
  }, timeout: const Timeout(Duration(seconds: 60)));
}
