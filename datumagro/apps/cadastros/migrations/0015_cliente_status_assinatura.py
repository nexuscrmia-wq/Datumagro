from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0014_propriedade_camadas_editaveis'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='status_assinatura',
            field=models.CharField(
                choices=[
                    ('PENDENTE', 'Pendente de Aprovação'),
                    ('ATIVO', 'Ativo'),
                    ('BLOQUEADO', 'Bloqueado'),
                ],
                db_index=True,
                default='PENDENTE',
                max_length=10,
                verbose_name='Status de Assinatura',
            ),
        ),
    ]
