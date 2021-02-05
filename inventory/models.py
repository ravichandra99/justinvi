from django.db import models
    
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=254, unique=True)
    quantity = models.IntegerField(default=1)
    sgst = models.FloatField(default = 9.0)
    cgst = models.FloatField(default = 9.0)
    cost_price = models.FloatField(blank = True)
    selling_price = models.FloatField(blank = True)
    barcode = models.CharField(max_length = 50,unique = True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
	    return self.name