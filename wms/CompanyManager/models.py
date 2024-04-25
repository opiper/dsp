from django.db import models

class Company(models.Model):
    companyName = models.CharField(max_length=50, blank=False)
    companyCode = models.CharField(max_length=50, blank=False)
    companyAddress = models.CharField(max_length=50, blank=True, null=True)
    directorName = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    weChat = models.CharField(max_length=50, blank=True, null=True)
    phoneNumber = models.IntegerField(blank=True, null=True)
    vatNumber = models.CharField(max_length=50, blank=True, null=True)
    businessLicence = models.ImageField(upload_to='images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        for field_name in ['companyName']:
            val = getattr(self, field_name, False)
            if val:
                val = val.upper().replace(" ", "")
                setattr(self, field_name, val)
        super(Company, self).save(*args, **kwargs)