"""One line to the operator when the morning job fails before the pipeline could speak.

The pipeline emails on its own failures; a job that dies earlier (a broken memory rebuild,
a missing library) was silent — a red run nobody saw until they looked. The workflow calls
this from a step that runs only on failure.
"""

from __future__ import annotations

import sys

from intel.config import get_settings
from intel.send import Outgoing, mailer_for


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    url = args[0] if args else "(no run link)"
    settings = get_settings()
    if not settings.operator_email:
        print("no OPERATOR_EMAIL; nothing to notify")
        return 0
    msg = Outgoing(
        to=[settings.operator_email],
        subject="[RUN FAILED] 1440 Intelligence — the morning job stopped before the pipeline ran",
        body_text=(
            "The morning job failed at a step before the pipeline could run or send anything, "
            "so there is no signal and no failure detail from the pipeline itself.\n\n"
            f"Run: {url}\n\n"
            "The log names the step. Nothing was sent to anyone else."
        ),
    )
    print(mailer_for(settings).send(msg))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
