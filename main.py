#!/usr/bin/env python3
"""Turn raw meeting notes into structured minutes.

Parses free-form notes for a title/date, attendees, decisions, and
action items (lines starting with TODO / ACTION / "Name: ..."), and
prints clean Markdown minutes. Standard library only.
"""
import argparse
import re
import sys
from datetime import date

ACTION_MARKERS = ("todo", "action", "action item", "follow up", "follow-up")


def parse_notes(text):
    """Split raw notes into sections and extract structured items."""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    title = None
    meeting_date = None
    attendees = []
    decisions = []
    actions = []  # (owner, task)
    discussion = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        low = stripped.lower()

        # Title: first line, or a Markdown heading.
        if title is None and (stripped.startswith("#") or not discussion):
            title = stripped.lstrip("#").strip()
            continue
        # Date line.
        date_match = re.search(
            r"(\d{4}-\d{2}-\d{2}|\d{1,2} [A-Z][a-z]+ \d{4}|"
            r"[A-Z][a-z]+ \d{1,2}, \d{4})", stripped)
        if meeting_date is None and date_match and "date" in low:
            meeting_date = date_match.group(1)
            continue
        # Attendees line.
        if low.startswith(("attendees:", "attending:", "present:")):
            names = stripped.split(":", 1)[1]
            attendees = [n.strip() for n in re.split(r"[,;]", names) if n.strip()]
            continue
        # Decisions.
        if low.startswith(("decision:", "decided:", "agreed:")):
            decisions.append(stripped.split(":", 1)[1].strip())
            continue
        # Action items: "TODO: ...", "ACTION: ...", "Name: do X".
        marker = next((m for m in ACTION_MARKERS if low.startswith(m + ":")
                       or low.startswith(m + " ")), None)
        if marker:
            task = re.split(r"[:\-]", stripped, maxsplit=1)[-1].strip()
            actions.append(("", task))
            continue
        owner_match = re.match(r"^([A-Z][A-Za-z ]{1,30}):\s+(.+)$", stripped)
        if owner_match and any(word in owner_match.group(2).lower()
                               for word in ("will", "to ", "should", "needs to",
                                            "by ", "follow", "send", "update",
                                            "prepare", "check", "review")):
            actions.append((owner_match.group(1).strip(),
                            owner_match.group(2).strip()))
            continue
        discussion.append(stripped)

    if title is None:
        title = "Meeting Notes"
    return {
        "title": title,
        "date": meeting_date or date.today().isoformat(),
        "attendees": attendees,
        "decisions": decisions,
        "actions": actions,
        "discussion": discussion,
    }


def format_minutes(parsed):
    out = [f"# {parsed['title']}", "", f"**Date:** {parsed['date']}", ""]
    if parsed["attendees"]:
        out.append("## Attendees")
        out.append("")
        for name in parsed["attendees"]:
            out.append(f"- {name}")
        out.append("")
    if parsed["discussion"]:
        out.append("## Discussion")
        out.append("")
        for line in parsed["discussion"]:
            bullet = line.lstrip("-*• ").strip()
            out.append(f"- {bullet}")
        out.append("")
    if parsed["decisions"]:
        out.append("## Decisions")
        out.append("")
        for decision in parsed["decisions"]:
            out.append(f"- {decision}")
        out.append("")
    if parsed["actions"]:
        out.append("## Action Items")
        out.append("")
        for owner, task in parsed["actions"]:
            if owner:
                out.append(f"- [ ] {task} — **{owner}**")
            else:
                out.append(f"- [ ] {task}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Turn raw meeting notes into structured minutes "
                    "(Markdown).")
    parser.add_argument("file", nargs="?", help="Raw notes file "
                        "(default: read from stdin).")
    parser.add_argument("-o", "--output", help="Write the minutes to this file.")
    parser.add_argument("--title", help="Override the meeting title.")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                text = f.read()
        except OSError as exc:
            print(f"Error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Error: no notes provided.", file=sys.stderr)
        return 1

    parsed = parse_notes(text)
    if args.title:
        parsed["title"] = args.title
    minutes = format_minutes(parsed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(minutes)
        print(f"Wrote minutes to {args.output}")
    else:
        print(minutes, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
