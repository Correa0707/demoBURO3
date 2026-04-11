from django.test import TestCase
from django.test import TestCase
import datetime
from django.urls import reverse
from django.utils import timezone
from .models import Task, Status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core import mail
from django.contrib.auth.models import User

class AuthViewsTest(TestCase):
    """
    Test cases for authentication views (login and logout).
    """

    def setUp(self):
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": self.password
        })

        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": "wrongpass"
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario o contraseña incorrectos")
        self.assertFalse("_auth_user_id" in self.client.session)

class SendEmailViewTest(TestCase):
    """
    Test cases for SendEmailView.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')


    def test_send_email(self):
        response = self.client.post(
            reverse("send-email"),
            {
                "subject": "Prueba TDD",
                "message": "Este es un mensaje de prueba",
                "recipient": "destinatario@example.com",
            },
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Prueba TDD")
        self.assertEqual(mail.outbox[0].body, "Este es un mensaje de prueba")
        self.assertIn("destinatario@example.com", mail.outbox[0].to)

class DeleteTaskViewTest(TestCase):
    """
    Test cases for delete task view.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.status = Status.objects.create(name="Pendiente")

        self.task = Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status=self.status,
        )

    def test_delete_task(self):
        """
        Test the delete task endpoint.
        """

        response = self.client.post(
            reverse("delete-task", args=[self.task.id])
        )

        self.assertFalse(
            Task.objects.filter(id=self.task.id).exists()
        )

class EditTaskViewTest(TestCase):
    """
    Test cases for edit_tasks view.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.status = Status.objects.create(name="Pendiente")
        
        self.task = Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status=self.status,
        )

    def test_edit_task(self):
        """
        Test the edit_task endpoint.
        """

        response = self.client.post(
            reverse("edit-task", args=[self.task.id]),
            {
                "name": "Aprender TDD - Modificado",
                "description": "Seguir el tutorial paso a paso - Modificado",
                "deadline": "2025-09-16",
                "status": self.status.id,
            },
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Aprender TDD - Modificado")
        self.assertEqual(self.task.description, "Seguir el tutorial paso a paso - Modificado")
        self.assertEqual(self.task.deadline, timezone.make_aware(datetime.datetime(2025, 9, 16)))
class CreateTaskViewTest(TestCase):
    """
    Test cases for task creation using CBV.
    """

    def setUp(self):
        self.status = Status.objects.create(name="Pendiente")
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_create_task(self):
        response = self.client.post(reverse("create-task"), {
            "name": "Aprender TDD",
            "description": "Seguir el tutorial paso a paso",
            "deadline": "2025-09-15",
        })

        task = Task.objects.first()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Aprender TDD")
        self.assertEqual(task.description, "Seguir el tutorial paso a paso")

        expected_date = timezone.make_aware(datetime.datetime(2025, 9, 15))
        self.assertEqual(task.deadline, expected_date)
        self.assertEqual(task.status, self.status)

# Create your tests here.

class ListTasksViewTest(TestCase):
    """
    Test cases for list tasks view.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.status = Status.objects.create(name="Pendiente")

    def test_list_tasks(self):
        """
        Test the list tasks endpoint.
        """

        Task.objects.create(
            name="Aprender TDD",
            description="Seguir el tutorial paso a paso",
            deadline=timezone.make_aware(datetime.datetime(2025, 9, 15)),
            status=self.status,
        )

        response = self.client.get(reverse("list-tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list_tasks.html")

        self.assertContains(response, "Aprender TDD")
        self.assertContains(response, "Seguir el tutorial paso a paso")