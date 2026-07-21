import base64
import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

def available():
    return bool(OPENAI_API_KEY)

def _client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не указан")
    return OpenAI(api_key=OPENAI_API_KEY)

def analyze_food_text(text: str) -> dict:
    if not available():
        return {
            "title": text,
            "calories": 0,
            "protein_g": 0,
            "fat_g": 0,
            "carbs_g": 0,
            "comment": "Добавлено без AI-расчёта."
        }
    response = _client().chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role":"system","content":"Ты эксперт по питанию. Оцени блюдо по описанию пользователя. Верни строго JSON без текста вокруг: title, calories, protein_g, fat_g, carbs_g, comment."},
            {"role":"user","content":text}
        ]
    )
    return _parse(response.choices[0].message.content or "{}")

def analyze_food_image(image_bytes: bytes) -> dict:
    if not available():
        raise RuntimeError("OPENAI_API_KEY не указан")

    b64 = base64.b64encode(image_bytes).decode()

    response = _client().responses.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Ты эксперт по питанию. "
                            "Проанализируй изображение еды. "
                            "Определи блюдо, примерный размер порции "
                            "и пищевую ценность. "
                            "Верни строго JSON без текста вокруг: "
                            "title, calories, protein_g, fat_g, carbs_g, comment."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Определи еду на фото и рассчитай примерные калории и БЖУ."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{b64}"
                    }
                ]
            }
        ]
    )

    return _parse(response.output_text)

def coach(summary: dict, user: dict) -> str:
    if not available():
        tips = []
        if summary["water_ml"] < (user.get("water_target") or 2500) * 0.6:
            tips.append("💧 Выпей ещё воды.")
        if summary["protein_g"] < (user.get("protein_target") or 120) * 0.7:
            tips.append("💪 Добавь белковый продукт.")
        if not tips:
            tips.append("✅ Ты хорошо держишь план.")
        return "🤖 AI Coach\n\n" + "\n".join(tips)
    response = _client().chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.6,
        messages=[
            {"role":"system","content":"Ты дружелюбный AI Health Coach. Дай короткий персональный совет на русском без медицинских обещаний."},
            {"role":"user","content":f"Профиль: {user}\nСегодня: {summary}"}
        ]
    )
    return "🤖 AI Coach\n\n" + (response.choices[0].message.content or "").strip()

def _parse(raw: str) -> dict:
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(raw[start:end + 1])
        else:
            raise ValueError("AI вернул некорректный формат ответа")
    return {
        "title": str(data.get("title") or "Блюдо"),
        "calories": float(data.get("calories") or 0),
        "protein_g": float(data.get("protein_g") or 0),
        "fat_g": float(data.get("fat_g") or 0),
        "carbs_g": float(data.get("carbs_g") or 0),
        "comment": str(data.get("comment") or ""),
    }
