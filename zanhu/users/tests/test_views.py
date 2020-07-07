from django.test import RequestFactory
from test_plus.test import TestCase

from zanhu.users.views import UserUpdateView


class BaseUserTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = self.make_user()


class TestUserUpdateView(BaseUserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.view = UserUpdateView()
        request = self.factory.get('/fake-url')
        request.user = self.user
        self.view.request = request #不需要模拟客户端经过中间件和路由，而是直接访问视图

    def test_get_success_url(self):
        self.assertEqual(self.view.get_success_url(),'/users/testuser/')

    def test_get_object(self):
        self.assertEqual(self.view.get_object(),self.user)
