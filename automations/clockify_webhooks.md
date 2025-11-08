
# Clockify → Clankerbot webhook mapping

- APPROVAL_REQUEST_STATUS_UPDATED → handled as `APPROVAL_REQUEST` summary
- NEW_PROJECT → handled as `PROJECT`
- NEW_TIME_ENTRY or NEW_TIMER_STARTED → handled as `TIME_ENTRY`

Place your receiver at: `POST /webhooks/clockify` and configure the webhook in Clockify to point there.
