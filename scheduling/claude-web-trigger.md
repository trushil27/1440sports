# Daily automation via Claude Code on the web (recommended)

The durable way to run this every morning is a **scheduled session** on Claude
Code for the web, pointed at this repo and this branch.

## Setup

1. Open this repo's environment at <https://claude.com/code> (or the Claude
   mobile/desktop app → Code).
2. Create a **scheduled trigger** (daily, at your chosen local time — e.g.
   07:00).
3. Set the session prompt to:

   > Follow the instructions in `PROMPT_DAILY.md`.

4. Configure the environment so the engine can email:
   - Add the SMTP/email variables as **environment secrets** (see `README.md` →
     Delivery): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`,
     `EMAIL_TO`.
   - Choose a **network policy** that allows outbound SMTP + web research (so the
     daily research refresh and the email send both work). See
     <https://code.claude.com/docs/en/claude-code-on-the-web>.
5. (Optional) Add a `SessionStart` hook to `pip install -r requirements.txt`
   so PDF rendering is available in each fresh container. See the
   `session-start-hook` skill.

Each run will: refresh `data/*.json` via live research, render the day's hero
brief into `briefs/<date>/`, email it, and commit the updates to the branch.

## Why not cron in the container?

The execution container is ephemeral and reclaimed after inactivity, so an
in-container `cron`/`sleep` loop will not survive. The scheduled trigger spins up
a fresh container on schedule — that is the reliable mechanism. A GitHub Actions
fallback (`scheduling/daily-brief.yml`) is provided for engine-only runs without
the research-refresh step.
