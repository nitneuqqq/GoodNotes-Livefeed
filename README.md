# GoodNotes Livefeed

An AI tutor that watches you write math in GoodNotes and points out a wrong step as soon as you pause.

How it works: the iPad screen is mirrored to a Windows PC. `tutor.py` grabs the screen every second. When you stop writing for a moment, it sends the page to Claude. If a step is wrong, it beeps and prints what's wrong and the corrected step.

## Setup

1. Mirror the iPad to the PC with an AirPlay receiver app for Windows (for example LonelyScreen or AirServer). Open GoodNotes on the iPad.
2. `pip install -r requirements.txt`
3. Set your API key: `$env:ANTHROPIC_API_KEY = "sk-ant-..."` (PowerShell)
4. Run: `python tutor.py`

Options:
- `--region left,top,width,height` watches only the mirror window instead of the whole screen.
- `--pause 2` sets how many seconds without writing before a check.

Test: `python test_tutor.py`
