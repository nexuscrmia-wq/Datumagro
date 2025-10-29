from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from datumagro.apps.usuarios.models import Usuario
from .models import Cliente, Propriedade, Animal


class SyncEndpointTest(TestCase):

    def setUp(self):
        self.client_user = Usuario.objects.create_user(email='sync@teste.com', password='123')
        # PerfilUsuario created by signal
        self.cliente = Cliente.objects.create(
            perfil_usuario=self.client_user.perfilusuario,
            nome_empresa='Fazenda Sync',
            cpf_cnpj='00011122233344',
            email_contato='contato@sync.com'
        )
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente,
            nome_propriedade='Sync Farm',
            cidade='Teste',
            estado='SP'
        )

        self.api = APIClient()
        self.api.force_authenticate(user=self.client_user)

    def test_create_animal_via_sync(self):
        payload = {
            'last_server_sync': None,
            'changes': [
                {
                    'op': 'create',
                    'model': 'animal',
                    'client_id': 'tmp-1',
                    'data': {
                        'propriedade': self.propriedade.id,
                        'brinco': 'SYNC-001',
                        'raca': 'NELORE',
                        'sexo': 'M',
                        'data_nascimento': '2024-01-01'
                    }
                }
            ]
        }

        resp = self.api.post('/api/cadastros/sync/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn('applied', body)
        applied = body['applied']
        self.assertEqual(len(applied), 1)
        self.assertEqual(applied[0].get('status'), 'ok')
        # check that the animal exists
        self.assertTrue(Animal.objects.filter(brinco='SYNC-001', propriedade=self.propriedade).exists())

    def test_update_conflict_detected(self):
        # create an animal on server
        animal = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='SYNC-002',
            sexo='F',
            raca='ANGUS',
            data_nascimento='2023-01-01'
        )

        # update server-side to have a recent updated_at
        animal.caracteristicas_adicionais = 'server change'
        animal.save()

        # client sends update with an older updated_at -> should be conflict
        client_old_time = (animal.updated_at - timedelta(days=1)).isoformat()
        payload = {
            'last_server_sync': None,
            'changes': [
                {
                    'op': 'update',
                    'model': 'animal',
                    'id': animal.id,
                    'updated_at': client_old_time,
                    'data': {
                        'caracteristicas_adicionais': 'client change'
                    }
                }
            ]
        }

        resp = self.api.post('/api/cadastros/sync/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn('conflicts', body)
        self.assertTrue(len(body['conflicts']) >= 1)

    def test_delete_animal_via_sync(self):
        animal = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='SYNC-003',
            sexo='M',
            raca='NELORE',
            data_nascimento='2022-01-01'
        )

        payload = {
            'last_server_sync': None,
            'changes': [
                {
                    'op': 'delete',
                    'model': 'animal',
                    'id': animal.id,
                }
            ]
        }

        resp = self.api.post('/api/cadastros/sync/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        applied = body.get('applied', [])
        self.assertEqual(applied[0].get('status'), 'ok')
        animal.refresh_from_db()
        self.assertFalse(animal.ativo)
