from django.urls import path, include
from rest_framework.routers import DefaultRouter

from home.api.v1.viewsets import (
    SignupViewSet,
    LoginViewSet,
    AppModelViewSet,
    PlanModelViewSet,
    SubscriptionModelViewSet,
)

router = DefaultRouter()
router.register("signup", SignupViewSet, basename="signup")
router.register("login", LoginViewSet, basename="login")
router.register(r"app", AppModelViewSet, basename="app")
router.register(r"plan", PlanModelViewSet, basename="plan")
router.register(r"subscription", SubscriptionModelViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
]
