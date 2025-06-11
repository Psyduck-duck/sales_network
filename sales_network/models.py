from django.db import models
from django.core.exceptions import ValidationError


class NetworkElement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название звена')
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(verbose_name='Страна')
    city = models.CharField(verbose_name='Город')
    street = models.CharField(verbose_name='Улица')
    building = models.CharField(verbose_name='Строение')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
    products = models.ForeignKey('sales_network.Product', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Дата создания')
    debt_to_parent = models.FloatField(round(2), blank=True, null=True, default=0)
    network_lvl = models.IntegerField(blank=True, null=True, default=0)

    def clean(self):
        super().clean()
        if self.parent and self.parent.count() > 1:
            raise ValidationError('У звена может быть только один родительский узел')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название продукта')
    model = models.CharField(blank=True, null=True, verbose_name='Модель продукта')
    release_date = models.DateField(blank=True, null=True, verbose_name='Дата выхода')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
