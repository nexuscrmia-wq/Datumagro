#!/usr/bin/env python3
"""
Melhorias para os Testes de Fumaça da API DatumAgro

Coloque este arquivo na raiz do projeto e execute com:

  source .venv/bin/activate
  python smoke_tests.py

O script usa chamadas HTTP para http://localhost:8000/api — certifique-se de
que o servidor de desenvolvimento esteja rodando (python manage.py runserver)
em outro terminal.

Gera um relatório JSON em `smoke_tests_report.json` ao final.
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests

BASE_URL = "http://localhost:8000/api"
DEFAULT_TIMEOUT = 6  # segundos
REPORT_FILE = "smoke_tests_report.json"


class SmokeTester:
    def __init__(self):
        self.session = requests.Session()
        # Sessão padrão com JSON
        self.session.headers.update({"Content-Type": "application/json"})
        self.token: Optional[str] = None
        self.user_email: Optional[str] = None
        self.user_password = "testpass123"
        self.user_data: Optional[Dict[str, Any]] = None
        self.propriedade_id: Optional[int] = None
        self.results: Dict[str, Any] = {"runs_at": datetime.utcnow().isoformat()}

    def _log_step(self, name: str):
        print('\n' + '=' * 60)
        print(f"🔍 {name}")
        print('=' * 60)

    def _record(self, test_name: str, ok: bool, detail: Optional[Dict[str, Any]] = None):
        self.results.setdefault('tests', {})[test_name] = {
            'ok': bool(ok),
            'detail': detail or {}
        }

    def test_registro(self) -> bool:
        self._log_step("TESTANDO REGISTRO DE USUÁRIO")

        ts = int(time.time())
        short = uuid.uuid4().hex[:6]
        email = f"smoketest+{ts}-{short}@datumagro.local"
        self.user_email = email
        # marcar um identificador único para toda a execução para evitar conflitos de nomes
        self.run_ts = ts

        payload = {
            "email": email,
            "username": f"smoketest_{ts}",
            "password": self.user_password,
            "password2": self.user_password,
            "first_name": "Smoke",
            "last_name": "Test",
        }

        try:
            r = self.session.post(
                f"{BASE_URL}/usuarios/usuarios/registrar/",
                json=payload,
                timeout=DEFAULT_TIMEOUT,
            )

            if r.status_code in (200, 201):
                data = r.json()
                self.user_data = data.get('user') or data
                self._record('registro', True, {'status_code': r.status_code, 'email': email})
                print(f"✅ Registro bem-sucedido: {email}")
                return True

            # Usuário já existe? tentar login
            if r.status_code == 400:
                try:
                    err = r.json()
                except Exception:
                    err = {'text': r.text}

                self._record('registro', False, {'status_code': r.status_code, 'error': err})
                print(f"⚠️ Registro retornou 400: {err}. Tentando login...")
                # Fallback: tentar login com as credenciais padrão (se existir)
                return False

            self._record('registro', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha no registro: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('registro', False, {'exception': str(exc)})
            print(f"❌ Erro no registro: {exc}")
            return False

    def test_login(self, email: Optional[str] = None) -> bool:
        self._log_step("TESTANDO LOGIN")
        email = email or self.user_email
        if not email:
            self._record('login', False, {'reason': 'no_email'})
            print("❌ Nenhum email disponível para login")
            return False

        payload = {"email": email, "password": self.user_password}

        try:
            r = self.session.post(
                f"{BASE_URL}/usuarios/usuarios/login/",
                json=payload,
                timeout=DEFAULT_TIMEOUT,
            )

            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:
                    data = {}

                # tolerante com diferentes chaves
                token = data.get('access') or data.get('token') or data.get('access_token')
                user = data.get('user') or data

                if token:
                    self.token = token
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    self.user_data = user
                    self._record('login', True, {'status_code': r.status_code})
                    print(f"✅ Login bem-sucedido: {email}")
                    return True

                # Se não veio token, mas status 200, consideramos sucesso parcial
                self._record('login', False, {'status_code': r.status_code, 'body': data})
                print(f"⚠️ Login 200 sem token: {data}")
                return False

            self._record('login', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha no login: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('login', False, {'exception': str(exc)})
            print(f"❌ Erro no login: {exc}")
            return False

    def test_perfil_usuario(self) -> bool:
        self._log_step("TESTANDO RECUPERAÇÃO DE PERFIL")
        try:
            # rota correta para perfil (ver `apps/usuarios/urls.py` -> path('me/', ...))
            r = self.session.get(f"{BASE_URL}/usuarios/me/", timeout=DEFAULT_TIMEOUT)
            if r.status_code == 200:
                try:
                    perfil = r.json()
                except Exception:
                    perfil = {'raw': r.text}
                self._record('perfil', True, {'profile': perfil})
                print(f"✅ Perfil recuperado: {perfil.get('email', perfil)}")
                return True

            self._record('perfil', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha ao recuperar perfil: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('perfil', False, {'exception': str(exc)})
            print(f"❌ Erro ao recuperar perfil: {exc}")
            return False

    def test_criar_propriedade(self) -> bool:
        self._log_step("TESTANDO CRIAÇÃO DE PROPRIEDADE")

        payload = {
            # Campos esperados pelo modelo Propriedade em apps/cadastros.models
            # tornar o nome único por execução (evita UNIQUE constraint para mesmo cliente)
            'nome_propriedade': f'Fazenda Smoke Test {getattr(self, "run_ts", int(time.time()))}',
            'endereco': 'Estrada de Teste, 123',
            'cidade': 'TesteVille',
            'estado': 'SP',
            'cep': '',
            'hectares': 100.0,
        }

        try:
            # endpoint de propriedades está no app `cadastros` (ver `apps/cadastros/urls.py`)
            r = self.session.post(f"{BASE_URL}/cadastros/propriedades/", json=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code in (200, 201):
                try:
                    data = r.json()
                except Exception:
                    data = {}

                # extrair id de forma tolerante
                pid = data.get('id') or data.get('pk') or data.get('propriedade')
                if pid:
                    self.propriedade_id = int(pid)
                self._record('criar_propriedade', True, {'status_code': r.status_code, 'id': pid})
                print(f"✅ Propriedade criada: {data.get('nome', '')} (id={pid})")
                return True

            self._record('criar_propriedade', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha ao criar propriedade: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('criar_propriedade', False, {'exception': str(exc)})
            print(f"❌ Erro ao criar propriedade: {exc}")
            return False

    def test_criar_animal(self) -> bool:
        self._log_step("TESTANDO CRIAÇÃO DE ANIMAL")

        if not self.propriedade_id:
            self._record('criar_animal', False, {'reason': 'no_propriedade_id'})
            print("❌ Não há propriedade_id disponível para criar o animal")
            return False

        payload = {
            # brinco precisa ser único dentro da propriedade; usar timestamp para evitar conflitos
            'brinco': f'SMOKE-{getattr(self, "run_ts", int(time.time()))}-{uuid.uuid4().hex[:4]}',
            'nome': f'Animal Smoke Test {getattr(self, "run_ts", int(time.time()))}',
            'sexo': 'M',
            # usar uma das opções definidas no modelo (ex.: 'NELORE')
            'raca': 'NELORE',
            'aptidao': 'CORTE',
            'data_nascimento': '2020-01-01',
            'propriedade': self.propriedade_id,
        }

        try:
            r = self.session.post(f"{BASE_URL}/cadastros/animais/", json=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code in (200, 201):
                try:
                    data = r.json()
                except Exception:
                    data = {}
                # tentar extrair id do animal criado
                aid = data.get('id') or data.get('pk') or data.get('animal')
                if aid:
                    try:
                        self.animal_id = int(aid)
                    except Exception:
                        self.animal_id = None

                self._record('criar_animal', True, {'status_code': r.status_code, 'brinco': data.get('brinco'), 'id': aid})
                print(f"✅ Animal criado: {data.get('brinco', '')} - {data.get('nome', '')} (id={aid})")
                return True

            self._record('criar_animal', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha ao criar animal: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('criar_animal', False, {'exception': str(exc)})
            print(f"❌ Erro ao criar animal: {exc}")
            return False

    def test_fluxo_reset_senha(self) -> bool:
        self._log_step("TESTANDO FLUXO DE RESET DE SENHA")
        if not self.user_email:
            self._record('reset_senha', False, {'reason': 'no_email'})
            print("❌ Nenhum email disponível para reset de senha")
            return False

        payload = {'email': self.user_email}

        try:
            # rota correta para reset está sob o router 'usuarios' -> /api/usuarios/usuarios/reset_password/
            r = self.session.post(f"{BASE_URL}/usuarios/usuarios/reset_password/", json=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code in (200, 202):
                self._record('reset_senha', True, {'status_code': r.status_code})
                print("✅ Solicitação de reset de senha enviada")
                return True

            # se endpoint não existir, registrar como falha mas não crítico
            if r.status_code == 404:
                self._record('reset_senha', False, {'status_code': 404, 'text': r.text})
                print("⚠️ Endpoint de reset de senha não implementado (404)")
                return False

            self._record('reset_senha', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha na solicitação de reset: {r.status_code} - {r.text}")
            return False

        except requests.RequestException as exc:
            self._record('reset_senha', False, {'exception': str(exc)})
            print(f"❌ Erro no reset de senha: {exc}")
            return False

    def test_financeiro_flow(self) -> bool:
        """Cria uma categoria, cria uma transação e consulta o fluxo de caixa mensal."""
        self._log_step("TESTANDO FLUXO FINANCEIRO")

        # 1) criar categoria
        cat_payload = {
            'nome': f'SMOKE-CAT-{getattr(self, "run_ts", int(time.time()))}',
            'tipo': 'CUSTO',
        }

        try:
            r = self.session.post(f"{BASE_URL}/financeiro/categorias/", json=cat_payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code not in (200, 201):
                self._record('financeiro_categoria', False, {'status_code': r.status_code, 'text': r.text})
                print(f"❌ Falha ao criar categoria: {r.status_code} - {r.text}")
                return False
            cat = r.json()
            cat_id = cat.get('id') or cat.get('pk')
            print(f"✅ Categoria criada: {cat.get('nome')} (id={cat_id})")
            self._record('financeiro_categoria', True, {'id': cat_id})
        except requests.RequestException as exc:
            self._record('financeiro_categoria', False, {'exception': str(exc)})
            print(f"❌ Erro ao criar categoria: {exc}")
            return False

        # 2) criar transacao
        trans_payload = {
            'descricao': 'Compra SMOKE',
            'valor': '123.45',
            'data': datetime.utcnow().date().isoformat(),
            'categoria': cat_id,
        }
        # opcional: linkar a um animal se tivermos um
        if getattr(self, 'animal_id', None):
            trans_payload['animal'] = self.animal_id

        try:
            r = self.session.post(f"{BASE_URL}/financeiro/transacoes/", json=trans_payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code not in (200, 201):
                self._record('financeiro_transacao', False, {'status_code': r.status_code, 'text': r.text})
                print(f"❌ Falha ao criar transacao: {r.status_code} - {r.text}")
                return False
            trans = r.json()
            print(f"✅ Transação criada: {trans.get('descricao')} (id={trans.get('id')})")
            self._record('financeiro_transacao', True, {'id': trans.get('id')})
        except requests.RequestException as exc:
            self._record('financeiro_transacao', False, {'exception': str(exc)})
            print(f"❌ Erro ao criar transacao: {exc}")
            return False

        # 3) consultar fluxo de caixa mensal
        try:
            r = self.session.get(f"{BASE_URL}/financeiro/transacoes/fluxo_caixa_mensal/", timeout=DEFAULT_TIMEOUT)
            if r.status_code == 200:
                try:
                    dados = r.json()
                except Exception:
                    dados = {'raw': r.text}
                self._record('financeiro_fluxo', True, {'data': dados})
                print("✅ Fluxo de caixa mensal consultado")
                return True
            self._record('financeiro_fluxo', False, {'status_code': r.status_code, 'text': r.text})
            print(f"❌ Falha ao consultar fluxo: {r.status_code} - {r.text}")
            return False
        except requests.RequestException as exc:
            self._record('financeiro_fluxo', False, {'exception': str(exc)})
            print(f"❌ Erro ao consultar fluxo: {exc}")
            return False

    def test_inteligencia_alertas(self) -> bool:
        """Consulta alertas da IA e tenta marcar o primeiro como resolvido (se existir)."""
        self._log_step("TESTANDO INTELIGÊNCIA (ALERTAS)")
        try:
            r = self.session.get(f"{BASE_URL}/inteligencia/alertas/", timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:
                self._record('inteligencia_list', False, {'status_code': r.status_code, 'text': r.text})
                print(f"❌ Falha ao listar alertas: {r.status_code} - {r.text}")
                return False

            alerts = r.json()
            self._record('inteligencia_list', True, {'count': len(alerts) if isinstance(alerts, list) else 'unknown'})
            print(f"✅ Listagem de alertas retornou {len(alerts) if isinstance(alerts, list) else 'N/A'} itens")

            # se houver alertas, tentar marcar o primeiro como resolvido
            if isinstance(alerts, list) and alerts:
                first = alerts[0]
                alert_id = first.get('id') or first.get('pk')
                if alert_id:
                    r2 = self.session.post(f"{BASE_URL}/inteligencia/alertas/{alert_id}/marcar_como_resolvido/", timeout=DEFAULT_TIMEOUT)
                    if r2.status_code == 200:
                        self._record('inteligencia_resolver', True, {'id': alert_id})
                        print(f"✅ Alerta {alert_id} marcado como resolvido")
                        return True
                    else:
                        self._record('inteligencia_resolver', False, {'status_code': r2.status_code, 'text': r2.text})
                        print(f"❌ Falha ao marcar alerta: {r2.status_code} - {r2.text}")
                        return False

            # sem alertas: consideramos não-critico, OK
            print("⚠️ Nenhum alerta presente; nada a resolver (skip)")
            return True

        except requests.RequestException as exc:
            self._record('inteligencia_list', False, {'exception': str(exc)})
            print(f"❌ Erro ao consultar alertas: {exc}")
            return False

    def run_all_tests(self) -> bool:
        self._log_step("INICIANDO TESTES DE FUMAÇA DATUMAGRO")

        # sequência prudente: registro -> login -> perfil -> propriedade -> animal -> reset
        all_tests = [
            ('registro', self.test_registro),
            ('login', self.test_login),
            ('perfil', self.test_perfil_usuario),
            ('criar_propriedade', self.test_criar_propriedade),
            ('criar_animal', self.test_criar_animal),
            ('reset_senha', self.test_fluxo_reset_senha),
        ]

        results = []

        # Primeiro registro
        ok = self.test_registro()
        results.append(ok)

        # Tentar login com o email recém-criado; se registro falhar porque o usuário já existe,
        # tentar login com o mesmo email (para evitar falha permanente em ambientes com estado)
        if not ok:
            # se não temos email criado, gera um comportamento de tentativa com email padrão
            if not self.user_email:
                # gerar email com timestamp (fallback)
                ts = int(time.time())
                self.user_email = f"smoketest+{ts}@datumagro.local"

        # login
        ok_login = self.test_login(self.user_email)
        results.append(ok_login)

        # perfil (só se login ok)
        results.append(self.test_perfil_usuario() if ok_login else False)

        # criar propriedade
        results.append(self.test_criar_propriedade() if ok_login else False)

        # criar animal (usa propriedade criada)
        results.append(self.test_criar_animal() if ok_login else False)

        # reset senha
        results.append(self.test_fluxo_reset_senha())

        # financeiro: categoria, transacao e fluxo
        results.append(self.test_financeiro_flow() if ok_login else False)

        # inteligencia: listar alertas e tentar resolver
        results.append(self.test_inteligencia_alertas() if ok_login else False)

        passed = sum(1 for r in results if r)
        total = len(results)

        summary = {
            'passed': passed,
            'total': total,
            'success': passed == total,
        }

        self.results['summary'] = summary

        # gravar relatório completo
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as fh:
                json.dump(self.results, fh, ensure_ascii=False, indent=2)
            print(f"\nRelatório escrito em {REPORT_FILE}")
        except Exception as exc:
            print(f"Falha ao escrever relatório: {exc}")

        print('\n' + '=' * 60)
        print(f"✅ Testes passados: {passed}/{total}")
        print(f"❌ Testes falhados: {total - passed}/{total}")

        if passed == total:
            print("🎉 TODOS OS TESTES DE FUMAÇA PASSARAM!")
            return True
        else:
            print("⚠️  ALGUNS TESTES FALHARAM!")
            return False


def main() -> int:
    tester = SmokeTester()
    ok = tester.run_all_tests()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

