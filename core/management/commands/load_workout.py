from django.core.management.base import BaseCommand
from core.models import WorkoutType

WORKOUT_TYPES = [
    # --- strength ---
    ("Deadlift", "strength"),
    ("Romanian deadlift", "strength"),
    ("Pull-ups", "strength"),
    ("Lat pulldown", "strength"),
    ("Seated row", "strength"),
    ("Bent-over row", "strength"),
    ("Bench press", "strength"),
    ("Incline bench press", "strength"),
    ("Overhead press", "strength"),
    ("Chest press machine", "strength"),
    ("Chest fly (pec deck)", "strength"),
    ("Reverse fly", "strength"),
    ("Lateral raise", "strength"),
    ("Squat", "strength"),
    ("Leg press", "strength"),
    ("Bulgarian split squat", "strength"),
    ("Hip abduction", "strength"),
    ("Hip adduction", "strength"),
    ("Leg curl", "strength"),
    ("Leg extension", "strength"),
    ("Biceps curl", "strength"),
    ("Triceps extension", "strength"),

    # --- cardio ---
    ("Running", "cardio"),
    ("Treadmill", "cardio"),
    ("Cycling", "cardio"),
    ("Elliptical", "cardio"),
    ("Rowing machine", "cardio"),
    ("Walking", "cardio"),
    ("Jump rope", "cardio"),
    ("Stair climber", "cardio"),
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        for name, exercise_type in WORKOUT_TYPES:
            WorkoutType.objects.update_or_create(
                name=name,
                defaults={"exercise_type": exercise_type},
            )

        self.stdout.write(f"Workout types: {WorkoutType.objects.count()}")