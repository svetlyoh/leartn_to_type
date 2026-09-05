ALTER TABLE auth_sessions ADD COLUMN name_confirmed INTEGER NOT NULL DEFAULT 0 CHECK(name_confirmed IN(0,1));
ALTER TABLE auth_sessions ADD COLUMN login_name TEXT;
