from backend.app.ai.validator import validate
from backend.app.curriculum.generated_curriculum import CURRICULUM
from backend.app.progress import calculate_module_progress, capability_envelope


def test_full_curriculum_is_cumulative_and_fallbacks_are_safe():
    assert len(CURRICULUM["stages"]) == 64
    assert len(CURRICULUM["lessons"]) == 64
    prior = set()
    orders = set()
    for stage in CURRICULUM["stages"]:
        allowed = set(stage["allowedCharacters"])
        assert prior <= allowed
        assert set(stage["introducedKeys"]) - {"Shift"} <= allowed
        assert stage["order"] not in orders
        assert stage["fallbackDrills"]
        assert all(validate(drill, stage["allowedCharacters"], 1, 1200)["valid"] for drill in stage["fallbackDrills"])
        orders.add(stage["order"])
        prior = allowed


def test_module_progress_requires_all_criteria_not_one_round():
    keys = [{"key": "f", "value": .80, "target": .75, "met": True}]
    percent, ready = calculate_module_progress(1, 4, .96, .92, keys, .75, .01, .15)
    assert not ready and percent < 100
    percent, ready = calculate_module_progress(4, 4, .96, .92, keys, .75, .01, .15)
    assert ready and percent == 100


def test_capabilities_expand_without_client_unlocks():
    early = capability_envelope(CURRICULUM["stages"][0])
    prose = capability_envelope(next(stage for stage in CURRICULUM["stages"] if stage["id"] == "module_64"))
    assert early == {"band":"orientation","min":20,"max":80,"topic":False,"long":False,"numbers":False,"symbols":False}
    assert prose["topic"] and prose["long"] and prose["numbers"] and prose["max"] == 1200


def test_rev10_text_catalog_is_complete_and_safe():
    stages = CURRICULUM["stages"]
    lessons = CURRICULUM["lessons"]
    assert [stage["id"] for stage in stages] == [f"module_{number:02d}" for number in range(1, 65)]
    assert [stage["order"] for stage in stages] == list(range(1, 65))
    by_id = {lesson["id"]: lesson for lesson in lessons}
    assert all(stage["builtInTextId"] in by_id for stage in stages)
    assert all(lesson["moduleId"] in {stage["id"] for stage in stages} for lesson in lessons)
    assert all(len(lesson["text"].split()) <= 120 for lesson in lessons)
    for stage in stages[:14]:
        lesson = by_id[stage["builtInTextId"]]
        assert validate(lesson["text"], stage["allowedCharacters"], 1, 1200)["valid"]
    for lesson in lessons[32:48]:
        assert lesson["sourceType"] == "original_commentary"
        assert "original_commentary" in lesson["tags"]
        assert "Excerpt" not in lesson["title"]
