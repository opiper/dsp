from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from CompanyManager.models import Company


class CustomUser(AbstractUser):
    roleChoices = [
        (1,'Customer'),
        (2, 'Operative'),
        (3, 'Manager')
    ]
    role = models.IntegerField(
        choices=roleChoices,
        blank=True,
        null=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)