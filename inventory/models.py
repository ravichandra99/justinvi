from django.db import models
from django.contrib.auth.models import User

class SuperMarket(models.Model):
    name = models.CharField(max_length = 100)
    address = models.TextField()
    user = models.ForeignKey(User,on_delete = models.SET_NULL, null = True)


    def __str__(self):
        return self.name
    
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=254)
    super_market = models.ForeignKey(SuperMarket, on_delete = models.SET_NULL, null = True)
    quantity = models.IntegerField(default=1)
    sgst = models.FloatField(default = 9.0)
    cgst = models.FloatField(default = 9.0)
    cost_price = models.FloatField(blank = True)
    selling_price = models.FloatField(blank = True)
    barcode = models.CharField(max_length = 50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
	    return self.name