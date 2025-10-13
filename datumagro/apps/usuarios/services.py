# datumagro/apps/usuarios/services.py

from django.db import transaction
from .models import Usuario
from datumagro.apps.cadastros.models import Cliente


@transaction.atomic
def criar_novo_cliente_e_usuario(
        email: str,
        password: str,
        nome_completo: str,
        nome_empresa: str,
        cpf_cnpj: str,
        telefone: str,
) -> Usuario:
    """
    Serviço completo para o registro de um novo cliente.
    Cria o Usuário, o Perfil (via signal), e o Cliente, tudo em uma única transação.
    """
    usuario = Usuario.objects.create_user(
        email=email,
        password=password,
        nome_completo=nome_completo
    )

    perfil = usuario.perfilusuario

    cliente = Cliente.objects.create(
        perfil_usuario=perfil,
        nome_empresa=nome_empresa,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email_contato=email
    )

    perfil.cliente = cliente
    perfil.save()

    return usuario