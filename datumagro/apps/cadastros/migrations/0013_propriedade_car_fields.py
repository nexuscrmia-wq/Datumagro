from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0012_add_tipo_especie_to_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='propriedade',
            name='codigo_car',
            field=models.CharField(
                blank=True, max_length=80, verbose_name='Código CAR',
                help_text='Ex: BR-RJ-330100-9AB12345.678901234567-2024.09.17',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='arquivo_car',
            field=models.FileField(
                blank=True, null=True, upload_to='car/', verbose_name='Arquivo CAR',
                help_text='Arquivo .kml ou .geojson baixado do SInCAR',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='geojson_car',
            field=models.JSONField(
                blank=True, null=True, verbose_name='GeoJSON CAR',
                help_text='FeatureCollection extraído do arquivo CAR',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='area_total_ha',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Área Total CAR (ha)',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='area_reserva_legal_ha',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Reserva Legal (ha)',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='area_app_ha',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='APP (ha)',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='area_util_ha',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Área Útil (ha)',
            ),
        ),
    ]
