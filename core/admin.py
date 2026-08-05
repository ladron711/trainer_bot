from django.contrib import admin
from .models import User, BodyMeasurement, WorkoutType, Workout, SetEntry, Product, Meal, MealItem

admin.site.register(User)
admin.site.register(BodyMeasurement)
admin.site.register(WorkoutType)
admin.site.register(Workout)
admin.site.register(SetEntry)
admin.site.register(Product)
admin.site.register(Meal)
admin.site.register(MealItem)

# Register your models here.
