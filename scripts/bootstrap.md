# One-time bootstrap

Run `./scripts/bootstrap.ps1` from the repository root. It securely prompts for the site and admin PINs, rotates a temporary random `BOOTSTRAP_TOKEN`, calls the one-time endpoint, and deletes the temporary secret afterward. Never paste PINs or secret values into chat, logs, or source control.
