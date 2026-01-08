from django.db import models
from django.contrib.auth.models import User


# ================== FOOD EMISSION DATASHEET ==================
class FoodEmissionFactor(models.Model):
    food_name = models.CharField(max_length=100, unique=True)
    emission_factor = models.FloatField(help_text="kg CO₂ per kg")

    def __str__(self):
        return self.food_name


# ================== FOOD CONSUMPTION ==================
class FoodConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodEmissionFactor, on_delete=models.CASCADE)
    quantity_kg = models.FloatField()
    carbon_kg = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.food.food_name}"


# ================== ELECTRICITY ==================
class ElectricityUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    units_kwh = models.FloatField()
    carbon_kg = models.FloatField()
    date = models.DateField(auto_now_add=True)


# ================== TRAVEL ==================
class Travel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=50)   # car, bus, train, flight
    distance_km = models.FloatField()
    carbon_kg = models.FloatField()
    date = models.DateField(auto_now_add=True)


# ================== WASTE ==================
class WasteSegregation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity_kg = models.FloatField()
    carbon_kg = models.FloatField()
    date = models.DateField(auto_now_add=True)
