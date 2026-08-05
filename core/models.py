from django.db import models
from django.utils import timezone


# Create your models here.
class User(models.Model):
    GENDER_TYPE = [
        ("m", "M"),
        ("f", "F"),
    ]

    ACTIVITY = [
        ("under_three", "under_three"),
        ("three", "three"),
        ("more_three", "more_three"),
    ]

    TRAININGS_GOAL = [
        ("weight_loss", "weight_loss"),
        ("muscle_gain", "muscle_gain"),
        ("physical_health", "physical_health"),
    ]

    user_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_TYPE, null=True)
    height = models.FloatField(blank=True, null=True)
    start_weight = models.FloatField(blank=True, null=True)
    birth_day = models.DateField(null=True, blank=True)
    activity = models.CharField(max_length=20, choices=ACTIVITY, null=True)
    goal = models.CharField(max_length=20, choices=TRAININGS_GOAL, default="physical_health")

    daily_calories_goal = models.SmallIntegerField(blank=True, null=True)
    daily_protein_goal = models.SmallIntegerField(null=True, blank=True)
    daily_fats_goal = models.SmallIntegerField(null=True, blank=True)
    daily_carbs_goal = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.daily_calories_goal}"


class BodyMeasurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    weight = models.FloatField(null=True, blank=True) 

    neck = models.FloatField(null=True, blank=True)
    shoulders = models.FloatField(null=True, blank=True)
    chest = models.FloatField(null=True, blank=True)
    bicep = models.FloatField(null=True, blank=True)
    forearm = models.FloatField(null=True, blank=True)
    wrist = models.FloatField(null=True, blank=True)
    waist = models.FloatField(null=True, blank=True)
    hips = models.FloatField(null=True, blank=True)
    thigh = models.FloatField(null=True, blank=True)
    shin = models.FloatField(null=True, blank=True)

    class Meta:
            ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date}"


class WorkoutType(models.Model):
    TYPE_CHOICES = [
        ("cardio", "Cardio"),
        ("strength", "Strength"),
    ]

    name = models.CharField(max_length=20)
    exercise_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="strength") 

    def __str__(self):
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user} - {self.date}"


class SetEntry(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise_type = models.ForeignKey(WorkoutType, on_delete=models.CASCADE)
    reps = models.PositiveSmallIntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    minutes = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.exercise_type} - {self.weight or self.minutes}"


class Product(models.Model):
    UNIT_CHOICES = [
        ("gram", "Gram"),
        ("pcs", "PCS"),  
    ]

    PRODUCT_TYPE = [
        ("grains", "Grains"),
        ("meat", "Meat & Fish"),
        ("dairy", "Dairy"),
        ("vegetables", "Vegetables"),
        ("fruits", "Fruits"),
        ("dishes", "Dishes"),
        ("drinks", "Drinks"),
        ("snacks", "Snacks"),
        ("other", "Other"),
    ]
        
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="gram")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE, null=True)
    is_custom = models.BooleanField(default=False)

    protein = models.FloatField(blank=True, null=True)
    carbs = models.FloatField(blank=True, null=True)
    fats = models.FloatField(blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    total_calories = models.FloatField(blank=True, null=True)
    total_protein = models.FloatField(blank=True, null=True)
    total_carbs = models.FloatField(blank=True, null=True)
    total_fats = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.date} - {self.total_calories}" 


class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.meal} - {self.amount}"