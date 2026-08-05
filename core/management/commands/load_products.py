from django.core.management.base import BaseCommand
from core.models import Product

PRODUCTS = [
    # name, unit, type, protein, carbs, fats, calories (per 100g)

    # --- meat & fish ---
    ("Chicken (average)", "gram", "meat", 20.0, 0.0, 6.0, 140),
    ("Horse meat", "gram", "meat", 21.0, 0.0, 5.0, 133),
    ("Beef", "gram", "meat", 19.0, 0.0, 12.0, 187),
    ("Fish (average)", "gram", "meat", 20.0, 0.0, 8.0, 155),
    ("Tuna canned in water", "gram", "meat", 24.0, 0.0, 1.0, 110),
    # --- processed meat ---
    ("Boiled sausage (doctorskaya)", "gram", "meat", 12.0, 2.0, 22.0, 257),
    ("Smoked sausage", "gram", "meat", 17.0, 1.0, 40.0, 430),
    ("Ham", "gram", "meat", 16.0, 1.0, 20.0, 250),
    ("Kazy (horse sausage)", "gram", "meat", 12.0, 0.0, 25.0, 280),

    # --- grains & sides ---
    ("Rice cooked", "gram", "grains", 2.7, 28.0, 0.3, 130),
    ("Pasta cooked", "gram", "grains", 5.0, 25.0, 1.1, 131),
    ("Buckwheat cooked", "gram", "grains", 4.5, 21.0, 1.0, 110),
    ("Lentils cooked", "gram", "grains", 9.0, 20.0, 0.4, 116),
    ("Boiled dough (beshbarmak, lasagna)", "gram", "grains", 5.0, 27.0, 1.2, 140),
    ("Potato boiled", "gram", "grains", 2.0, 17.0, 0.1, 77),
    ("Oatmeal dry", "gram", "grains", 12.0, 60.0, 6.0, 350),
    ("Oatmeal cooked on water", "gram", "grains", 2.5, 12.0, 1.2, 70),
    ("Bread", "gram", "grains", 8.0, 49.0, 3.2, 265),

    # --- vegetables ---
    ("Cucumber", "gram", "vegetables", 0.7, 3.6, 0.1, 15),
    ("Tomato", "gram", "vegetables", 0.9, 3.9, 0.2, 18),
    ("Cabbage", "gram", "vegetables", 1.3, 6.0, 0.1, 25),
    ("Greens (average)", "gram", "vegetables", 2.5, 4.0, 0.4, 25),
    ("Bell pepper", "gram", "vegetables", 1.0, 6.0, 0.3, 26),
    ("Onion", "gram", "vegetables", 1.1, 9.3, 0.1, 40),
    ("Carrot", "gram", "vegetables", 0.9, 10.0, 0.2, 41),

    # --- fruits ---
    ("Apple", "gram", "fruits", 0.3, 14.0, 0.2, 52),
    ("Banana", "gram", "fruits", 1.1, 23.0, 0.3, 89),
    ("Watermelon", "gram", "fruits", 0.6, 8.0, 0.2, 30),
    ("Melon", "gram", "fruits", 0.8, 8.0, 0.2, 34),
    ("Citrus (average)", "gram", "fruits", 0.9, 11.0, 0.2, 47),
    ("Pineapple", "gram", "fruits", 0.5, 13.0, 0.1, 50),
    ("Berries (average)", "gram", "fruits", 1.0, 11.0, 0.4, 55),
    ("Mango", "gram", "fruits", 0.8, 15.0, 0.4, 60),
    ("Grapes", "gram", "fruits", 0.7, 17.0, 0.2, 69),
    ("Pomegranate", "gram", "fruits", 1.7, 19.0, 1.2, 83),
    ("Persimmon", "gram", "fruits", 0.6, 18.0, 0.4, 70),

    # --- dairy ---
    ("Milk 2.5%", "gram", "dairy", 2.9, 4.7, 2.5, 52),
    ("Kefir 2.5%", "gram", "dairy", 2.9, 4.0, 2.5, 50),
    ("Ryazhenka 4%", "gram", "dairy", 2.9, 4.2, 4.0, 67),
    ("Yogurt (average)", "gram", "dairy", 5.0, 7.0, 3.0, 75),
    ("Cottage cheese 5%", "gram", "dairy", 17.0, 2.0, 5.0, 121),
    ("Cheese", "gram", "dairy", 25.0, 1.3, 33.0, 402),
    ("Egg (50g each)", "gram", "dairy", 12.6, 0.8, 9.6, 140),

    # --- nuts & dried fruits ---
    ("Peanuts", "gram", "snacks", 26.0, 16.0, 49.0, 567),
    ("Walnuts", "gram", "snacks", 15.0, 14.0, 65.0, 654),
    ("Cashews", "gram", "snacks", 18.0, 30.0, 44.0, 553),
    ("Pistachios", "gram", "snacks", 20.0, 28.0, 45.0, 560),
    ("Raisins", "gram", "snacks", 3.1, 79.0, 0.5, 299),
    ("Dried apricots", "gram", "snacks", 3.4, 63.0, 0.5, 241),
    ("Dried apricots with pit (uryuk)", "gram", "snacks", 3.0, 62.0, 0.5, 235),

    # --- snacks & sweets ---
    ("Milk chocolate", "gram", "snacks", 7.0, 59.0, 30.0, 535),
    ("Potato chips", "gram", "snacks", 6.0, 53.0, 35.0, 545),
    ("Snickers bar", "gram", "snacks", 8.0, 60.0, 24.0, 484),
    ("Muffin", "gram", "snacks", 5.0, 50.0, 18.0, 380),
    ("Cream cake", "gram", "snacks", 4.0, 45.0, 20.0, 380),
    ("Plain cookies", "gram", "snacks", 7.0, 68.0, 15.0, 440),
    ("Chocolate cookies", "gram", "snacks", 6.0, 65.0, 22.0, 480),
    ("Jam", "gram", "snacks", 0.3, 65.0, 0.1, 250),

    # --- fats ---
    ("Vegetable oil", "gram", "other", 0.0, 0.0, 100.0, 884),
    ("Butter", "gram", "other", 0.9, 0.1, 82.0, 717),

    # --- drinks ---
    ("Juice (average)", "gram", "drinks", 0.5, 11.0, 0.1, 46),
    ("Sweet soda", "gram", "drinks", 0.0, 10.5, 0.0, 42),
    ("Whey protein shake in water", "gram", "drinks", 7.5, 1.0, 0.5, 38),
    ("Compote", "gram", "drinks", 0.2, 15.0, 0.0, 60),
    ("Tea with sugar (2 tsp per cup)", "gram", "drinks", 0.0, 4.0, 0.0, 16),
    ("Coffee with milk and sugar", "gram", "drinks", 0.7, 5.0, 0.7, 30),

    # --- other---
    ("Sugar", "gram", "other", 0.0, 100.0, 0.0, 387),
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for name, unit, ptype, protein, carbs, fats, calories in PRODUCTS:
            Product.objects.update_or_create(
                name=name, 
                defaults={
                    "unit": unit,
                    "product_type": ptype,
                    "protein": protein,
                    "carbs": carbs,
                    "fats": fats,
                    "calories": calories,
                },
            )

        self.stdout.write(f"Products: {Product.objects.count()}")