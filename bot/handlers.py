from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from datetime import date, datetime

from core.models import User, BodyMeasurement, WorkoutType, Workout, SetEntry, Product, Meal, MealItem
from bot.states import AddUser, AddBodyMeasurement, AddWorkout, AddMeals
from core.meal_nutrition import daily_macros_goal, daily_total, format_total
from core.llm_report import generate_report


router = Router()

#------user registration and mealsmacros collection

def reply_kb(*rows):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=True, 
        one_time_keyboard=True,
    )

GENDER_KB = reply_kb(["Male", "Female"])
ACTIVITY_KB = reply_kb(["Less than 3"], ["3 times"], ["More than 3"])
GOAL_KB = reply_kb(["Weight loss"], ["Muscle gain"], ["Health"])


GENDER_MAP = {"Male": "m", "Female": "f"}

ACTIVITY_MAP = {
    "Less than 3": "under_three",
    "3 times": "three",
    "More than 3": "more_three",
}

GOAL_MAP = {
    "Weight loss": "weight_loss",
    "Muscle gain": "muscle_gain",
    "Health": "physical_health",
}

USER_FIELDS = [
    ("gender", "Your gender?", GENDER_KB),
    ("birth_day", "Your birth date in format YYYY-MM-DD", ReplyKeyboardRemove()),
    ("height", "Your height in cm", ReplyKeyboardRemove()),
    ("start_weight", "Your weight in kg", ReplyKeyboardRemove()),
    ("activity", "How many strength or cardio workout per week?", ACTIVITY_KB),
    ("goal", "Your goal", GOAL_KB),
]


def parse_value(field, text):
    if field == "gender":
        return GENDER_MAP.get(text)

    if field == "activity":
        return ACTIVITY_MAP.get(text)

    if field == "goal":
        return GOAL_MAP.get(text)

    if field == "birth_day":
        try:
            value = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            return None
        today = date.today()
        age = today.year - value.year
        return value if 10 < age < 100 else None 

    if field in ("height", "start_weight"):
        try:
            value = float(text.replace(",", "."))
        except ValueError:
            return None
        return value if 0 < value < 300 else None

    return None


@sync_to_async
def user_exists(user_id):
    return User.objects.filter(user_id=user_id).exists()


@sync_to_async
def create_user(user_id, name, values):
    user = User.objects.create(
        user_id=user_id,
        name=name,
        **values,
    )

    macros = daily_macros_goal(user, values["start_weight"])
    user.daily_calories_goal = macros["calories"]
    user.daily_protein_goal = macros["protein"]
    user.daily_fats_goal = macros["fats"]
    user.daily_carbs_goal = macros["carbs"]
    user.save()

    BodyMeasurement.objects.create(user=user, weight=values["start_weight"])
    return user


def get_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ New Log", callback_data="new_log")
    return kb.as_markup()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Canceled", reply_markup=get_main_keyboard())
    await callback.answer()


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Nothing to cancel")
        return

    await state.clear()

    if await user_exists(message.from_user.id):
        await message.answer("Canceled", reply_markup=get_main_keyboard())
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="New User", callback_data="new_user")
    await message.answer("Registration canceled. You need to register first", reply_markup=kb.as_markup())


@router.message(CommandStart())
async def start_command(message: Message):
    if await user_exists(message.from_user.id):
        await message.answer("Glad to see you again. To add new record press ➕", reply_markup=get_main_keyboard())
        return
        
    kb = InlineKeyboardBuilder()
    kb.button(text="New User", callback_data="new_user")
    await message.answer("Welcome to TRAINING_HELPER. If you want to start with it, press button 'New User'", reply_markup=kb.as_markup())
 

@router.callback_query(F.data == "new_user")
async def registration_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddUser.waiting_for_userdata)
    await state.update_data(index=0, values={})

    _, question, keyboard = USER_FIELDS[0]
    await callback.message.answer(question, reply_markup=keyboard)
    await callback.answer()


