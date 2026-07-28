// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'database.dart';

// ignore_for_file: type=lint
class $AnimalsTable extends Animals with TableInfo<$AnimalsTable, Animal> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $AnimalsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _serverIdMeta =
      const VerificationMeta('serverId');
  @override
  late final GeneratedColumn<int> serverId = GeneratedColumn<int>(
      'server_id', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _propriedadeIdMeta =
      const VerificationMeta('propriedadeId');
  @override
  late final GeneratedColumn<int> propriedadeId = GeneratedColumn<int>(
      'propriedade', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _brincoMeta = const VerificationMeta('brinco');
  @override
  late final GeneratedColumn<String> brinco = GeneratedColumn<String>(
      'brinco', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _racaMeta = const VerificationMeta('raca');
  @override
  late final GeneratedColumn<String> raca = GeneratedColumn<String>(
      'raca', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _sexoMeta = const VerificationMeta('sexo');
  @override
  late final GeneratedColumn<String> sexo = GeneratedColumn<String>(
      'sexo', aliasedName, true,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 1, maxTextLength: 1),
      type: DriftSqlType.string,
      requiredDuringInsert: false);
  static const VerificationMeta _dataNascimentoMeta =
      const VerificationMeta('dataNascimento');
  @override
  late final GeneratedColumn<DateTime> dataNascimento =
      GeneratedColumn<DateTime>('data_nascimento', aliasedName, true,
          type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _categoriaMeta =
      const VerificationMeta('categoria');
  @override
  late final GeneratedColumn<String> categoria = GeneratedColumn<String>(
      'categoria', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _temperamentoMeta =
      const VerificationMeta('temperamento');
  @override
  late final GeneratedColumn<String> temperamento = GeneratedColumn<String>(
      'temperamento', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _aptidaoMeta =
      const VerificationMeta('aptidao');
  @override
  late final GeneratedColumn<String> aptidao = GeneratedColumn<String>(
      'aptidao', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _statusReprodutivoMeta =
      const VerificationMeta('statusReprodutivo');
  @override
  late final GeneratedColumn<String> statusReprodutivo =
      GeneratedColumn<String>('status_reprodutivo', aliasedName, true,
          type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _isReprodutorMeta =
      const VerificationMeta('isReprodutor');
  @override
  late final GeneratedColumn<bool> isReprodutor = GeneratedColumn<bool>(
      'is_reprodutor', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("is_reprodutor" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _caracteristicasMeta =
      const VerificationMeta('caracteristicas');
  @override
  late final GeneratedColumn<String> caracteristicas = GeneratedColumn<String>(
      'caracteristicas_adicionais', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _paiIdMeta = const VerificationMeta('paiId');
  @override
  late final GeneratedColumn<int> paiId = GeneratedColumn<int>(
      'pai', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _maeIdMeta = const VerificationMeta('maeId');
  @override
  late final GeneratedColumn<int> maeId = GeneratedColumn<int>(
      'mae', aliasedName, true,
      type: DriftSqlType.int, requiredDuringInsert: false);
  static const VerificationMeta _fotoPerfilMeta =
      const VerificationMeta('fotoPerfil');
  @override
  late final GeneratedColumn<String> fotoPerfil = GeneratedColumn<String>(
      'foto_perfil', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _ativoMeta = const VerificationMeta('ativo');
  @override
  late final GeneratedColumn<bool> ativo = GeneratedColumn<bool>(
      'ativo', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("ativo" IN (0, 1))'),
      defaultValue: const Constant(true));
  static const VerificationMeta _dataNascimentoOriginalMeta =
      const VerificationMeta('dataNascimentoOriginal');
  @override
  late final GeneratedColumn<DateTime> dataNascimentoOriginal =
      GeneratedColumn<DateTime>('data_nascimento_original', aliasedName, true,
          type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        serverId,
        propriedadeId,
        brinco,
        raca,
        sexo,
        dataNascimento,
        categoria,
        temperamento,
        aptidao,
        statusReprodutivo,
        isReprodutor,
        caracteristicas,
        paiId,
        maeId,
        fotoPerfil,
        ativo,
        dataNascimentoOriginal,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'animals';
  @override
  VerificationContext validateIntegrity(Insertable<Animal> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('server_id')) {
      context.handle(_serverIdMeta,
          serverId.isAcceptableOrUnknown(data['server_id']!, _serverIdMeta));
    }
    if (data.containsKey('propriedade')) {
      context.handle(
          _propriedadeIdMeta,
          propriedadeId.isAcceptableOrUnknown(
              data['propriedade']!, _propriedadeIdMeta));
    } else if (isInserting) {
      context.missing(_propriedadeIdMeta);
    }
    if (data.containsKey('brinco')) {
      context.handle(_brincoMeta,
          brinco.isAcceptableOrUnknown(data['brinco']!, _brincoMeta));
    } else if (isInserting) {
      context.missing(_brincoMeta);
    }
    if (data.containsKey('raca')) {
      context.handle(
          _racaMeta, raca.isAcceptableOrUnknown(data['raca']!, _racaMeta));
    }
    if (data.containsKey('sexo')) {
      context.handle(
          _sexoMeta, sexo.isAcceptableOrUnknown(data['sexo']!, _sexoMeta));
    }
    if (data.containsKey('data_nascimento')) {
      context.handle(
          _dataNascimentoMeta,
          dataNascimento.isAcceptableOrUnknown(
              data['data_nascimento']!, _dataNascimentoMeta));
    }
    if (data.containsKey('categoria')) {
      context.handle(_categoriaMeta,
          categoria.isAcceptableOrUnknown(data['categoria']!, _categoriaMeta));
    }
    if (data.containsKey('temperamento')) {
      context.handle(
          _temperamentoMeta,
          temperamento.isAcceptableOrUnknown(
              data['temperamento']!, _temperamentoMeta));
    }
    if (data.containsKey('aptidao')) {
      context.handle(_aptidaoMeta,
          aptidao.isAcceptableOrUnknown(data['aptidao']!, _aptidaoMeta));
    }
    if (data.containsKey('status_reprodutivo')) {
      context.handle(
          _statusReprodutivoMeta,
          statusReprodutivo.isAcceptableOrUnknown(
              data['status_reprodutivo']!, _statusReprodutivoMeta));
    }
    if (data.containsKey('is_reprodutor')) {
      context.handle(
          _isReprodutorMeta,
          isReprodutor.isAcceptableOrUnknown(
              data['is_reprodutor']!, _isReprodutorMeta));
    }
    if (data.containsKey('caracteristicas_adicionais')) {
      context.handle(
          _caracteristicasMeta,
          caracteristicas.isAcceptableOrUnknown(
              data['caracteristicas_adicionais']!, _caracteristicasMeta));
    }
    if (data.containsKey('pai')) {
      context.handle(
          _paiIdMeta, paiId.isAcceptableOrUnknown(data['pai']!, _paiIdMeta));
    }
    if (data.containsKey('mae')) {
      context.handle(
          _maeIdMeta, maeId.isAcceptableOrUnknown(data['mae']!, _maeIdMeta));
    }
    if (data.containsKey('foto_perfil')) {
      context.handle(
          _fotoPerfilMeta,
          fotoPerfil.isAcceptableOrUnknown(
              data['foto_perfil']!, _fotoPerfilMeta));
    }
    if (data.containsKey('ativo')) {
      context.handle(
          _ativoMeta, ativo.isAcceptableOrUnknown(data['ativo']!, _ativoMeta));
    }
    if (data.containsKey('data_nascimento_original')) {
      context.handle(
          _dataNascimentoOriginalMeta,
          dataNascimentoOriginal.isAcceptableOrUnknown(
              data['data_nascimento_original']!, _dataNascimentoOriginalMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Animal map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Animal(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      serverId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}server_id']),
      propriedadeId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}propriedade'])!,
      brinco: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}brinco'])!,
      raca: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}raca']),
      sexo: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}sexo']),
      dataNascimento: attachedDatabase.typeMapping.read(
          DriftSqlType.dateTime, data['${effectivePrefix}data_nascimento']),
      categoria: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}categoria']),
      temperamento: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}temperamento']),
      aptidao: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}aptidao']),
      statusReprodutivo: attachedDatabase.typeMapping.read(
          DriftSqlType.string, data['${effectivePrefix}status_reprodutivo']),
      isReprodutor: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}is_reprodutor'])!,
      caracteristicas: attachedDatabase.typeMapping.read(DriftSqlType.string,
          data['${effectivePrefix}caracteristicas_adicionais']),
      paiId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}pai']),
      maeId: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}mae']),
      fotoPerfil: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}foto_perfil']),
      ativo: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}ativo'])!,
      dataNascimentoOriginal: attachedDatabase.typeMapping.read(
          DriftSqlType.dateTime,
          data['${effectivePrefix}data_nascimento_original']),
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at']),
    );
  }

  @override
  $AnimalsTable createAlias(String alias) {
    return $AnimalsTable(attachedDatabase, alias);
  }
}

class Animal extends DataClass implements Insertable<Animal> {
  final int id;
  final int? serverId;
  final int propriedadeId;
  final String brinco;
  final String? raca;
  final String? sexo;
  final DateTime? dataNascimento;
  final String? categoria;
  final String? temperamento;
  final String? aptidao;
  final String? statusReprodutivo;
  final bool isReprodutor;
  final String? caracteristicas;
  final int? paiId;
  final int? maeId;
  final String? fotoPerfil;
  final bool ativo;
  final DateTime? dataNascimentoOriginal;
  final DateTime? updatedAt;
  const Animal(
      {required this.id,
      this.serverId,
      required this.propriedadeId,
      required this.brinco,
      this.raca,
      this.sexo,
      this.dataNascimento,
      this.categoria,
      this.temperamento,
      this.aptidao,
      this.statusReprodutivo,
      required this.isReprodutor,
      this.caracteristicas,
      this.paiId,
      this.maeId,
      this.fotoPerfil,
      required this.ativo,
      this.dataNascimentoOriginal,
      this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    if (!nullToAbsent || serverId != null) {
      map['server_id'] = Variable<int>(serverId);
    }
    map['propriedade'] = Variable<int>(propriedadeId);
    map['brinco'] = Variable<String>(brinco);
    if (!nullToAbsent || raca != null) {
      map['raca'] = Variable<String>(raca);
    }
    if (!nullToAbsent || sexo != null) {
      map['sexo'] = Variable<String>(sexo);
    }
    if (!nullToAbsent || dataNascimento != null) {
      map['data_nascimento'] = Variable<DateTime>(dataNascimento);
    }
    if (!nullToAbsent || categoria != null) {
      map['categoria'] = Variable<String>(categoria);
    }
    if (!nullToAbsent || temperamento != null) {
      map['temperamento'] = Variable<String>(temperamento);
    }
    if (!nullToAbsent || aptidao != null) {
      map['aptidao'] = Variable<String>(aptidao);
    }
    if (!nullToAbsent || statusReprodutivo != null) {
      map['status_reprodutivo'] = Variable<String>(statusReprodutivo);
    }
    map['is_reprodutor'] = Variable<bool>(isReprodutor);
    if (!nullToAbsent || caracteristicas != null) {
      map['caracteristicas_adicionais'] = Variable<String>(caracteristicas);
    }
    if (!nullToAbsent || paiId != null) {
      map['pai'] = Variable<int>(paiId);
    }
    if (!nullToAbsent || maeId != null) {
      map['mae'] = Variable<int>(maeId);
    }
    if (!nullToAbsent || fotoPerfil != null) {
      map['foto_perfil'] = Variable<String>(fotoPerfil);
    }
    map['ativo'] = Variable<bool>(ativo);
    if (!nullToAbsent || dataNascimentoOriginal != null) {
      map['data_nascimento_original'] =
          Variable<DateTime>(dataNascimentoOriginal);
    }
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    return map;
  }

  AnimalsCompanion toCompanion(bool nullToAbsent) {
    return AnimalsCompanion(
      id: Value(id),
      serverId: serverId == null && nullToAbsent
          ? const Value.absent()
          : Value(serverId),
      propriedadeId: Value(propriedadeId),
      brinco: Value(brinco),
      raca: raca == null && nullToAbsent ? const Value.absent() : Value(raca),
      sexo: sexo == null && nullToAbsent ? const Value.absent() : Value(sexo),
      dataNascimento: dataNascimento == null && nullToAbsent
          ? const Value.absent()
          : Value(dataNascimento),
      categoria: categoria == null && nullToAbsent
          ? const Value.absent()
          : Value(categoria),
      temperamento: temperamento == null && nullToAbsent
          ? const Value.absent()
          : Value(temperamento),
      aptidao: aptidao == null && nullToAbsent
          ? const Value.absent()
          : Value(aptidao),
      statusReprodutivo: statusReprodutivo == null && nullToAbsent
          ? const Value.absent()
          : Value(statusReprodutivo),
      isReprodutor: Value(isReprodutor),
      caracteristicas: caracteristicas == null && nullToAbsent
          ? const Value.absent()
          : Value(caracteristicas),
      paiId:
          paiId == null && nullToAbsent ? const Value.absent() : Value(paiId),
      maeId:
          maeId == null && nullToAbsent ? const Value.absent() : Value(maeId),
      fotoPerfil: fotoPerfil == null && nullToAbsent
          ? const Value.absent()
          : Value(fotoPerfil),
      ativo: Value(ativo),
      dataNascimentoOriginal: dataNascimentoOriginal == null && nullToAbsent
          ? const Value.absent()
          : Value(dataNascimentoOriginal),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
    );
  }

  factory Animal.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Animal(
      id: serializer.fromJson<int>(json['id']),
      serverId: serializer.fromJson<int?>(json['serverId']),
      propriedadeId: serializer.fromJson<int>(json['propriedadeId']),
      brinco: serializer.fromJson<String>(json['brinco']),
      raca: serializer.fromJson<String?>(json['raca']),
      sexo: serializer.fromJson<String?>(json['sexo']),
      dataNascimento: serializer.fromJson<DateTime?>(json['dataNascimento']),
      categoria: serializer.fromJson<String?>(json['categoria']),
      temperamento: serializer.fromJson<String?>(json['temperamento']),
      aptidao: serializer.fromJson<String?>(json['aptidao']),
      statusReprodutivo:
          serializer.fromJson<String?>(json['statusReprodutivo']),
      isReprodutor: serializer.fromJson<bool>(json['isReprodutor']),
      caracteristicas: serializer.fromJson<String?>(json['caracteristicas']),
      paiId: serializer.fromJson<int?>(json['paiId']),
      maeId: serializer.fromJson<int?>(json['maeId']),
      fotoPerfil: serializer.fromJson<String?>(json['fotoPerfil']),
      ativo: serializer.fromJson<bool>(json['ativo']),
      dataNascimentoOriginal:
          serializer.fromJson<DateTime?>(json['dataNascimentoOriginal']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'serverId': serializer.toJson<int?>(serverId),
      'propriedadeId': serializer.toJson<int>(propriedadeId),
      'brinco': serializer.toJson<String>(brinco),
      'raca': serializer.toJson<String?>(raca),
      'sexo': serializer.toJson<String?>(sexo),
      'dataNascimento': serializer.toJson<DateTime?>(dataNascimento),
      'categoria': serializer.toJson<String?>(categoria),
      'temperamento': serializer.toJson<String?>(temperamento),
      'aptidao': serializer.toJson<String?>(aptidao),
      'statusReprodutivo': serializer.toJson<String?>(statusReprodutivo),
      'isReprodutor': serializer.toJson<bool>(isReprodutor),
      'caracteristicas': serializer.toJson<String?>(caracteristicas),
      'paiId': serializer.toJson<int?>(paiId),
      'maeId': serializer.toJson<int?>(maeId),
      'fotoPerfil': serializer.toJson<String?>(fotoPerfil),
      'ativo': serializer.toJson<bool>(ativo),
      'dataNascimentoOriginal':
          serializer.toJson<DateTime?>(dataNascimentoOriginal),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
    };
  }

  Animal copyWith(
          {int? id,
          Value<int?> serverId = const Value.absent(),
          int? propriedadeId,
          String? brinco,
          Value<String?> raca = const Value.absent(),
          Value<String?> sexo = const Value.absent(),
          Value<DateTime?> dataNascimento = const Value.absent(),
          Value<String?> categoria = const Value.absent(),
          Value<String?> temperamento = const Value.absent(),
          Value<String?> aptidao = const Value.absent(),
          Value<String?> statusReprodutivo = const Value.absent(),
          bool? isReprodutor,
          Value<String?> caracteristicas = const Value.absent(),
          Value<int?> paiId = const Value.absent(),
          Value<int?> maeId = const Value.absent(),
          Value<String?> fotoPerfil = const Value.absent(),
          bool? ativo,
          Value<DateTime?> dataNascimentoOriginal = const Value.absent(),
          Value<DateTime?> updatedAt = const Value.absent()}) =>
      Animal(
        id: id ?? this.id,
        serverId: serverId.present ? serverId.value : this.serverId,
        propriedadeId: propriedadeId ?? this.propriedadeId,
        brinco: brinco ?? this.brinco,
        raca: raca.present ? raca.value : this.raca,
        sexo: sexo.present ? sexo.value : this.sexo,
        dataNascimento:
            dataNascimento.present ? dataNascimento.value : this.dataNascimento,
        categoria: categoria.present ? categoria.value : this.categoria,
        temperamento:
            temperamento.present ? temperamento.value : this.temperamento,
        aptidao: aptidao.present ? aptidao.value : this.aptidao,
        statusReprodutivo: statusReprodutivo.present
            ? statusReprodutivo.value
            : this.statusReprodutivo,
        isReprodutor: isReprodutor ?? this.isReprodutor,
        caracteristicas: caracteristicas.present
            ? caracteristicas.value
            : this.caracteristicas,
        paiId: paiId.present ? paiId.value : this.paiId,
        maeId: maeId.present ? maeId.value : this.maeId,
        fotoPerfil: fotoPerfil.present ? fotoPerfil.value : this.fotoPerfil,
        ativo: ativo ?? this.ativo,
        dataNascimentoOriginal: dataNascimentoOriginal.present
            ? dataNascimentoOriginal.value
            : this.dataNascimentoOriginal,
        updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
      );
  Animal copyWithCompanion(AnimalsCompanion data) {
    return Animal(
      id: data.id.present ? data.id.value : this.id,
      serverId: data.serverId.present ? data.serverId.value : this.serverId,
      propriedadeId: data.propriedadeId.present
          ? data.propriedadeId.value
          : this.propriedadeId,
      brinco: data.brinco.present ? data.brinco.value : this.brinco,
      raca: data.raca.present ? data.raca.value : this.raca,
      sexo: data.sexo.present ? data.sexo.value : this.sexo,
      dataNascimento: data.dataNascimento.present
          ? data.dataNascimento.value
          : this.dataNascimento,
      categoria: data.categoria.present ? data.categoria.value : this.categoria,
      temperamento: data.temperamento.present
          ? data.temperamento.value
          : this.temperamento,
      aptidao: data.aptidao.present ? data.aptidao.value : this.aptidao,
      statusReprodutivo: data.statusReprodutivo.present
          ? data.statusReprodutivo.value
          : this.statusReprodutivo,
      isReprodutor: data.isReprodutor.present
          ? data.isReprodutor.value
          : this.isReprodutor,
      caracteristicas: data.caracteristicas.present
          ? data.caracteristicas.value
          : this.caracteristicas,
      paiId: data.paiId.present ? data.paiId.value : this.paiId,
      maeId: data.maeId.present ? data.maeId.value : this.maeId,
      fotoPerfil:
          data.fotoPerfil.present ? data.fotoPerfil.value : this.fotoPerfil,
      ativo: data.ativo.present ? data.ativo.value : this.ativo,
      dataNascimentoOriginal: data.dataNascimentoOriginal.present
          ? data.dataNascimentoOriginal.value
          : this.dataNascimentoOriginal,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Animal(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('propriedadeId: $propriedadeId, ')
          ..write('brinco: $brinco, ')
          ..write('raca: $raca, ')
          ..write('sexo: $sexo, ')
          ..write('dataNascimento: $dataNascimento, ')
          ..write('categoria: $categoria, ')
          ..write('temperamento: $temperamento, ')
          ..write('aptidao: $aptidao, ')
          ..write('statusReprodutivo: $statusReprodutivo, ')
          ..write('isReprodutor: $isReprodutor, ')
          ..write('caracteristicas: $caracteristicas, ')
          ..write('paiId: $paiId, ')
          ..write('maeId: $maeId, ')
          ..write('fotoPerfil: $fotoPerfil, ')
          ..write('ativo: $ativo, ')
          ..write('dataNascimentoOriginal: $dataNascimentoOriginal, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      serverId,
      propriedadeId,
      brinco,
      raca,
      sexo,
      dataNascimento,
      categoria,
      temperamento,
      aptidao,
      statusReprodutivo,
      isReprodutor,
      caracteristicas,
      paiId,
      maeId,
      fotoPerfil,
      ativo,
      dataNascimentoOriginal,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Animal &&
          other.id == this.id &&
          other.serverId == this.serverId &&
          other.propriedadeId == this.propriedadeId &&
          other.brinco == this.brinco &&
          other.raca == this.raca &&
          other.sexo == this.sexo &&
          other.dataNascimento == this.dataNascimento &&
          other.categoria == this.categoria &&
          other.temperamento == this.temperamento &&
          other.aptidao == this.aptidao &&
          other.statusReprodutivo == this.statusReprodutivo &&
          other.isReprodutor == this.isReprodutor &&
          other.caracteristicas == this.caracteristicas &&
          other.paiId == this.paiId &&
          other.maeId == this.maeId &&
          other.fotoPerfil == this.fotoPerfil &&
          other.ativo == this.ativo &&
          other.dataNascimentoOriginal == this.dataNascimentoOriginal &&
          other.updatedAt == this.updatedAt);
}

class AnimalsCompanion extends UpdateCompanion<Animal> {
  final Value<int> id;
  final Value<int?> serverId;
  final Value<int> propriedadeId;
  final Value<String> brinco;
  final Value<String?> raca;
  final Value<String?> sexo;
  final Value<DateTime?> dataNascimento;
  final Value<String?> categoria;
  final Value<String?> temperamento;
  final Value<String?> aptidao;
  final Value<String?> statusReprodutivo;
  final Value<bool> isReprodutor;
  final Value<String?> caracteristicas;
  final Value<int?> paiId;
  final Value<int?> maeId;
  final Value<String?> fotoPerfil;
  final Value<bool> ativo;
  final Value<DateTime?> dataNascimentoOriginal;
  final Value<DateTime?> updatedAt;
  const AnimalsCompanion({
    this.id = const Value.absent(),
    this.serverId = const Value.absent(),
    this.propriedadeId = const Value.absent(),
    this.brinco = const Value.absent(),
    this.raca = const Value.absent(),
    this.sexo = const Value.absent(),
    this.dataNascimento = const Value.absent(),
    this.categoria = const Value.absent(),
    this.temperamento = const Value.absent(),
    this.aptidao = const Value.absent(),
    this.statusReprodutivo = const Value.absent(),
    this.isReprodutor = const Value.absent(),
    this.caracteristicas = const Value.absent(),
    this.paiId = const Value.absent(),
    this.maeId = const Value.absent(),
    this.fotoPerfil = const Value.absent(),
    this.ativo = const Value.absent(),
    this.dataNascimentoOriginal = const Value.absent(),
    this.updatedAt = const Value.absent(),
  });
  AnimalsCompanion.insert({
    this.id = const Value.absent(),
    this.serverId = const Value.absent(),
    required int propriedadeId,
    required String brinco,
    this.raca = const Value.absent(),
    this.sexo = const Value.absent(),
    this.dataNascimento = const Value.absent(),
    this.categoria = const Value.absent(),
    this.temperamento = const Value.absent(),
    this.aptidao = const Value.absent(),
    this.statusReprodutivo = const Value.absent(),
    this.isReprodutor = const Value.absent(),
    this.caracteristicas = const Value.absent(),
    this.paiId = const Value.absent(),
    this.maeId = const Value.absent(),
    this.fotoPerfil = const Value.absent(),
    this.ativo = const Value.absent(),
    this.dataNascimentoOriginal = const Value.absent(),
    this.updatedAt = const Value.absent(),
  })  : propriedadeId = Value(propriedadeId),
        brinco = Value(brinco);
  static Insertable<Animal> custom({
    Expression<int>? id,
    Expression<int>? serverId,
    Expression<int>? propriedadeId,
    Expression<String>? brinco,
    Expression<String>? raca,
    Expression<String>? sexo,
    Expression<DateTime>? dataNascimento,
    Expression<String>? categoria,
    Expression<String>? temperamento,
    Expression<String>? aptidao,
    Expression<String>? statusReprodutivo,
    Expression<bool>? isReprodutor,
    Expression<String>? caracteristicas,
    Expression<int>? paiId,
    Expression<int>? maeId,
    Expression<String>? fotoPerfil,
    Expression<bool>? ativo,
    Expression<DateTime>? dataNascimentoOriginal,
    Expression<DateTime>? updatedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (serverId != null) 'server_id': serverId,
      if (propriedadeId != null) 'propriedade': propriedadeId,
      if (brinco != null) 'brinco': brinco,
      if (raca != null) 'raca': raca,
      if (sexo != null) 'sexo': sexo,
      if (dataNascimento != null) 'data_nascimento': dataNascimento,
      if (categoria != null) 'categoria': categoria,
      if (temperamento != null) 'temperamento': temperamento,
      if (aptidao != null) 'aptidao': aptidao,
      if (statusReprodutivo != null) 'status_reprodutivo': statusReprodutivo,
      if (isReprodutor != null) 'is_reprodutor': isReprodutor,
      if (caracteristicas != null)
        'caracteristicas_adicionais': caracteristicas,
      if (paiId != null) 'pai': paiId,
      if (maeId != null) 'mae': maeId,
      if (fotoPerfil != null) 'foto_perfil': fotoPerfil,
      if (ativo != null) 'ativo': ativo,
      if (dataNascimentoOriginal != null)
        'data_nascimento_original': dataNascimentoOriginal,
      if (updatedAt != null) 'updated_at': updatedAt,
    });
  }

  AnimalsCompanion copyWith(
      {Value<int>? id,
      Value<int?>? serverId,
      Value<int>? propriedadeId,
      Value<String>? brinco,
      Value<String?>? raca,
      Value<String?>? sexo,
      Value<DateTime?>? dataNascimento,
      Value<String?>? categoria,
      Value<String?>? temperamento,
      Value<String?>? aptidao,
      Value<String?>? statusReprodutivo,
      Value<bool>? isReprodutor,
      Value<String?>? caracteristicas,
      Value<int?>? paiId,
      Value<int?>? maeId,
      Value<String?>? fotoPerfil,
      Value<bool>? ativo,
      Value<DateTime?>? dataNascimentoOriginal,
      Value<DateTime?>? updatedAt}) {
    return AnimalsCompanion(
      id: id ?? this.id,
      serverId: serverId ?? this.serverId,
      propriedadeId: propriedadeId ?? this.propriedadeId,
      brinco: brinco ?? this.brinco,
      raca: raca ?? this.raca,
      sexo: sexo ?? this.sexo,
      dataNascimento: dataNascimento ?? this.dataNascimento,
      categoria: categoria ?? this.categoria,
      temperamento: temperamento ?? this.temperamento,
      aptidao: aptidao ?? this.aptidao,
      statusReprodutivo: statusReprodutivo ?? this.statusReprodutivo,
      isReprodutor: isReprodutor ?? this.isReprodutor,
      caracteristicas: caracteristicas ?? this.caracteristicas,
      paiId: paiId ?? this.paiId,
      maeId: maeId ?? this.maeId,
      fotoPerfil: fotoPerfil ?? this.fotoPerfil,
      ativo: ativo ?? this.ativo,
      dataNascimentoOriginal:
          dataNascimentoOriginal ?? this.dataNascimentoOriginal,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (serverId.present) {
      map['server_id'] = Variable<int>(serverId.value);
    }
    if (propriedadeId.present) {
      map['propriedade'] = Variable<int>(propriedadeId.value);
    }
    if (brinco.present) {
      map['brinco'] = Variable<String>(brinco.value);
    }
    if (raca.present) {
      map['raca'] = Variable<String>(raca.value);
    }
    if (sexo.present) {
      map['sexo'] = Variable<String>(sexo.value);
    }
    if (dataNascimento.present) {
      map['data_nascimento'] = Variable<DateTime>(dataNascimento.value);
    }
    if (categoria.present) {
      map['categoria'] = Variable<String>(categoria.value);
    }
    if (temperamento.present) {
      map['temperamento'] = Variable<String>(temperamento.value);
    }
    if (aptidao.present) {
      map['aptidao'] = Variable<String>(aptidao.value);
    }
    if (statusReprodutivo.present) {
      map['status_reprodutivo'] = Variable<String>(statusReprodutivo.value);
    }
    if (isReprodutor.present) {
      map['is_reprodutor'] = Variable<bool>(isReprodutor.value);
    }
    if (caracteristicas.present) {
      map['caracteristicas_adicionais'] =
          Variable<String>(caracteristicas.value);
    }
    if (paiId.present) {
      map['pai'] = Variable<int>(paiId.value);
    }
    if (maeId.present) {
      map['mae'] = Variable<int>(maeId.value);
    }
    if (fotoPerfil.present) {
      map['foto_perfil'] = Variable<String>(fotoPerfil.value);
    }
    if (ativo.present) {
      map['ativo'] = Variable<bool>(ativo.value);
    }
    if (dataNascimentoOriginal.present) {
      map['data_nascimento_original'] =
          Variable<DateTime>(dataNascimentoOriginal.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('AnimalsCompanion(')
          ..write('id: $id, ')
          ..write('serverId: $serverId, ')
          ..write('propriedadeId: $propriedadeId, ')
          ..write('brinco: $brinco, ')
          ..write('raca: $raca, ')
          ..write('sexo: $sexo, ')
          ..write('dataNascimento: $dataNascimento, ')
          ..write('categoria: $categoria, ')
          ..write('temperamento: $temperamento, ')
          ..write('aptidao: $aptidao, ')
          ..write('statusReprodutivo: $statusReprodutivo, ')
          ..write('isReprodutor: $isReprodutor, ')
          ..write('caracteristicas: $caracteristicas, ')
          ..write('paiId: $paiId, ')
          ..write('maeId: $maeId, ')
          ..write('fotoPerfil: $fotoPerfil, ')
          ..write('ativo: $ativo, ')
          ..write('dataNascimentoOriginal: $dataNascimentoOriginal, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }
}

class $SyncQueueTable extends SyncQueue
    with TableInfo<$SyncQueueTable, SyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
      'id', aliasedName, false,
      hasAutoIncrement: true,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('PRIMARY KEY AUTOINCREMENT'));
  static const VerificationMeta _opMeta = const VerificationMeta('op');
  @override
  late final GeneratedColumn<String> op = GeneratedColumn<String>(
      'op', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _modelMeta = const VerificationMeta('model');
  @override
  late final GeneratedColumn<String> model = GeneratedColumn<String>(
      'model', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _payloadMeta =
      const VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
      'payload', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns =>
      [id, op, model, payload, clientId, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_queue';
  @override
  VerificationContext validateIntegrity(Insertable<SyncQueueData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('op')) {
      context.handle(_opMeta, op.isAcceptableOrUnknown(data['op']!, _opMeta));
    } else if (isInserting) {
      context.missing(_opMeta);
    }
    if (data.containsKey('model')) {
      context.handle(
          _modelMeta, model.isAcceptableOrUnknown(data['model']!, _modelMeta));
    } else if (isInserting) {
      context.missing(_modelMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    } else if (isInserting) {
      context.missing(_payloadMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(_clientIdMeta,
          clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  SyncQueueData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncQueueData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}id'])!,
      op: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}op'])!,
      model: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}model'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload'])!,
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncQueueTable createAlias(String alias) {
    return $SyncQueueTable(attachedDatabase, alias);
  }
}

class SyncQueueData extends DataClass implements Insertable<SyncQueueData> {
  final int id;
  final String op;
  final String model;
  final String payload;
  final String? clientId;
  final DateTime createdAt;
  const SyncQueueData(
      {required this.id,
      required this.op,
      required this.model,
      required this.payload,
      this.clientId,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['op'] = Variable<String>(op);
    map['model'] = Variable<String>(model);
    map['payload'] = Variable<String>(payload);
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  SyncQueueCompanion toCompanion(bool nullToAbsent) {
    return SyncQueueCompanion(
      id: Value(id),
      op: Value(op),
      model: Value(model),
      payload: Value(payload),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      createdAt: Value(createdAt),
    );
  }

  factory SyncQueueData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncQueueData(
      id: serializer.fromJson<int>(json['id']),
      op: serializer.fromJson<String>(json['op']),
      model: serializer.fromJson<String>(json['model']),
      payload: serializer.fromJson<String>(json['payload']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'op': serializer.toJson<String>(op),
      'model': serializer.toJson<String>(model),
      'payload': serializer.toJson<String>(payload),
      'clientId': serializer.toJson<String?>(clientId),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncQueueData copyWith(
          {int? id,
          String? op,
          String? model,
          String? payload,
          Value<String?> clientId = const Value.absent(),
          DateTime? createdAt}) =>
      SyncQueueData(
        id: id ?? this.id,
        op: op ?? this.op,
        model: model ?? this.model,
        payload: payload ?? this.payload,
        clientId: clientId.present ? clientId.value : this.clientId,
        createdAt: createdAt ?? this.createdAt,
      );
  SyncQueueData copyWithCompanion(SyncQueueCompanion data) {
    return SyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      op: data.op.present ? data.op.value : this.op,
      model: data.model.present ? data.model.value : this.model,
      payload: data.payload.present ? data.payload.value : this.payload,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueData(')
          ..write('id: $id, ')
          ..write('op: $op, ')
          ..write('model: $model, ')
          ..write('payload: $payload, ')
          ..write('clientId: $clientId, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, op, model, payload, clientId, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncQueueData &&
          other.id == this.id &&
          other.op == this.op &&
          other.model == this.model &&
          other.payload == this.payload &&
          other.clientId == this.clientId &&
          other.createdAt == this.createdAt);
}

class SyncQueueCompanion extends UpdateCompanion<SyncQueueData> {
  final Value<int> id;
  final Value<String> op;
  final Value<String> model;
  final Value<String> payload;
  final Value<String?> clientId;
  final Value<DateTime> createdAt;
  const SyncQueueCompanion({
    this.id = const Value.absent(),
    this.op = const Value.absent(),
    this.model = const Value.absent(),
    this.payload = const Value.absent(),
    this.clientId = const Value.absent(),
    this.createdAt = const Value.absent(),
  });
  SyncQueueCompanion.insert({
    this.id = const Value.absent(),
    required String op,
    required String model,
    required String payload,
    this.clientId = const Value.absent(),
    this.createdAt = const Value.absent(),
  })  : op = Value(op),
        model = Value(model),
        payload = Value(payload);
  static Insertable<SyncQueueData> custom({
    Expression<int>? id,
    Expression<String>? op,
    Expression<String>? model,
    Expression<String>? payload,
    Expression<String>? clientId,
    Expression<DateTime>? createdAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (op != null) 'op': op,
      if (model != null) 'model': model,
      if (payload != null) 'payload': payload,
      if (clientId != null) 'client_id': clientId,
      if (createdAt != null) 'created_at': createdAt,
    });
  }

  SyncQueueCompanion copyWith(
      {Value<int>? id,
      Value<String>? op,
      Value<String>? model,
      Value<String>? payload,
      Value<String?>? clientId,
      Value<DateTime>? createdAt}) {
    return SyncQueueCompanion(
      id: id ?? this.id,
      op: op ?? this.op,
      model: model ?? this.model,
      payload: payload ?? this.payload,
      clientId: clientId ?? this.clientId,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (op.present) {
      map['op'] = Variable<String>(op.value);
    }
    if (model.present) {
      map['model'] = Variable<String>(model.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('op: $op, ')
          ..write('model: $model, ')
          ..write('payload: $payload, ')
          ..write('clientId: $clientId, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $AnimalsTable animals = $AnimalsTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [animals, syncQueue];
}

typedef $$AnimalsTableCreateCompanionBuilder = AnimalsCompanion Function({
  Value<int> id,
  Value<int?> serverId,
  required int propriedadeId,
  required String brinco,
  Value<String?> raca,
  Value<String?> sexo,
  Value<DateTime?> dataNascimento,
  Value<String?> categoria,
  Value<String?> temperamento,
  Value<String?> aptidao,
  Value<String?> statusReprodutivo,
  Value<bool> isReprodutor,
  Value<String?> caracteristicas,
  Value<int?> paiId,
  Value<int?> maeId,
  Value<String?> fotoPerfil,
  Value<bool> ativo,
  Value<DateTime?> dataNascimentoOriginal,
  Value<DateTime?> updatedAt,
});
typedef $$AnimalsTableUpdateCompanionBuilder = AnimalsCompanion Function({
  Value<int> id,
  Value<int?> serverId,
  Value<int> propriedadeId,
  Value<String> brinco,
  Value<String?> raca,
  Value<String?> sexo,
  Value<DateTime?> dataNascimento,
  Value<String?> categoria,
  Value<String?> temperamento,
  Value<String?> aptidao,
  Value<String?> statusReprodutivo,
  Value<bool> isReprodutor,
  Value<String?> caracteristicas,
  Value<int?> paiId,
  Value<int?> maeId,
  Value<String?> fotoPerfil,
  Value<bool> ativo,
  Value<DateTime?> dataNascimentoOriginal,
  Value<DateTime?> updatedAt,
});

class $$AnimalsTableFilterComposer
    extends Composer<_$AppDatabase, $AnimalsTable> {
  $$AnimalsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get propriedadeId => $composableBuilder(
      column: $table.propriedadeId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get brinco => $composableBuilder(
      column: $table.brinco, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get raca => $composableBuilder(
      column: $table.raca, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get sexo => $composableBuilder(
      column: $table.sexo, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dataNascimento => $composableBuilder(
      column: $table.dataNascimento,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get categoria => $composableBuilder(
      column: $table.categoria, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get temperamento => $composableBuilder(
      column: $table.temperamento, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get aptidao => $composableBuilder(
      column: $table.aptidao, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get statusReprodutivo => $composableBuilder(
      column: $table.statusReprodutivo,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get isReprodutor => $composableBuilder(
      column: $table.isReprodutor, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get caracteristicas => $composableBuilder(
      column: $table.caracteristicas,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get paiId => $composableBuilder(
      column: $table.paiId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get maeId => $composableBuilder(
      column: $table.maeId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get fotoPerfil => $composableBuilder(
      column: $table.fotoPerfil, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get ativo => $composableBuilder(
      column: $table.ativo, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dataNascimentoOriginal => $composableBuilder(
      column: $table.dataNascimentoOriginal,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));
}

class $$AnimalsTableOrderingComposer
    extends Composer<_$AppDatabase, $AnimalsTable> {
  $$AnimalsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get serverId => $composableBuilder(
      column: $table.serverId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get propriedadeId => $composableBuilder(
      column: $table.propriedadeId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get brinco => $composableBuilder(
      column: $table.brinco, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get raca => $composableBuilder(
      column: $table.raca, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get sexo => $composableBuilder(
      column: $table.sexo, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dataNascimento => $composableBuilder(
      column: $table.dataNascimento,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get categoria => $composableBuilder(
      column: $table.categoria, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get temperamento => $composableBuilder(
      column: $table.temperamento,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get aptidao => $composableBuilder(
      column: $table.aptidao, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get statusReprodutivo => $composableBuilder(
      column: $table.statusReprodutivo,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get isReprodutor => $composableBuilder(
      column: $table.isReprodutor,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get caracteristicas => $composableBuilder(
      column: $table.caracteristicas,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get paiId => $composableBuilder(
      column: $table.paiId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get maeId => $composableBuilder(
      column: $table.maeId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get fotoPerfil => $composableBuilder(
      column: $table.fotoPerfil, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get ativo => $composableBuilder(
      column: $table.ativo, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dataNascimentoOriginal => $composableBuilder(
      column: $table.dataNascimentoOriginal,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$AnimalsTableAnnotationComposer
    extends Composer<_$AppDatabase, $AnimalsTable> {
  $$AnimalsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<int> get serverId =>
      $composableBuilder(column: $table.serverId, builder: (column) => column);

  GeneratedColumn<int> get propriedadeId => $composableBuilder(
      column: $table.propriedadeId, builder: (column) => column);

  GeneratedColumn<String> get brinco =>
      $composableBuilder(column: $table.brinco, builder: (column) => column);

  GeneratedColumn<String> get raca =>
      $composableBuilder(column: $table.raca, builder: (column) => column);

  GeneratedColumn<String> get sexo =>
      $composableBuilder(column: $table.sexo, builder: (column) => column);

  GeneratedColumn<DateTime> get dataNascimento => $composableBuilder(
      column: $table.dataNascimento, builder: (column) => column);

  GeneratedColumn<String> get categoria =>
      $composableBuilder(column: $table.categoria, builder: (column) => column);

  GeneratedColumn<String> get temperamento => $composableBuilder(
      column: $table.temperamento, builder: (column) => column);

  GeneratedColumn<String> get aptidao =>
      $composableBuilder(column: $table.aptidao, builder: (column) => column);

  GeneratedColumn<String> get statusReprodutivo => $composableBuilder(
      column: $table.statusReprodutivo, builder: (column) => column);

  GeneratedColumn<bool> get isReprodutor => $composableBuilder(
      column: $table.isReprodutor, builder: (column) => column);

  GeneratedColumn<String> get caracteristicas => $composableBuilder(
      column: $table.caracteristicas, builder: (column) => column);

  GeneratedColumn<int> get paiId =>
      $composableBuilder(column: $table.paiId, builder: (column) => column);

  GeneratedColumn<int> get maeId =>
      $composableBuilder(column: $table.maeId, builder: (column) => column);

  GeneratedColumn<String> get fotoPerfil => $composableBuilder(
      column: $table.fotoPerfil, builder: (column) => column);

  GeneratedColumn<bool> get ativo =>
      $composableBuilder(column: $table.ativo, builder: (column) => column);

  GeneratedColumn<DateTime> get dataNascimentoOriginal => $composableBuilder(
      column: $table.dataNascimentoOriginal, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);
}

class $$AnimalsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $AnimalsTable,
    Animal,
    $$AnimalsTableFilterComposer,
    $$AnimalsTableOrderingComposer,
    $$AnimalsTableAnnotationComposer,
    $$AnimalsTableCreateCompanionBuilder,
    $$AnimalsTableUpdateCompanionBuilder,
    (Animal, BaseReferences<_$AppDatabase, $AnimalsTable, Animal>),
    Animal,
    PrefetchHooks Function()> {
  $$AnimalsTableTableManager(_$AppDatabase db, $AnimalsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$AnimalsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$AnimalsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$AnimalsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<int?> serverId = const Value.absent(),
            Value<int> propriedadeId = const Value.absent(),
            Value<String> brinco = const Value.absent(),
            Value<String?> raca = const Value.absent(),
            Value<String?> sexo = const Value.absent(),
            Value<DateTime?> dataNascimento = const Value.absent(),
            Value<String?> categoria = const Value.absent(),
            Value<String?> temperamento = const Value.absent(),
            Value<String?> aptidao = const Value.absent(),
            Value<String?> statusReprodutivo = const Value.absent(),
            Value<bool> isReprodutor = const Value.absent(),
            Value<String?> caracteristicas = const Value.absent(),
            Value<int?> paiId = const Value.absent(),
            Value<int?> maeId = const Value.absent(),
            Value<String?> fotoPerfil = const Value.absent(),
            Value<bool> ativo = const Value.absent(),
            Value<DateTime?> dataNascimentoOriginal = const Value.absent(),
            Value<DateTime?> updatedAt = const Value.absent(),
          }) =>
              AnimalsCompanion(
            id: id,
            serverId: serverId,
            propriedadeId: propriedadeId,
            brinco: brinco,
            raca: raca,
            sexo: sexo,
            dataNascimento: dataNascimento,
            categoria: categoria,
            temperamento: temperamento,
            aptidao: aptidao,
            statusReprodutivo: statusReprodutivo,
            isReprodutor: isReprodutor,
            caracteristicas: caracteristicas,
            paiId: paiId,
            maeId: maeId,
            fotoPerfil: fotoPerfil,
            ativo: ativo,
            dataNascimentoOriginal: dataNascimentoOriginal,
            updatedAt: updatedAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<int?> serverId = const Value.absent(),
            required int propriedadeId,
            required String brinco,
            Value<String?> raca = const Value.absent(),
            Value<String?> sexo = const Value.absent(),
            Value<DateTime?> dataNascimento = const Value.absent(),
            Value<String?> categoria = const Value.absent(),
            Value<String?> temperamento = const Value.absent(),
            Value<String?> aptidao = const Value.absent(),
            Value<String?> statusReprodutivo = const Value.absent(),
            Value<bool> isReprodutor = const Value.absent(),
            Value<String?> caracteristicas = const Value.absent(),
            Value<int?> paiId = const Value.absent(),
            Value<int?> maeId = const Value.absent(),
            Value<String?> fotoPerfil = const Value.absent(),
            Value<bool> ativo = const Value.absent(),
            Value<DateTime?> dataNascimentoOriginal = const Value.absent(),
            Value<DateTime?> updatedAt = const Value.absent(),
          }) =>
              AnimalsCompanion.insert(
            id: id,
            serverId: serverId,
            propriedadeId: propriedadeId,
            brinco: brinco,
            raca: raca,
            sexo: sexo,
            dataNascimento: dataNascimento,
            categoria: categoria,
            temperamento: temperamento,
            aptidao: aptidao,
            statusReprodutivo: statusReprodutivo,
            isReprodutor: isReprodutor,
            caracteristicas: caracteristicas,
            paiId: paiId,
            maeId: maeId,
            fotoPerfil: fotoPerfil,
            ativo: ativo,
            dataNascimentoOriginal: dataNascimentoOriginal,
            updatedAt: updatedAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$AnimalsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $AnimalsTable,
    Animal,
    $$AnimalsTableFilterComposer,
    $$AnimalsTableOrderingComposer,
    $$AnimalsTableAnnotationComposer,
    $$AnimalsTableCreateCompanionBuilder,
    $$AnimalsTableUpdateCompanionBuilder,
    (Animal, BaseReferences<_$AppDatabase, $AnimalsTable, Animal>),
    Animal,
    PrefetchHooks Function()>;
typedef $$SyncQueueTableCreateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  required String op,
  required String model,
  required String payload,
  Value<String?> clientId,
  Value<DateTime> createdAt,
});
typedef $$SyncQueueTableUpdateCompanionBuilder = SyncQueueCompanion Function({
  Value<int> id,
  Value<String> op,
  Value<String> model,
  Value<String> payload,
  Value<String?> clientId,
  Value<DateTime> createdAt,
});

class $$SyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get op => $composableBuilder(
      column: $table.op, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get model => $composableBuilder(
      column: $table.model, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$SyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get op => $composableBuilder(
      column: $table.op, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get model => $composableBuilder(
      column: $table.model, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$SyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get op =>
      $composableBuilder(column: $table.op, builder: (column) => column);

  GeneratedColumn<String> get model =>
      $composableBuilder(column: $table.model, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$SyncQueueTableTableManager extends RootTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()> {
  $$SyncQueueTableTableManager(_$AppDatabase db, $SyncQueueTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncQueueTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncQueueTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<int> id = const Value.absent(),
            Value<String> op = const Value.absent(),
            Value<String> model = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<String?> clientId = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncQueueCompanion(
            id: id,
            op: op,
            model: model,
            payload: payload,
            clientId: clientId,
            createdAt: createdAt,
          ),
          createCompanionCallback: ({
            Value<int> id = const Value.absent(),
            required String op,
            required String model,
            required String payload,
            Value<String?> clientId = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
          }) =>
              SyncQueueCompanion.insert(
            id: id,
            op: op,
            model: model,
            payload: payload,
            clientId: clientId,
            createdAt: createdAt,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncQueueTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$AnimalsTableTableManager get animals =>
      $$AnimalsTableTableManager(_db, _db.animals);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
}
