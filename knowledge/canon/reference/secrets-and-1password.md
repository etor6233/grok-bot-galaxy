# Secrets and 1Password

Source: clip 09 Q&A ~00:01:35–00:02:18.

Do you sign into 1Password **on the bot’s VM**? **No — a Grok Bot modal.**

- Login / API secrets / env secrets pop a modal **in Grok Bot**, not on the side of the VM.
- Stored **securely inside Grok Bot**; not exposed to the SpaceX team.
- Credentials are then used to log into the services the bot needs.
