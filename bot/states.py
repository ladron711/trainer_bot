from aiogram.fsm.state import State, StatesGroup


class AddUser(StatesGroup):
    waiting_for_userdata = State()


class AddBodyMeasurement(StatesGroup):
    waiting_for_measurement = State()


class AddMeals(StatesGroup):
    waiting_for_product = State()
    waiting_for_amount = State()


class AddProduct(StatesGroup):
    waiting_for_unit = State()
    waiting_for_protein = State()
    waiting_for_carbs = State()
    waiting_for_fats = State()
    waiting_for_calories = State()


class AddWorkout(StatesGroup):
    waiting_for_exercise = State()
    waiting_for_sets = State()