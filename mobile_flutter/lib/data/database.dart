import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
// drift_flutter not required for current setup; using drift/native for local DB
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

part 'database.g.dart';

class Animals extends Table {
  IntColumn get id => integer().autoIncrement()();
  IntColumn get serverId => integer().named('server_id').nullable()();
  IntColumn get propriedadeId => integer().named('propriedade')();
  TextColumn get brinco => text()();
  TextColumn get raca => text().nullable()();
  TextColumn get sexo => text().withLength(min: 1, max: 1).nullable()();
  DateTimeColumn get dataNascimento => dateTime().named('data_nascimento').nullable()();
  TextColumn get categoria => text().nullable()();
  TextColumn get temperamento => text().nullable()();
  TextColumn get aptidao => text().nullable()();
  TextColumn get statusReprodutivo => text().named('status_reprodutivo').nullable()();
  BoolColumn get isReprodutor => boolean().named('is_reprodutor').withDefault(const Constant(false))();
  TextColumn get caracteristicas => text().named('caracteristicas_adicionais').nullable()();
  IntColumn get paiId => integer().named('pai').nullable()();
  IntColumn get maeId => integer().named('mae').nullable()();
  TextColumn get fotoPerfil => text().named('foto_perfil').nullable()();
  BoolColumn get ativo => boolean().withDefault(const Constant(true))();
  DateTimeColumn get dataNascimentoOriginal => dateTime().nullable()();
  DateTimeColumn get updatedAt => dateTime().named('updated_at').nullable()();
}

class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get op => text()(); // create/update/delete
  TextColumn get model => text()();
  TextColumn get payload => text()(); // JSON payload
  TextColumn get clientId => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

@DriftDatabase(tables: [Animals, SyncQueue])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  // Animals CRUD
  Future<List<Animal>> getAllAnimals() => select(animals).get();
  Stream<List<Animal>> watchAllAnimals() => select(animals).watch();

  Future<int> insertAnimal(AnimalsCompanion entry) => into(animals).insert(entry);
  Future<bool> updateAnimalEntry(Animal animal) => update(animals).replace(animal);
  Future<int> deleteAnimalEntry(int id) => (delete(animals)..where((t) => t.id.equals(id))).go();

  Future<Animal?> getById(int id) => (select(animals)..where((t) => t.id.equals(id))).getSingleOrNull();
  Future<Animal?> getByServerId(int serverId) => (select(animals)..where((t) => t.serverId.equals(serverId))).getSingleOrNull();

  Future<int> upsertByServerId(int? serverId, AnimalsCompanion companion) async {
    if (serverId != null) {
      final existing = await getByServerId(serverId);
      if (existing != null) {
        // update existing (no need to keep returned value)
        await (update(animals)..where((t) => t.serverId.equals(serverId))).write(companion);
        return existing.id;
      } else {
        // insert with serverId value set in companion
        return await into(animals).insert(companion);
      }
    } else {
      return await into(animals).insert(companion);
    }
  }

  // Sync queue
  Future<int> enqueue(String op, String model, String payload, {String? clientId}) {
    return into(syncQueue).insert(SyncQueueCompanion.insert(op: op, model: model, payload: payload, clientId: Value(clientId)));
  }

  Future<List<SyncQueueData>> getPendingQueue() => (select(syncQueue)..orderBy([(t) => OrderingTerm(expression: t.createdAt)])).get();
  Future<int> removeQueueItem(int id) => (delete(syncQueue)..where((t) => t.id.equals(id))).go();
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'datumagro.sqlite'));
    return NativeDatabase(file);
  });
}