@router.message(AddUser.waiting_for_userdata)
async def process_userdata(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data["index"]
    values = data["values"]

    field, question, keyboard = USER_FIELDS[index]

    if not message.text:
        await message.answer(f"Send a text. \n{question}", reply_markup=keyboard)
        return

    parsed = parse_value(field, message.text)
    if parsed is None:
        await message.answer(f"Invalid value. \n{question}", reply_markup=keyboard)
        return
    
    values[field] = parsed
    index += 1

    if index < len(USER_FIELDS):
        await state.update_data(index=index, values=values)
        _, next_question, next_keyboard = USER_FIELDS[index]
        await message.answer(next_question, reply_markup=next_keyboard)
        return

    user = await create_user(message.from_user.id, message.from_user.first_name, values)
    await state.clear()

    await message.answer(
        f"Registration complete.\n\n"
        f"Calories: {int(user.daily_calories_goal)} kcal\n"
        f"Protein: {int(user.daily_protein_goal)} g\n"
        f"Fats: {int(user.daily_fats_goal)} g\n"
        f"Carbs: {int(user.daily_carbs_goal)} g",
        reply_markup=get_main_keyboard(),
    )

#------record of body measurements
MEASUREMENT_FIELDS = [
    ("weight", "Weight, kg"),
    ("neck", "Neck, cm"),
    ("shoulders", "Shoulders, cm"),
    ("chest", "Chest, cm"),
    ("bicep", "Bicep, cm"),
    ("forearm", "Forearm, cm"),
    ("wrist", "Wrist, cm"),
    ("waist", "Waist, cm"),
    ("hips", "Hips, cm"),
    ("thigh", "Thigh, cm"),
    ("shin", "Shin, cm"),
]

MEASUREMENT_LABELS = dict(MEASUREMENT_FIELDS)

def measurement_kb():
    kb = InlineKeyboardBuilder()
    for field, label in MEASUREMENT_FIELDS:
        kb.button(text=label, callback_data=f"m_{field}")
    kb.button(text="Done", callback_data="m_done")
    kb.button(text="Cancel", callback_data="cancel")
    kb.adjust(2)
    return kb.as_markup()


@sync_to_async
def save_measurement(user_id, field, value):
    user = User.objects.get(user_id=user_id)
    measurement, _ = BodyMeasurement.objects.get_or_create(user=user, date=date.today())
    setattr(measurement, field, value)
    measurement.save()


@router.callback_query(F.data == "new_log")
async def new_log(callback: CallbackQuery):
    if not await user_exists(callback.from_user.id):
        kb = InlineKeyboardBuilder()
        kb.button(text="New User", callback_data="new_user")
        await callback.message.answer("You need to register first", reply_markup=kb.as_markup())
        await callback.answer()
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="Body Measurement", callback_data="log_body_measurement")
    kb.button(text="Workout", callback_data="log_workout")
    kb.button(text="Meal", callback_data="log_meal")
    kb.button(text="Cancel", callback_data="cancel")
    kb.adjust(2)

    await callback.message.edit_text("Choose log type:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "log_body_measurement")
async def start_measurement(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddBodyMeasurement.waiting_for_measurement)
    await callback.message.answer("What do you want to record?", reply_markup=measurement_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("m_"), AddBodyMeasurement.waiting_for_measurement)
async def pick_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.removeprefix("m_")

    if field == "done":
        await state.clear()
        await callback.message.answer("Saved", reply_markup=get_main_keyboard())
        await callback.answer()
        return

    label = MEASUREMENT_LABELS[field]
    await state.update_data(field=field)
    await callback.message.answer(f"Enter {label}", reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@router.message(AddBodyMeasurement.waiting_for_measurement)
async def save_values(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")

    if field is None:
        await message.answer("Pick a field first", reply_markup=measurement_kb())
        return

    if not message.text:
        await message.answer("Send a text.")
        return 

    try:
        value = float(message.text.replace(",", "."))
        
    except ValueError:
        await message.answer("Invalid value. Please enter a number.")
        return

    if not 0 < value < 300:
        await message.answer("Invalid value")
        return

    await save_measurement(message.from_user.id, field, value)
    await state.update_data(field=None) 
    await message.answer("Saved. Anything else?", reply_markup=measurement_kb())


# ----- meal logging-------

@sync_to_async
def create_meal(user_id):
    user = User.objects.get(user_id=user_id)
    meal = Meal.objects.create(user=user)
    return meal.id

@sync_to_async
def search_products(query):
    return list(Product.objects.filter(name__icontains=query)[:10])


@sync_to_async
def add_meal_item(meal_id, product_id, amount):
    meal = Meal.objects.get(id=meal_id)
    product = Product.objects.get(id=product_id)

    MealItem.objects.create(meal=meal, product=product, amount=amount)

    meal.total_calories = 0
    meal.total_protein = 0
    meal.total_fats = 0 
    meal.total_carbs = 0

    for item in meal.mealitem_set.select_related("product"):
        k = item.amount / 100
        meal.total_calories += item.product.calories * k
        meal.total_protein += item.product.protein * k
        meal.total_fats += item.product.fats * k
        meal.total_carbs += item.product.carbs * k

    meal.save()
    return meal


@sync_to_async
def get_daily_summary(user_id):
    user = User.objects.get(user_id=user_id)
    return {
        "calories": daily_total(user, "calories"),
        "protein": daily_total(user, "protein"),
        "fats": daily_total(user, "fats"),
        "carbs": daily_total(user, "carbs"),
    }


@router.callback_query(F.data == "log_meal")
async def start_meal(callback: CallbackQuery, state: FSMContext):
    meal_id = await create_meal(callback.from_user.id)
    await state.set_state(AddMeals.waiting_for_product)
    await state.update_data(meal_id=meal_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data="cancel")

    await callback.message.answer("Enter product name", reply_markup=kb.as_markup())
    await callback.answer()


@router.message(AddMeals.waiting_for_product)
async def search_product(message: Message, state: FSMContext):

    if not message.text:
        await message.answer("Enter a product with text")
        return

    products = await search_products(message.text)
    if not products:
        await message.answer("No products found. Try again or cancel with /cancel")
        return

    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(text=product.name, callback_data=f"p_{product.id}")
    kb.button(text="Cancel", callback_data="cancel")

    await message.answer("Select a product", reply_markup=kb.as_markup())


@router.callback_query(AddMeals.waiting_for_product, F.data.startswith("p_"))
async def pick_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.removeprefix("p_"))
    await state.set_state(AddMeals.waiting_for_amount)
    await state.update_data(product_id=product_id)

    await callback.message.answer("Enter amount in grams")
    await callback.answer()


@router.message(AddMeals.waiting_for_amount)
async def enter_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    meal_id = data.get("meal_id")
    product_id = data.get("product_id")

    if not message.text:
        await message.answer("Enter a number")
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Invalid value. Enter a number")
        return

    if not 0 < amount < 10000:
        await message.answer("Invalid value. Enter a correct number")
        return

    meal = await add_meal_item(meal_id, product_id, amount)

    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data="cancel")
    kb.button(text="Done", callback_data="meal_done")
    kb.adjust(2)

    await state.set_state(AddMeals.waiting_for_product)
    await message.answer(
        f"Added. Meal total: {int(meal.total_calories)} kcal\n" 
        f"Protein: {int(meal.total_protein)} g \n"
        f"Fats: {int(meal.total_fats)} g \n"
        f"Carbs: {int(meal.total_carbs)} g \n"
        f"Enter another product or press Done.",
        reply_markup=kb.as_markup()
    )
    

@router.callback_query(F.data ==  "meal_done", AddMeals.waiting_for_product)
async def finish_meal(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    summary = await get_daily_summary(callback.from_user.id)
    await callback.message.answer(
        f"Meal logged. Daily summary:\n"
        f"Calories: {format_total(summary['calories'], ' kcal')}\n"
        f"Protein: {format_total(summary['protein'])}\n"
        f"Fats: {format_total(summary['fats'])}\n"
        f"Carbs: {format_total(summary['carbs'])}",
        reply_markup=get_main_keyboard()
    )

#-----  workout logging -----
@sync_to_async
def create_workout(user_id):
    user = User.objects.get(user_id=user_id)
    workout = Workout.objects.create(user=user)
    return workout.id

@sync_to_async
def get_workout_types(query):
    return list(WorkoutType.objects.filter(name__icontains=query)[:10])

@sync_to_async
def add_exercise_entry(workout_id, type_id, reps=None, weight=None, minutes=None):
    workout = Workout.objects.get(id=workout_id)
    exercise_type = WorkoutType.objects.get(id=type_id)

    SetEntry.objects.create(
        workout=workout,
        exercise_type=exercise_type,
        reps=reps,
        weight=weight,
        minutes=minutes
    )

@sync_to_async
def is_cardio(type_id):
    return WorkoutType.objects.get(id=type_id).exercise_type == "cardio"

@router.callback_query(F.data == "log_workout")
async def start_workout(callback: CallbackQuery, state: FSMContext):
    workout_id = await create_workout(callback.from_user.id)
    await state.set_state(AddWorkout.waiting_for_exercise)
    await state.update_data(workout_id=workout_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data="cancel")

    await callback.message.answer("Enter exercise name or cancel", reply_markup=kb.as_markup())
    await callback.answer()


@router.message(AddWorkout.waiting_for_exercise)
async def exercise_search(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Enter a text")
        return

    workout_types = await get_workout_types(message.text)
    if not workout_types:
        await message.answer("No exercises found. Try again or cancel")
        return
 
    kb = InlineKeyboardBuilder()
    for workout_type in workout_types:
        kb.button(text=workout_type.name, callback_data=f"t_{workout_type.id}")
    kb.button(text="Cancel", callback_data="cancel")
    kb.adjust(2)

    await message.answer("Select an exercise", reply_markup=kb.as_markup())


@router.callback_query(AddWorkout.waiting_for_exercise, F.data.startswith("t_"))
async def pick_exercise(callback: CallbackQuery, state: FSMContext):
    type_id = int(callback.data.removeprefix("t_"))

    if await is_cardio(type_id):
        await state.set_state(AddWorkout.waiting_for_minutes)
        await state.update_data(type_id=type_id)
        await callback.message.answer("Enter duration in minutes")
        await callback.answer()
        return

    await state.set_state(AddWorkout.waiting_for_sets_reps_weight)
    await state.update_data(type_id=type_id)
    
    await callback.message.answer("Enter sets-reps-weight in format '3-10-60' (where 3 is sets, 10 is reps and 60 is weight in kg)")
    await callback.answer()


@router.message(AddWorkout.waiting_for_sets_reps_weight)
async def enter_sets(message: Message, state: FSMContext):
    data = await state.get_data()
    workout_id = data.get("workout_id")
    type_id = data.get("type_id")

    if not message.text:
        await message.answer("Enter a numbers in format '3-10-60' (where 3 is sets, 10 is reps and 60 is weight in kg)")
        return

    parts = message.text.split("-")

    if len(parts) != 3:
        await message.answer("Enter 3 numbers: set-reps-weight")
        return

    try:
        sets = int(parts[0])
        reps = int(parts[1])
        weight = float(parts[2].replace(",", "."))
        
    except ValueError:
        await message.answer("Invalid value. Enter numbers in format '3-10-60' (where 3 is sets, 10 is reps and 60 is weight in kg)")
        return

    if not 0 < sets < 100:
        await message.answer("Invalid sets")
        return
    
    if not 0 < reps < 100:
        await message.answer("Invalid reps")
        return

    if not weight >= 0:
        await message.answer("Invalid weight")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data="cancel")
    kb.button(text="Done", callback_data="workout_done")
    kb.adjust(2)

    await add_exercise_entry(workout_id, type_id, reps, weight) 

    await state.set_state(AddWorkout.waiting_for_exercise)
    await message.answer("Enter another exercise or press done", reply_markup=kb.as_markup())


@router.message(AddWorkout.waiting_for_minutes)
async def enter_minutes(message: Message, state: FSMContext):
    data = await state.get_data()
    workout_id = data.get("workout_id")
    type_id = data.get("type_id")

    if not message.text:
        await message.answer("Enter duration in minutes")
        return

    try:
        minutes = int(message.text)
    except ValueError:
        await message.answer("Invalid value. Enter a number")
        return

    if not 0 < minutes < 1000:
        await message.answer("Invalid value. Enter a correct number")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="Cancel", callback_data="cancel")
    kb.button(text="Done", callback_data="workout_done")
    kb.adjust(2)

    await add_exercise_entry(workout_id, type_id, minutes=minutes) 

    await state.set_state(AddWorkout.waiting_for_exercise)
    await message.answer("Exercise added", reply_markup=kb.as_markup())


@router.callback_query(F.data == "workout_done")
async def finish_workout(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Workout logged", reply_markup=get_main_keyboard())
    await callback.answer()


@router.message(Command("report"))
async def llm_report(message: Message):
    if not await user_exists(message.from_user.id):
        kb = InlineKeyboardBuilder()
        kb.button(text="New User", callback_data="new_user")
        await message.answer("At first you must be registered", reply_markup=kb.as_markup())
        return

    await message.answer("Analyzing your week...")

    report = await sync_to_async(generate_report)(message.from_user.id)

    await message.answer(f"Coach: {report}", reply_markup=get_main_keyboard())
    