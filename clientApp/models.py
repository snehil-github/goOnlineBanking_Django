from django.db import models


# Create your models here.

# This table contains customer data.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    pwd = models.CharField(max_length=50)
    mno = models.CharField(max_length=10)
    address = models.CharField(max_length=50)
    balance = models.IntegerField(null=True, blank=True)
    accno = models.IntegerField(null=True, blank=True)
    atmno = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "customer_master"


# This table contains record data.
class Record(models.Model):
    objects = None
    cus_id = models.IntegerField()
    status = models.CharField(max_length=50)
    accno = models.IntegerField()
    rdate = models.CharField(max_length=50)
    amount = models.IntegerField(null=True, blank=True)
    bal = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.status

    class Meta:
        db_table = "record_master"
