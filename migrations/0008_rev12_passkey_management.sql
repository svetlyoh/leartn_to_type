ALTER TABLE passkey_credentials ADD COLUMN nickname TEXT NOT NULL DEFAULT '';
ALTER TABLE webauthn_challenges ADD COLUMN auth_session_hash TEXT;

-- Enforce the cap even when two registration ceremonies finish concurrently.
CREATE TRIGGER passkey_max_two BEFORE INSERT ON passkey_credentials
WHEN (SELECT COUNT(*) FROM passkey_credentials WHERE user_id=NEW.user_id)>=2
BEGIN SELECT RAISE(ABORT, 'Maximum two passkeys'); END;
