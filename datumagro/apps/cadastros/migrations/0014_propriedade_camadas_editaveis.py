from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0013_propriedade_car_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='propriedade',
            name='geojson_piquetes_talhoes',
            field=models.JSONField(
                blank=True, null=True,
                verbose_name='Piquetes / Talhões (GeoJSON)',
                help_text='FeatureCollection de polígonos desenhados pelo usuário',
            ),
        ),
        migrations.AddField(
            model_name='propriedade',
            name='geojson_infraestrutura',
            field=models.JSONField(
                blank=True, null=True,
                verbose_name='Infraestrutura (GeoJSON)',
                help_text='FeatureCollection de pontos: bebedouros, cochos, porteiras etc.',
            ),
        ),
    ]
