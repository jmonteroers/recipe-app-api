from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    def setUp(self):
        """Sets up test case by creating a Test client, adds and logs in an
        admin user, and adds a regular user"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@montero.es',
            password='password1234'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@montero.es',
            password='password122',
            name='Test user with a long name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        # use client to perform a HTTP GET on our django app
        res = self.client.get(url)

        # these statements also check that response status code is 200
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
