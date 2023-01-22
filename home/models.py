from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

DEFAULT_PLANS = [
    {
        "name": "Free",
        "description": "Free Plan",
        "price": "0.00",
    },
    {
        "name": "Standard",
        "description": "Standard Plan",
        "price": "10.00",
    },
    {
        "name": "Pro",
        "description": "Pro Plan",
        "price": "25.00",
    },
]


class TimeTrackedModel(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Created At",
    )

    class Meta:
        abstract = True


class App(TimeTrackedModel):
    TYPE_CHOICES = (
        ("Web", "Web"),
        ("Mobile", "Mobile"),
    )
    FRAMEWORK_CHOICES = (
        ("Django", "Django"),
        ("React Native", "React Native"),
    )

    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text="Name",
    )
    description = models.TextField(
        help_text="Description",
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text="Type",
    )
    framework = models.CharField(
        max_length=50,
        choices=FRAMEWORK_CHOICES,
        help_text="Framework",
    )
    domain_name = models.CharField(
        max_length=50,
        help_text="Domain name",
    )
    screenshot = models.URLField(
        help_text="Screenshot",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        help_text="User",
    )

    @property
    def subscription(self):
        return self.subscription_set.first()


class Plan(TimeTrackedModel):
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text="Name",
    )
    description = models.TextField(
        help_text="Description",
    )
    price = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        help_text="Price",
    )


class Subscription(TimeTrackedModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        help_text="User",
    )
    plan = models.OneToOneField(
        Plan,
        on_delete=models.PROTECT,
        null=False,
        related_name="subscription_plan",
        help_text="Plan",
    )
    app = models.ForeignKey(
        App,
        on_delete=models.SET_NULL,
        null=True,
        help_text="App",
    )
    active = models.BooleanField(
        null=False,
        help_text="Active",
    )
