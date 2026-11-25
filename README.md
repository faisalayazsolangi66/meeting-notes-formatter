# meeting-notes-formatter

Turn raw meeting notes into structured minutes (Markdown) with
attendees, discussion, decisions, and action items. Lines starting
with `TODO:` / `ACTION:` — or `Name: will do X` — become action items.

## Requirements

- Python 3.8+
- No third-party packages (standard library only)

## Usage

```bash
python3 main.py notes.txt
python3 main.py notes.txt -o minutes.md
python3 main.py notes.txt --title "Sprint Planning"
cat notes.txt | python3 main.py
```

Options:

- `file` — raw notes file (default: read from stdin)
- `-o, --output` — write the minutes to a file
- `--title` — override the meeting title

## Example

```bash
$ python3 main.py <<'EOF'
Weekly Sync
Attendees: Faisal, Ayesha
We reviewed the launch checklist. The homepage is ready.
Decision: launch on Friday.
TODO: Faisal will send the release notes by Thursday.
EOF
```

Sample output:

```markdown
# Weekly Sync

**Date:** 2026-11-25

## Attendees

- Faisal
- Ayesha

## Discussion

- We reviewed the launch checklist. The homepage is ready.

## Decisions

- launch on Friday.

## Action Items

- [ ] Faisal will send the release notes by Thursday.
```

## License

MIT — see [LICENSE](LICENSE).
