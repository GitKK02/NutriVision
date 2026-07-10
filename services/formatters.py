def bar(value, target, blocks=10):
    if not target:
        return "░" * blocks + " 0%"
    pct = max(0, min(1, value / target))
    filled = int(round(pct * blocks))
    return "█" * filled + "░" * (blocks-filled) + f" {round(pct*100)}%"

def goal_name(goal):
    return {"gain":"💪 Набор массы","maintain":"⚖️ Удержание","deficit":"🔥 Дефицит"}.get(goal, "Не выбрана")
