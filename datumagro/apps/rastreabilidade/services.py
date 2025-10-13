# datumagro/apps/rastreabilidade/services.py

import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from .models import PerfilPublicoAnimal


def gerar_qr_code_para_perfil(perfil: PerfilPublicoAnimal):
    """
    Gera uma imagem de QR Code para o perfil público e a salva no modelo.
    """
    # Monta a URL completa para o perfil público
    url_publica = reverse('rastreabilidade:perfil-publico-animal', kwargs={'slug': perfil.slug})

    # Configurações do QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_publica)
    qr.make(fit=True)

    # Cria a imagem em memória
    img = qr.make_image(fill_color="black", back_color="white")

    # Salva a imagem em um buffer de bytes
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)

    # Salva o buffer como um arquivo no campo ImageField do modelo
    nome_arquivo = f'qr_code_{perfil.slug}.png'
    perfil.qr_code.save(nome_arquivo, File(buffer), save=True)

    return perfil.qr_code