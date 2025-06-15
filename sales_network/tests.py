from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from datetime import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Product, NetworkElement
from users.models import User


class ProductTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', )
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(name='product 1', model='model 1', release_date='2024-12-12')

    def test_product_list(self):
        url = reverse('network:product-list')
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                'id': self.product.pk,
                'name': 'product 1',
                'model': 'model 1',
                'release_date': '2024-12-12'
            }]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data, result)

    def test_product_retrieve(self):
        url = reverse('network:product-detail', args=(self.product.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_create(self):
        url = reverse('network:product-list', )
        data = {'name': 'product 2', 'model': 'model 2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            Product.objects.all().count(), 2
        )

    def test_course_update(self):
        url = reverse('network:product-detail', args=(self.product.pk,))
        data = {'name': 'product 2 new', 'model': 'model 2.1'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.json()['name'], 'product 2 new'
        )

    def test_course_delete(self):
        url = reverse('network:product-detail', args=(self.product.pk,))
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(
            Product.objects.all().count(), 0
        )


class NetworkElementTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', )
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(name='product 1', model='model 1', release_date='2024-12-12')
        self.element = NetworkElement.objects.create(
            name="element 1",
            email="mail1@mail.com",
            country="Russia",
            city="Moscow",
            street="Volodarskogo",
            building="4",
            debt_to_parent=100
        )
        self.element.products.set([self.product.pk])

    def test_element_list(self):
        url = reverse('network:network-list')
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.element.pk,
                "name": "element 1",
                "email": "mail1@mail.com",
                "country": "Russia",
                "city": "Moscow",
                "street": "Volodarskogo",
                "building": "4",
                "created_at": self.element.created_at.isoformat().replace("+00:00", "Z"),
                "debt_to_parent": "100.00",
                "network_lvl": 0,
                "parent": None,
                "products": [
                    self.product.pk
                ]
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(data, result)

    def test_element_retrieve(self):
        url = reverse('network:network-detail', args=(self.element.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_element_create(self):
        # Прописана автоматическая градация уровня сети от родителя
        url = reverse('network:network-list', )
        data = {"name": "element 2",
                "email": "mail2@mail.com",
                "country": "Russia",
                "city": "Moscow",
                "street": "Volodarskogo",
                "building": "5",
                "debt_to_parent": "150.12",
                "parent": self.element.pk,
                "products": [
                    self.product.pk
                ]
                }
        response = self.client.post(url, data, format='json')
        new_element = NetworkElement.objects.get(name='element 2')
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            NetworkElement.objects.all().count(), 2
        )
        self.assertEqual(
            new_element.network_lvl, 1
        )

    def test_element_update(self):
        url = reverse('network:network-detail', args=(self.element.pk,))
        data = {'name': 'element 1 new'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.json()['name'], 'element 1 new'
        )

    def test_element_delete(self):
        url = reverse('network:network-detail', args=(self.element.pk,))
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(
            NetworkElement.objects.all().count(), 0
        )

    def test_element_none_update_debt(self):
        # Хоть статус и 200_OK, но изменения для долга не сохраняются
        url = reverse('network:network-detail', args=(self.element.pk,))
        data = {'debt_to_parent': '123'}
        old_debt = self.element.debt_to_parent
        response = self.client.patch(url, data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            float(response.json()['debt_to_parent']), float(old_debt)
        )


class NetworkElementCleanMethodTests(TestCase):
    def setUp(self):
        # Создаем базовые элементы для тестирования
        self.root = NetworkElement.objects.create(
            name='Root Element',
            email='root@example.com',
            country='Country',
            city='City',
            street='Street',
            building='1'
        )

        self.child1 = NetworkElement.objects.create(
            name='Child 1',
            email='child1@example.com',
            country='Country',
            city='City',
            street='Street',
            building='2',
            parent=self.root
        )

        self.child2 = NetworkElement.objects.create(
            name='Child 2',
            email='child2@example.com',
            country='Country',
            city='City',
            street='Street',
            building='3',
            parent=self.root
        )

    def test_valid_parent_assignment(self):
        """Тест корректного назначения родителя"""
        grandchild = NetworkElement(
            name='Grandchild',
            email='grandchild@example.com',
            country='Country',
            city='City',
            street='Street',
            building='4',
            parent=self.child1
        )

        try:
            grandchild.full_clean()  # Вызывает clean() и другие валидации
        except ValidationError:
            self.fail("Valid parent assignment raised ValidationError unexpectedly")

    def test_self_reference_validation(self):
        """Тест валидации ссылки на самого себя"""
        element = NetworkElement.objects.get(pk=self.root.pk)
        element.parent = element

        with self.assertRaises(ValidationError) as context:
            element.full_clean()

        self.assertIn('Элемент не может быть родителем самому себе', str(context.exception))

    def test_direct_cycle_detection(self):
        """Тест обнаружения прямой циклической ссылки"""
        self.root.parent = self.child1
        with self.assertRaises(ValidationError) as context:
            self.root.full_clean()

        self.assertIn('Обнаружена циклическая ссылка в иерархии', str(context.exception))

    def test_indirect_cycle_detection(self):
        """Тест обнаружения косвенной циклической ссылки"""
        grandchild = NetworkElement.objects.create(
            name='Grandchild',
            email='grandchild@example.com',
            country='Country',
            city='City',
            street='Street',
            building='4',
            parent=self.child1
        )

        # Создаем циклическую ссылку: root -> child1 -> grandchild -> root
        self.root.parent = grandchild

        with self.assertRaises(ValidationError) as context:
            self.root.full_clean()

        self.assertIn('Обнаружена циклическая ссылка в иерархии', str(context.exception))

    def test_network_level_calculation_with_parent(self):
        """Тест вычисления network_lvl при наличии родителя"""
        grandchild = NetworkElement(
            name='Grandchild',
            email='grandchild@example.com',
            country='Country',
            city='City',
            street='Street',
            building='4',
            parent=self.child1
        )
        grandchild.full_clean()
        self.assertEqual(grandchild.network_lvl, 2)

    def test_network_level_calculation_without_parent(self):
        """Тест вычисления network_lvl при отсутствии родителя"""
        new_element = NetworkElement(
            name='New Element',
            email='new@example.com',
            country='Country',
            city='City',
            street='Street',
            building='5'
        )
        new_element.full_clean()
        self.assertEqual(new_element.network_lvl, 0)


class InactiveUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', is_active=False )
        self.client.force_authenticate(user=self.user)


    def test_product_list_inactive_user(self):
        url = reverse('network:product-list', )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_network_list_inactive_user(self):
        url = reverse('network:network-list', )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
