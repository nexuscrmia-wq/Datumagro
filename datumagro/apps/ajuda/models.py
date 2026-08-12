from django.db import models


class GuiaModulo(models.Model):
    class Especie(models.TextChoices):
        GLOBAL = "GLOBAL", "Todas as Atividades"
        BOVINO_CORTE = "BOVINOS_CORTE", "Bovinos de Corte"
        BOVINO_LEITE = "BOVINOS_LEITE", "Bovinos de Leite"
        SUINO = "SUINOS", "Suinocultura"
        EQUINO = "EQUINOS", "Equinocultura"
        OVINO_CAPRINO = "OVINOS_CAPRINOS", "Ovinos e Caprinos"
        TERRA = "TERRA", "Apenas Terra / Agricultura"

    modulo_slug = models.SlugField(
        max_length=50,
        help_text="Identificador da tela. Ex: mapa, pesagem, sanitario, financeiro",
    )
    titulo = models.CharField(max_length=150)
    especie = models.CharField(
        max_length=20, choices=Especie.choices, default=Especie.GLOBAL
    )
    ordem = models.PositiveSmallIntegerField(default=0)
    como_usar_passo_a_passo = models.TextField()
    dicas_agronomicas_zootecnicas = models.TextField()
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["modulo_slug", "ordem"]
        unique_together = [("modulo_slug", "especie")]
        verbose_name = "Guia de Módulo"
        verbose_name_plural = "Guias de Módulos"

    def __str__(self):
        return f"[{self.especie}] {self.titulo} ({self.modulo_slug})"
