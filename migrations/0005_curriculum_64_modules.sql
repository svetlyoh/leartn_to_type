UPDATE progress
SET stage_id = CASE stage_id
  WHEN 'orientation' THEN 'module_01'
  WHEN 'home_anchors' THEN 'module_01'
  WHEN 'home_left' THEN 'module_02'
  WHEN 'home_right' THEN 'module_03'
  WHEN 'home_all' THEN 'module_04'
  WHEN 'top_left' THEN 'module_07'
  WHEN 'top_right' THEN 'module_10'
  WHEN 'top_all' THEN 'module_10'
  WHEN 'bottom_left' THEN 'module_12'
  WHEN 'bottom_right' THEN 'module_14'
  WHEN 'lowercase_letters' THEN 'module_14'
  WHEN 'shift_capitals' THEN 'module_15'
  WHEN 'punctuation_basic' THEN 'module_16'
  WHEN 'numbers' THEN 'module_20'
  WHEN 'short_sentences' THEN 'module_28'
  WHEN 'paragraphs' THEN 'module_32'
  ELSE stage_id END,
  current_lesson_id = 'builtin_01',
  curriculum_version = '2026.10';
