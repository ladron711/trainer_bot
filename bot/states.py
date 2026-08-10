from aiogram.fsm.state import State, StatesGroup


class AddUser(StatesGroup):
    waiting_for_userdata = State()


class AddBodyMeasurement(StatesGroup):
    waiting_for_measurement = State()


class AddMeals(StatesGroup):
    waiting_for_product = State()
    waiting_for_amount = State()


class AddWorkout(StatesGroup):
    waiting_for_exercise = State()
    waiting_for_sets_reps_weight = State()
    waiting_for_minutes = State()