# Security

Report security issues privately to the repository owner. Never include real PINs, API keys, peppers, bootstrap tokens, or session values in an issue.

The target design uses a server-rendered site gate, PBKDF2-HMAC-SHA256 credential verifiers with per-credential salts and a Worker-secret pepper, opaque HttpOnly sessions represented in D1 only by HMAC, credential lockouts, same-origin mutation checks, and restrictive response headers. The current scaffold denies private assets closed until its D1 session repository is wired.
