from django.db import models


class FileForRecognition(models.Model):
    class Meta:
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'

    file = models.FileField(verbose_name='Загруженный файл',  upload_to='test/', blank=True, null=True)
    date = models.DateField('Дата загрузки', auto_now_add=True)
