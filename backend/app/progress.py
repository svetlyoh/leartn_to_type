def capability_envelope(stage):
    order = int(stage.get("order", 1))
    if order <= 2: return {"band":"orientation","min":20,"max":80,"topic":False,"long":False,"numbers":False,"symbols":False}
    if order <= 5: return {"band":"foundation","min":40,"max":160,"topic":False,"long":False,"numbers":False,"symbols":False}
    if order <= 10: return {"band":"building","min":60,"max":300,"topic":False,"long":False,"numbers":False,"symbols":False}
    if order <= 12: return {"band":"alphabet","min":120,"max":500,"topic":True,"long":False,"numbers":False,"symbols":False}
    if order <= 13: return {"band":"prose","min":180,"max":800,"topic":True,"long":True,"numbers":False,"symbols":True}
    return {"band":"advanced","min":200,"max":1200,"topic":True,"long":True,"numbers":True,"symbols":True}


def calculate_module_progress(completed, minimum, recent_accuracy, target_accuracy, introduced, target_mastery, hint_rate, max_hint_rate):
    drill_component = min(completed / max(minimum, 1), 1)
    accuracy_component = min((recent_accuracy or 0) / target_accuracy, 1)
    mastery_component = (sum(min(item["value"] / target_mastery, 1) for item in introduced) / len(introduced)) if introduced else 1
    hint_component = 1 if hint_rate <= max_hint_rate else min(max_hint_rate / hint_rate, 1)
    ready = completed >= minimum and recent_accuracy is not None and recent_accuracy >= target_accuracy and all(item["met"] for item in introduced) and hint_rate <= max_hint_rate
    return (100 if ready else round(100 * (.25*drill_component + .30*accuracy_component + .35*mastery_component + .10*hint_component))), ready
