from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    age = State()
    gender = State()
    height = State()
    weight = State()
    target_weight = State()
    activity = State()

class WeightStates(StatesGroup):
    value = State()

class FoodStates(StatesGroup):
    waiting_text = State()
