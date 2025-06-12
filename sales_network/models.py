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
    products = models.ManyToManyField('sales_network.Product', related_name='product')
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='Дата создания')
    debt_to_parent = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True, default=0)
    network_lvl = models.IntegerField(blank=True, null=True, default=0)

    def clean(self):
        super().clean()

        if self.parent:
            if self.parent == self:
                raise ValidationError('Элемент не может быть родителем самому себе')

            parent = self.parent
            while parent is not None:
                if parent == self:
                    raise ValidationError('Обнаружена циклическая ссылка в иерархии')
                parent = parent.parent

        if self.parent:
            self.network_lvl = self.parent.network_lvl + 1
        else:
            self.network_lvl = 0

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Уровень: {self.network_lvl})"

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
