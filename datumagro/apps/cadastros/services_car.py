"""
Parser de arquivos CAR (KML / GeoJSON) sem dependências GIS externas.

Estratégia:
- KML  → xml.etree.ElementTree  (stdlib)
- GeoJSON → json (stdlib)
- Área → fórmula Shoelace esférica (aproximação geodésica suficiente para ha)

Não realiza nenhuma chamada ao SInCAR/Gov.br — o arquivo é fornecido
pelo próprio produtor após download no portal oficial.
"""

import json
import math
import xml.etree.ElementTree as ET


# ── Área geodésica ────────────────────────────────────────────────────────────

def _area_ha(coords: list[list[float]]) -> float:
    """
    Spherical Shoelace: área de um polígono geodésico em hectares.
    coords: lista de [lon, lat] em graus decimais.
    """
    if len(coords) < 3:
        return 0.0
    R = 6_371_000.0  # raio terrestre em metros
    n = len(coords)
    total = 0.0
    for i in range(n):
        j = (i + 1) % n
        lon1, lat1 = math.radians(coords[i][0]), math.radians(coords[i][1])
        lon2, lat2 = math.radians(coords[j][0]), math.radians(coords[j][1])
        total += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
    return round(abs(total) * R * R / 2 / 10_000, 2)  # m² → ha


# ── Helpers ───────────────────────────────────────────────────────────────────

def _polygon_geometry(outer: list, holes: list | None = None) -> dict:
    return {'type': 'Polygon', 'coordinates': [outer] + (holes or [])}


def _feature(name: str, area_ha: float, geometry: dict) -> dict:
    return {
        'type': 'Feature',
        'properties': {'name': name, 'area_ha': area_ha},
        'geometry': geometry,
    }


# ── KML ───────────────────────────────────────────────────────────────────────

def _parse_coords_text(text: str) -> list[list[float]]:
    ring = []
    for triplet in (text or '').split():
        parts = triplet.split(',')
        if len(parts) >= 2:
            try:
                ring.append([float(parts[0]), float(parts[1])])
            except ValueError:
                pass
    return ring


def parse_kml(content: bytes) -> dict:
    """
    Parseia KML e retorna:
      geojson       → FeatureCollection pronto para salvar no banco
      area_total_ha → soma das áreas de todos os polígonos
      placemarks    → lista de {name, area_ha, geometry}
    Lança ValueError se o arquivo não for válido ou não tiver polígonos.
    """
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError(f'KML inválido: {exc}') from exc

    # Detecta namespace (pode variar entre versões do KML)
    tag = root.tag
    ns = tag[:tag.index('}') + 1] if tag.startswith('{') else ''

    def q(name):
        return f'{ns}{name}'

    placemarks = []
    for pm in root.iter(q('Placemark')):
        name = (pm.findtext(q('name')) or 'Área CAR').strip()

        # Tenta localizar coordenadas do anel externo
        outer_el = pm.find(f'.//{q("outerBoundaryIs")}/{q("LinearRing")}/{q("coordinates")}')
        if outer_el is None:
            outer_el = pm.find(f'.//{q("coordinates")}')
        if outer_el is None or not outer_el.text:
            continue

        outer = _parse_coords_text(outer_el.text)
        if len(outer) < 3:
            continue

        holes = [
            _parse_coords_text(el.text)
            for el in pm.findall(f'.//{q("innerBoundaryIs")}/{q("LinearRing")}/{q("coordinates")}')
            if el.text and len(_parse_coords_text(el.text)) >= 3
        ]

        geom = _polygon_geometry(outer, holes)
        placemarks.append({'name': name, 'area_ha': _area_ha(outer), 'geometry': geom})

    if not placemarks:
        raise ValueError('Nenhum polígono encontrado no KML.')

    return {
        'geojson': {'type': 'FeatureCollection',
                    'features': [_feature(p['name'], p['area_ha'], p['geometry']) for p in placemarks]},
        'area_total_ha': round(sum(p['area_ha'] for p in placemarks), 2),
        'placemarks': placemarks,
    }


# ── GeoJSON ───────────────────────────────────────────────────────────────────

def _extract_polygons(geom: dict, props: dict, out: list) -> None:
    gtype = (geom or {}).get('type', '')
    rings_list = []
    if gtype == 'Polygon':
        rings_list = [geom.get('coordinates', [])]
    elif gtype == 'MultiPolygon':
        rings_list = geom.get('coordinates', [])
    for rings in rings_list:
        outer = rings[0] if rings else []
        if len(outer) < 3:
            continue
        holes = rings[1:]
        geom_out = _polygon_geometry(outer, holes)
        name = props.get('name') or props.get('nome') or 'Área CAR'
        out.append({'name': name, 'area_ha': _area_ha(outer), 'geometry': geom_out})


def parse_geojson(content: bytes) -> dict:
    """
    Parseia GeoJSON e retorna a mesma estrutura que parse_kml.
    Suporta FeatureCollection, Feature, Polygon e MultiPolygon.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f'GeoJSON inválido: {exc}') from exc

    placemarks: list[dict] = []
    dtype = data.get('type', '')

    if dtype == 'FeatureCollection':
        for feat in data.get('features', []):
            _extract_polygons(feat.get('geometry'), feat.get('properties') or {}, placemarks)
    elif dtype == 'Feature':
        _extract_polygons(data.get('geometry'), data.get('properties') or {}, placemarks)
    elif dtype in ('Polygon', 'MultiPolygon'):
        _extract_polygons(data, {}, placemarks)

    if not placemarks:
        raise ValueError('Nenhum polígono encontrado no GeoJSON.')

    return {
        'geojson': {'type': 'FeatureCollection',
                    'features': [_feature(p['name'], p['area_ha'], p['geometry']) for p in placemarks]},
        'area_total_ha': round(sum(p['area_ha'] for p in placemarks), 2),
        'placemarks': placemarks,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_car_file(filename: str, content: bytes) -> dict:
    """
    Detecta o formato pelo nome do arquivo e parseia.
    Aceita: .kml, .geojson, .json
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext == 'kml':
        return parse_kml(content)
    if ext in ('geojson', 'json'):
        return parse_geojson(content)
    raise ValueError(f'Formato não suportado: ".{ext}". Use .kml ou .geojson')
