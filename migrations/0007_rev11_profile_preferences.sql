ALTER TABLE profiles ADD COLUMN school_status TEXT;
ALTER TABLE profiles ADD COLUMN grade_level TEXT;
ALTER TABLE profiles ADD COLUMN theme_id TEXT NOT NULL DEFAULT 'midnight';
ALTER TABLE profiles ADD COLUMN sound_enabled INTEGER NOT NULL DEFAULT 1 CHECK(sound_enabled IN(0,1));
ALTER TABLE profiles ADD COLUMN last_training_at TEXT;
