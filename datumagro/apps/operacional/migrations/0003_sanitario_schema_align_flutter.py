from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0002_alter_registroreprodutivo_options_and_more'),
        ('cadastros', '0011_onboarding_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ManejoSanitario',
        ),
        migrations.CreateModel(
            name='ManejoSanitario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[
                        ('VACINACAO', 'Vacinação'),
                        ('VERMIFUGACAO', 'Vermifugação'),
                        ('CARRAPATICIDA', 'Carrapaticida'),
                        ('SUPLEMENTACAO', 'Suplementação'),
                        ('OUTRO', 'Outro'),
                    ],
                    default='VACINACAO',
                    max_length=20,
                )),
                ('data', models.DateField()),
                ('descricao', models.CharField(blank=True, max_length=200)),
                ('produto', models.CharField(blank=True, max_length=100)),
                ('dosagem', models.CharField(blank=True, max_length=50)),
                ('via_aplicacao', models.CharField(blank=True, max_length=50)),
                ('profissional', models.CharField(blank=True, max_length=100)),
                ('observacoes', models.TextField(blank=True)),
                ('animal', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='manejos_sanitarios',
                    to='cadastros.animal',
                )),
            ],
            options={
                'ordering': ['-data'],
            },
        ),
    ]
