from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('public', '0006_menu_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='permisosmenuacciones',
            name='grupo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='menu_permiso_grupo',
                to='auth.group'
            ),
        ),
    ]
