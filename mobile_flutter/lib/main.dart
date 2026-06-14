import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/login.dart';
import 'screens/animals_list.dart';
import 'screens/romaneio_screen.dart';
import 'data/database.dart';

void main() {
  final db = AppDatabase();
  runApp(Provider<AppDatabase>.value(
    value: db,
    child: const DatumAgroApp(),
  ));
}

class DatumAgroApp extends StatelessWidget {
  const DatumAgroApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DatumAgro Mobile',
      theme: ThemeData(
        primarySwatch: Colors.green,
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/animals': (context) => const AnimalsListScreen(),
        '/romaneio': (context) => const RomaneioScreen(),
      },
    );
  }
}
