import random
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/motivation", tags=["Motivation"])

MOTIVATION_MESSAGES = [
    "Вот это ты разошелся! 🔥",
    "Отличный темп!",
    "Так держать!",
    "Еще немного — и готово!",
    "Каждый шаг приближает тебя к цели! 🏃‍♂️",
    "Ритм твоей жизни — в твоих руках!",
    "Прекрасная тренировка! 💪"
]

@router.get("")
def get_motivation():
    message = random.choice(MOTIVATION_MESSAGES)
    return {"message": message}
