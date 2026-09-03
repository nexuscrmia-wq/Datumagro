from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0003_add_tipo_status_categoria_nome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacaofinanceira',
            name='tipo',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('RECEITA', 'Receita'),
                    ('DESPESA', 'Despesa'),
                    ('INICIAL', 'Caixa Inicial'),
                ],
                default='DESPESA',
            ),
        ),
    ]
