PRAGMA foreign_keys=ON;

CREATE TABLE users(
  id TEXT PRIMARY KEY,
  webauthn_user_id BLOB NOT NULL UNIQUE,
  temporary_handle TEXT NOT NULL UNIQUE,
  account_status TEXT NOT NULL DEFAULT 'active' CHECK(account_status IN('active','disabled')),
  accepted_activation_version INTEGER,
  activation_verified_at TEXT,
  onboarding_completed INTEGER NOT NULL DEFAULT 0 CHECK(onboarding_completed IN(0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE passkey_credentials(
  credential_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  public_key BLOB NOT NULL,
  sign_count INTEGER NOT NULL DEFAULT 0,
  device_type TEXT,
  backed_up INTEGER NOT NULL DEFAULT 0 CHECK(backed_up IN(0,1)),
  transports_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  last_used_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX idx_passkey_credentials_user ON passkey_credentials(user_id);

CREATE TABLE webauthn_challenges(
  id TEXT PRIMARY KEY,
  session_nonce TEXT NOT NULL,
  challenge BLOB NOT NULL,
  ceremony_type TEXT NOT NULL CHECK(ceremony_type IN('registration','authentication')),
  pending_user_id TEXT,
  webauthn_user_id BLOB,
  temporary_handle TEXT,
  expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX idx_webauthn_challenges_expiry ON webauthn_challenges(expires_at);

CREATE TABLE app_access_config(
  id INTEGER PRIMARY KEY CHECK(id=1),
  activation_version INTEGER NOT NULL DEFAULT 1,
  changed_at TEXT NOT NULL
);
INSERT INTO app_access_config(id,activation_version,changed_at)
VALUES(1,1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));

ALTER TABLE auth_sessions ADD COLUMN user_id TEXT REFERENCES users(id);
ALTER TABLE profiles ADD COLUMN user_id TEXT REFERENCES users(id);
CREATE INDEX idx_profiles_user ON profiles(user_id);
