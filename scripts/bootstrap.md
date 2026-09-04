# One-time bootstrap

After deployment, set `BOOTSTRAP_TOKEN` as a Worker secret and call `POST /api/v1/admin/bootstrap` with the bearer token and chosen site/admin PINs. Confirm it refuses a second attempt, then immediately remove the bootstrap secret. Never paste any value into logs or source control.
