import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from home.models import App
from home.models import Plan
from home.models import Subscription

APPLICATION_JSON = "application/json"

APP_DATA = {
    "name": "botic test",
    "description": "botic test app",
    "type": "Web",
    "framework": "Django",
    "domain_name": "botic.text",
    "screenshot": None,
}

USER_USERNAME = "rafael"
USER_PASS = "user-1-pass"
USER_EMAIL = "rafavolpato@gmail.com"


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = self.create_new_user()
        self.client.login(username=USER_USERNAME, password=USER_PASS)

    @staticmethod
    def create_new_user():
        return get_user_model().objects.create_user(
            username=USER_USERNAME,
            password=USER_PASS,
            email=USER_EMAIL,
            is_superuser=True,
        )

    def delete_json(self, url):
        return self.client.delete(url, content_type=APPLICATION_JSON)

    def put_json(self, url, data):
        return self.client.put(url, json.dumps(data), content_type=APPLICATION_JSON)

    def patch_json(self, url, data):
        return self.client.patch(url, json.dumps(data), content_type=APPLICATION_JSON)

    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type=APPLICATION_JSON)

    def assert_resp(self, resp, status):
        self.assertEqual(resp.status_code, status)

    def assert_json(self, resp, status):
        self.assert_resp(resp, status)
        self.assertEqual(resp["content-type"], APPLICATION_JSON)

    def test_post_app(self):
        url = reverse("app-list")
        resp = self.post_json(url, APP_DATA)
        self.assert_json(resp, 201)

        app = App.objects.filter(**APP_DATA)
        self.assertTrue(len(app))

    def create_app(self):
        return App.objects.create(**APP_DATA, user=self.user)

    @staticmethod
    def get_first_plan():
        return Plan.objects.first()


class TestAppViews(BaseTestCase):
    def test_put_app(self):
        app = self.create_app()
        url = reverse("app-detail", args=(app.id,))
        app_put = {
            "name": "botic test2",
            "description": "botic test app2",
            "type": "Mobile",
            "framework": "React Native",
            "domain_name": "botic.text2",
            "screenshot": "http://test.co",
        }
        resp = self.put_json(url, app_put)
        self.assert_json(resp, 200)

        app = App.objects.get(id=app.id)
        for field, value in app_put.items():
            self.assertEqual(getattr(app, field), value)

    def test_patch_app(self):
        app = self.create_app()
        url = reverse("app-detail", args=(app.id,))
        app_patch = {
            "type": "Mobile",
            "framework": "React Native",
        }
        resp = self.patch_json(url, app_patch)
        self.assert_json(resp, 200)

        app = App.objects.get(id=app.id)
        for field, value in app_patch.items():
            self.assertEqual(getattr(app, field), value)

    def test_delete_app(self):
        app = self.create_app()
        url = reverse("app-detail", args=(app.id,))

        resp = self.delete_json(url)
        self.assert_resp(resp, 204)

        app = App.objects.filter(id=app.id)
        self.assertEqual(len(app), 0)

    def test_list_app(self):
        app = self.create_app()
        url = reverse("app-list")
        resp = self.client.get(url)
        self.assert_json(resp, 200)
        app_found = (row for row in resp.data if row["id"] == app.id)
        self.assertTrue(app_found)

    def test_get_app(self):
        app = self.create_app()
        url = reverse("app-detail", args=(app.id,))
        resp = self.client.get(url)
        self.assert_json(resp, 200)

        for field, value in APP_DATA.items():
            self.assertEqual(getattr(app, field), resp.data[field])


class TestPlanViews(BaseTestCase):
    def test_list_app(self):
        count = Plan.objects.count()
        url = reverse("plan-list")
        resp = self.client.get(url)
        self.assert_json(resp, 200)
        self.assertTrue(count, len(resp.data))

    def test_get_plan(self):
        plan = self.get_first_plan()
        url = reverse("plan-detail", args=(plan.id,))
        resp = self.client.get(url)
        self.assert_json(resp, 200)

        self.assertEqual(plan.name, resp.data["name"])
        self.assertEqual(plan.description, resp.data["description"])
        self.assertEqual(str(plan.price), resp.data["price"])


class TestSubscriptionViews(BaseTestCase):
    def get_subscription_data(self):
        return {
            "plan_id": self.get_first_plan().id,
            "app_id": self.create_app().id,
            "active": True,
        }

    def create_subscription(self):
        return Subscription.objects.create(
            **self.get_subscription_data(), user=self.user
        )

    def test_put_subscription(self):
        subscription = self.create_subscription()
        url = reverse("subscription-detail", args=(subscription.id,))
        subscription_put = {
            "app": subscription.app.id,
            "plan": subscription.plan_id,
            "active": False,
        }
        resp = self.put_json(url, subscription_put)
        self.assert_json(resp, 200)

        subscription = Subscription.objects.get(id=subscription.id)
        self.assertEqual(subscription.app_id, resp.data["app"])
        self.assertEqual(subscription.plan_id, resp.data["plan"])
        self.assertEqual(subscription.active, resp.data["active"])

    def test_patch_subscription(self):
        subscription = self.create_subscription()
        url = reverse("subscription-detail", args=(subscription.id,))
        subscription_patch = {
            "active": False,
        }
        resp = self.patch_json(url, subscription_patch)
        self.assert_json(resp, 200)

        subscription = Subscription.objects.get(id=subscription.id)
        for field, value in subscription_patch.items():
            self.assertEqual(getattr(subscription, field), value)

    def test_list_subscription(self):
        subscription = self.create_subscription()
        url = reverse("subscription-list")
        resp = self.client.get(url)
        self.assert_json(resp, 200)
        subscription_found = (row for row in resp.data if row["id"] == subscription.id)
        self.assertTrue(subscription_found)

    def test_get_subscription(self):
        subscription = self.create_subscription()
        url = reverse("subscription-detail", args=(subscription.id,))
        resp = self.client.get(url)
        self.assert_json(resp, 200)

        self.assertEqual(subscription.app_id, resp.data["app"])
        self.assertEqual(subscription.plan_id, resp.data["plan"])
        self.assertEqual(subscription.active, resp.data["active"])
