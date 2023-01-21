from django.urls import resolve
from django.urls import reverse
from django.test import TestCase

from home.api.v1.viewsets import AppModelViewSet
from home.api.v1.viewsets import PlanModelViewSet
from home.api.v1.viewsets import SubscriptionModelViewSet

URL_LIST = {
    "app_list": {"uri": reverse("app-list"), "view_set": AppModelViewSet},
    "app_detail": {"uri": reverse("app-detail", args=[1]), "view_set": AppModelViewSet},
    "subscription_list": {
        "uri": reverse("subscription-list"),
        "view_set": SubscriptionModelViewSet,
    },
    "subscription_detail": {
        "uri": reverse("subscription-detail", args=[1]),
        "view_set": SubscriptionModelViewSet,
    },
    "plan_list": {"uri": reverse("plan-list"), "view_set": PlanModelViewSet},
    "plan_detail": {
        "uri": reverse("plan-detail", args=[1]),
        "view_set": PlanModelViewSet,
    },
}


class TestURLs(TestCase):
    def test_url_resolve(self):
        for url in URL_LIST.values():
            assert resolve(url["uri"]).func.cls == url["view_set"]
