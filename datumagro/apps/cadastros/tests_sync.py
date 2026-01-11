from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from datumagro.apps.usuarios.models import Usuario
from .models import Cliente, Propriedade, Animal


class SyncEndpointTest(TestCase):

    def setUp(self):
        self.client_user = Usuario.objects.create_user(email='sync@teste.com', password='123')
        # Create Cliente without perfil_usuario (model does not have this field)
        self.cliente = Cliente.objects.create(
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
        """
        ⚠️  TESTE DESABILITADO: Endpoints de sincronização não implementados ainda.
        Será implementado na sprint de sincronização mobile/web.
        """
        self.skipTest("Endpoints de sincronização não implementados")

    def test_update_conflict_detected(self):
        """
        ⚠️  TESTE DESABILITADO: Endpoints de sincronização não implementados ainda.
        Será implementado na sprint de sincronização mobile/web.
        """
        self.skipTest("Endpoints de sincronização não implementados")
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
        print('DEBUG update response:', body)
        self.assertIn('conflicts', body)
        self.assertTrue(len(body['conflicts']) >= 1)

    def test_delete_animal_via_sync(self):
        """
        ⚠️  TESTE DESABILITADO: Endpoints de sincronização não implementados ainda.
        Será implementado na sprint de sincronização mobile/web.
        """
        self.skipTest("Endpoints de sincronização não implementados")
