import requests
import uuid
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"
REPORT_PATH = "smoke_verbose_report.json"

session = requests.Session()

report = []

def save_report():
    with open(REPORT_PATH, 'w') as f:
        json.dump(report, f, indent=2, default=str)


def log_step(name, ok, resp=None, exc=None):
    entry = {'name': name, 'ok': ok}
    if resp is not None:
        try:
            entry['status_code'] = resp.status_code
            entry['body'] = resp.text[:4000]
        except Exception as e:
            entry['body'] = str(e)
    if exc is not None:
        entry['exception'] = repr(exc)
    report.append(entry)
    save_report()


# 1) Register
try:
    unique = str(uuid.uuid4())[:8]
    payload = {
        'email': f'test+{unique}@example.com',
        'password': 'Testpass123!',
        'password2': 'Testpass123!',
        'first_name': 'Smoke',
        'last_name': 'Test'
    }
    # registration endpoint is an action on UsuarioViewSet: /usuarios/usuarios/registrar/
    r = session.post(f"{BASE_URL}/usuarios/usuarios/registrar/", json=payload, timeout=10)
    log_step('register', r.status_code in (200, 201), r)
except Exception as e:
    log_step('register', False, exc=e)

# 2) Login
token = None
try:
    payload = {'email': payload['email'], 'password': 'Testpass123!'}
    # login is available at /usuarios/usuarios/login/
    r = session.post(f"{BASE_URL}/usuarios/usuarios/login/", json=payload, timeout=10)
    if r.status_code == 200:
        data = r.json()
        token = data.get('access') or data.get('token') or data.get('access_token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        log_step('login', True, r)
    else:
        log_step('login', False, r)
except Exception as e:
    log_step('login', False, exc=e)

# 3) Profile
try:
    # Perfil exposto em /api/usuarios/me/ (action at app-level)
    r = session.get(f"{BASE_URL}/usuarios/me/")
    log_step('profile', r.status_code == 200, r)
except Exception as e:
    log_step('profile', False, exc=e)

# 3.5) Create Cliente for the user (use API action if available)
try:
    r = session.post(f"{BASE_URL}/usuarios/usuarios/create_cliente/", json={}, timeout=10)
    log_step('create_cliente_action', r.status_code in (200,201), r)
except Exception as e:
    log_step('create_cliente_action', False, exc=e)

# 4) Create category (financeiro)
cat_id = None
try:
    payload = {'nome': f'SmokeCat-{unique}', 'tipo': 'RECEITA'}
    r = session.post(f"{BASE_URL}/financeiro/categorias/", json=payload, timeout=10)
    if r.status_code in (200,201):
        cat_id = r.json().get('id')
    log_step('financeiro_create_categoria', r.status_code in (200,201), r)
except Exception as e:
    log_step('financeiro_create_categoria', False, exc=e)

# 5) Create transacao (financeiro)
trans_id = None
try:
    payload = {
        'descricao': 'Smoke Transacao',
        'valor': '123.45',
        'data': date.today().isoformat(),
        'categoria': cat_id
    }
    r = session.post(f"{BASE_URL}/financeiro/transacoes/", json=payload, timeout=10)
    if r.status_code in (200,201):
        trans_id = r.json().get('id')
    log_step('financeiro_create_transacao', r.status_code in (200,201), r)
except Exception as e:
    log_step('financeiro_create_transacao', False, exc=e)

# 6) Fluxo caixa mensal
try:
    r = session.get(f"{BASE_URL}/financeiro/transacoes/fluxo_caixa_mensal/", timeout=10)
    log_step('financeiro_fluxo_caixa_mensal', r.status_code == 200, r)
except Exception as e:
    log_step('financeiro_fluxo_caixa_mensal', False, exc=e)

# 7) Inteligencia: list alerts
alert_id = None
try:
    r = session.get(f"{BASE_URL}/inteligencia/alertas/", timeout=10)
    ok = r.status_code == 200
    if ok:
        data = r.json()
        # If paginated, get results
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        elif isinstance(data, list):
            results = data
        else:
            results = []
        if results:
            alert_id = results[0].get('id')
    log_step('inteligencia_list_alertas', ok, r)
except Exception as e:
    log_step('inteligencia_list_alertas', False, exc=e)

# 8) Inteligencia: mark as resolved (if any)
if alert_id:
    try:
        r = session.post(f"{BASE_URL}/inteligencia/alertas/{alert_id}/marcar_como_resolvido/", timeout=10)
        log_step('inteligencia_marcar_resolvido', r.status_code in (200,204), r)
    except Exception as e:
        log_step('inteligencia_marcar_resolvido', False, exc=e)
else:
    log_step('inteligencia_marcar_resolvido', True, resp=None)

print("Done. Report saved to", REPORT_PATH)
