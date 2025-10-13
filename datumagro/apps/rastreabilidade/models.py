# datumagro/apps/rastreabilidade/models.py

from django.db import models
from django.utils.text import slugify

class PerfilPublicoAnimal(models.Model):
    """
    Controla a página de rastreabilidade pública de um animal,
    acessível via QR Code.
    """
    animal = models.OneToOneField(
        'cadastros.Animal',
        on_delete=models.CASCADE,
        related_name='perfil_publico'
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL única para o perfil do animal.")
    is_publico = models.BooleanField(default=False, help_text="Controla se a página pública está ativa.")
    titulo_perfil = models.CharField(max_length=255, blank=True, help_text="Ex: Conheça o Lote Premium da Fazenda Modelo")
    historia_destacada = models.TextField(blank=True, help_text="Um texto para o consumidor sobre a origem e qualidade do animal.")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    class Meta:
        verbose_name = "Perfil Público do Animal"
        verbose_name_plural = "Perfis Públicos dos Animais"

    def __str__(self):
        return f"Perfil de Rastreabilidade de {self.animal.brinco}"

    def save(self, *args, **kwargs):
        # Gera o slug automaticamente a partir do brinco e id se estiver vazio
        if not self.slug:
            base_slug = slugify(self.animal.brinco)
            self.slug = f"{base_slug}-{self.animal.id}"
        super().save(*args, **kwargs)