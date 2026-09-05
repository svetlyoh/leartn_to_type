UPDATE progress
SET current_lesson_id = replace(stage_id, 'module_', 'builtin_')
WHERE stage_id GLOB 'module_[0-9][0-9]';
