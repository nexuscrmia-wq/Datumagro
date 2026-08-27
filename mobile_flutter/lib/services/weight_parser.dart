class WeightData {
  final double weight;
  final bool isStable;
  final String raw;

  const WeightData({
    required this.weight,
    required this.isStable,
    required this.raw,
  });
}

/// Parser universal para balanças de curral e industriais.
/// Suporta: Tru-Test, Coimma, Toledo, Beckhauser, Datamars e genéricas.
/// Formatos cobertos:
///   "WN 450.5kg\r\n"  — Tru-Test
///   "ST,GS,+00450.50,kg"  — Toledo/Mettler
///   "450.5\r"  — genérica
///   "\x02450.5\x03"  — com STX/ETX
///   " 450,5 kg"  — vírgula decimal
class UniversalWeightParser {
  static final RegExp _weightPattern = RegExp(
    r'[-+]?\s*([0-9]{1,5}[.,][0-9]{1,3}|[0-9]{2,5})',
  );

  static final RegExp _stablePattern = RegExp(
    r'(ST|STABLE|OK|S\b|GS|\x02)',
    caseSensitive: false,
  );

  static WeightData? parse(String rawData) {
    final trimmed = rawData.trim();
    if (trimmed.isEmpty) return null;

    // Remove caracteres de controle exceto usar como indicador de estabilidade
    final isStable = _stablePattern.hasMatch(rawData);
    final normalized = trimmed
        .replaceAll(',', '.')
        .replaceAll(RegExp(r'[\x00-\x1F\x7F]'), ' ')
        .trim();

    final match = _weightPattern.firstMatch(normalized);
    if (match == null) return null;

    final valStr = match.group(1)!.replaceAll(' ', '');
    final weight = double.tryParse(valStr);
    if (weight == null || weight <= 0 || weight > 9999) return null;

    return WeightData(weight: weight, isStable: isStable, raw: rawData);
  }
}
