from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0003_plano_acesso_importacao_internacional_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plano',
            name='cap_descricao',
            field=models.CharField(
                blank=True, default='', max_length=100,
                help_text='Descrição da capacidade exibida no app. Ex: Até 100 cabeças',
            ),
        ),
        migrations.AddField(
            model_name='plano',
            name='recursos',
            field=models.JSONField(
                blank=True, default=list,
                help_text='Lista de recursos exibidos no app.',
            ),
        ),
        migrations.AddField(
            model_name='plano',
            name='highlight',
            field=models.BooleanField(
                default=False,
                help_text='Exibir em destaque como "Mais popular" no app',
            ),
        ),
        migrations.AddField(
            model_name='plano',
            name='whatsapp_msg',
            field=models.CharField(
                blank=True, default='', max_length=500,
                help_text='Mensagem URL-encoded para WhatsApp ao clicar em Consultar.',
            ),
        ),
    ]
