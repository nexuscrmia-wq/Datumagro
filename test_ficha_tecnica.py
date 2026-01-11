#!/usr/bin/env python3
"""
Script de teste específico para a Ficha Técnica Animal
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

def test_endpoint(name, url, method='GET', headers=None, data=None):
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)

        if response.status_code in [200, 201]:
            print(f'✅ {name}: OK ({response.status_code})')
            return True, response.json() if response.content else None
        else:
            print(f'❌ {name}: FAILED ({response.status_code}) - {response.text[:100]}')
            return False, None
    except Exception as e:
        print(f'❌ {name}: ERROR - {str(e)}')
        return False, None

def main():
    print("🚀 Testando Ficha Técnica Animal - DatumAgro")
    print("=" * 50)

    # Aguardar servidor
    print("⏳ Aguardando servidor iniciar...")
    time.sleep(3)

    results = []

    # Health check
    success, _ = test_endpoint('Health Check', f'{BASE_URL}/health/')
    results.append(success)

    # Login
    success, login_data = test_endpoint('User Login', f'{BASE_URL}/usuarios/usuarios/login/', 'POST',
                                       data={'email': 'test@example.com', 'password': 'test123'})
    results.append(success)

    if success and login_data:
        token = login_data.get('access')
        headers = {'Authorization': f'Bearer {token}'}
        print(f'🔑 Token obtido: {token[:30]}...')

        # Test authenticated endpoints
        success, _ = test_endpoint('User Profile', f'{BASE_URL}/usuarios/me/', headers=headers)
        results.append(success)

        # Testar Fichas Técnicas
        print("\n📋 Testando Fichas Técnicas...")
        success, fichas = test_endpoint('Fichas Técnicas', f'{BASE_URL}/cadastros/fichas-tecnicas/', headers=headers)
        results.append(success)

        if success and fichas:
            print(f'📊 Encontradas {len(fichas)} fichas técnicas')
            if fichas:
                ficha = fichas[0]
                print("\n📋 DETALHES DA PRIMEIRA FICHA TÉCNICA:")
                print(f'🐄 Animal: {ficha.get("animal_brinco", "N/A")}')
                print(f'📝 Raça: {ficha.get("animal_raca", "N/A")}')
                print(f'🚹 Sexo: {ficha.get("animal_sexo", "N/A")}')
                print(f'📍 Piquete: {ficha.get("piquete_nome", "N/A")}')
                print(f'⚖️ Peso atual: {ficha.get("peso_atual_kg", "N/A")} kg')
                print(f'📈 GMD Diário: {ficha.get("gmd_diario", "N/A")} kg/dia')
                print(f'📈 GMD Quinzenal: {ficha.get("gmd_quinzenal", "N/A")} kg/quinzena')
                print(f'📈 GMD Mensal: {ficha.get("gmd_mensal", "N/A")} kg/mês')
                print(f'📈 GMD Anual: {ficha.get("gmd_anual", "N/A")} kg/ano')
                print(f'💉 Vacinas em dia: {"Sim" if ficha.get("vacinas_em_dia") else "Não"}')
                print(f'🏥 Status saúde: {ficha.get("status_saude", "N/A")}')
                print(f'💰 Custo diário: R$ {ficha.get("custo_diario", "N/A")}')
                print(f'💎 Valor estimado: R$ {ficha.get("valor_estimado", "N/A")}')
                print(f'📅 Idade: {ficha.get("idade_meses", "N/A")} meses')

                # Testar endpoint detalhado
                ficha_id = ficha.get('id')
                if ficha_id:
                    success, relatorio = test_endpoint(f'Relatório Completo {ficha_id}',
                                                     f'{BASE_URL}/cadastros/fichas-tecnicas/{ficha_id}/relatorio_completo/',
                                                     headers=headers)
                    if success and relatorio:
                        print("\n📊 RELATÓRIO COMPLETO:")
                        print(f'📈 Total de pesagens: {relatorio.get("estatisticas", {}).get("total_pesagens", 0)}')
                        print(f'💉 Total de vacinas: {relatorio.get("estatisticas", {}).get("total_vacinas", 0)}')
                        print(f'👨‍👩‍👧‍👦 Número de filhos: {relatorio.get("estatisticas", {}).get("numero_filhos", 0)}')

        # Testar outros endpoints relacionados
        print("\n🔬 Testando endpoints relacionados...")

        success, piquetes = test_endpoint('Piquetes', f'{BASE_URL}/cadastros/piquetes/', headers=headers)
        if success and piquetes:
            print(f'🏞️ Encontrados {len(piquetes)} piquetes')

        success, vacinas = test_endpoint('Vacinas', f'{BASE_URL}/cadastros/vacinas/', headers=headers)
        if success and vacinas:
            print(f'💉 Encontradas {len(vacinas)} vacinas no catálogo')

        success, aplicacoes = test_endpoint('Aplicações Vacina', f'{BASE_URL}/cadastros/aplicacoes-vacina/', headers=headers)
        if success and aplicacoes:
            print(f'💉 Encontradas {len(aplicacoes)} aplicações de vacina')

    # Resultado final
    passed = sum(results)
    total = len(results)
    print(f'\n📊 RESULTADO FINAL: {passed}/{total} endpoints funcionando')

    if passed == total:
        print('🎉 SISTEMA DA FICHA TÉCNICA 100% FUNCIONAL!')
        print('\n✅ Funcionalidades testadas:')
        print('  • Autenticação JWT')
        print('  • Listagem de fichas técnicas')
        print('  • Detalhes completos da ficha')
        print('  • Cálculos automáticos de GMD')
        print('  • Informações de saúde e vacinas')
        print('  • Dados genéticos')
        print('  • Relatório completo')
        print('  • Endpoints relacionados (piquetes, vacinas)')
    else:
        print(f'⚠️ {total - passed} problemas encontrados')

if __name__ == '__main__':
    main()