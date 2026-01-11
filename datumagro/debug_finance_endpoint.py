import requests
import uuid
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"

s = requests.Session()
unique = str(uuid.uuid4())[:8]
reg_payload = {'email': f'test+{unique}@example.com', 'password': 'Testpass123!', 'password2': 'Testpass123!', 'first_name':'D', 'last_name':'T'}
r = s.post(f"{BASE_URL}/usuarios/usuarios/registrar/", json=reg_payload)
print('register', r.status_code)
login_payload = {'email': reg_payload['email'], 'password': reg_payload['password']}
r = s.post(f"{BASE_URL}/usuarios/usuarios/login/", json=login_payload)
print('login', r.status_code, r.text)
if r.status_code==200:
    token = r.json().get('access')
    s.headers.update({'Authorization': f'Bearer {token}'})

# Create a Cliente for this user via debug endpoint (development only)
r_debug = s.post(f"{BASE_URL}/debug/create_cliente/")
print('create_cliente debug status', r_debug.status_code, r_debug.text)

cat_payload = {'nome': f'DebugCat-{unique}', 'tipo':'RECEITA'}
r = s.post(f"{BASE_URL}/financeiro/categorias/", json=cat_payload)
print('post categorias status', r.status_code)
open('finance_categorias_full.html','w').write(r.text)
print('wrote finance_categorias_full.html')

r2 = s.get(f"{BASE_URL}/financeiro/transacoes/fluxo_caixa_mensal/")
print('fluxo status', r2.status_code)
open('finance_fluxo_full.html','w').write(r2.text)
print('wrote finance_fluxo_full.html')

r3 = s.get(f"{BASE_URL}/inteligencia/alertas/")
print('alertas status', r3.status_code)
open('inteligencia_alertas_full.html','w').write(r3.text)
print('wrote inteligencia_alertas_full.html')
