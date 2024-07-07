# Generated by Django 4.2.7 on 2024-02-17 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_remove_client_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrateur',
            name='Email',
            field=models.EmailField(default='email@gmail.com', max_length=254),
        ),
        migrations.AlterField(
            model_name='administrateur',
            name='Numero_tel',
            field=models.CharField(default='0710069551', max_length=45),
        ),
        migrations.AlterField(
            model_name='client',
            name='Email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='client',
            name='Numero_tel',
            field=models.CharField(default='', max_length=45),
        ),
    ]
