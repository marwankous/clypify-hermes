---
name: prospect
description: Daily Clypify lead prospecting — scan Reddit, X, and Indie Hackers, score leads, draft outreach, write HTML report
trigger: cron
---

# Prospect Skill

Runs the daily lead-prospecting pipeline for Clypify. Scans Reddit, X/Twitter, and Indie Hackers for potential customers, scores them with Gemini (Grok fallback), drafts personalised outreach, and writes a browsable HTML report to `hermes/output/`.

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start (background + daily schedule) | `powershell -ExecutionPolicy Bypass -File start.ps1` |
| Run once now (foreground, live output) | `powershell -ExecutionPolicy Bypass -File run-now.ps1` |
| Stop + cancel schedule | `powershell -ExecutionPolicy Bypass -File stop.ps1` |
| Watch live log | `Get-Content output\prospector.log -Wait` |
| Open today's report | `start output\leads-$(Get-Date -Format yyyy-MM-dd).html` |

All commands must be run from `C:\Users\WS\Desktop\projects\clypta\hermes\`.

---

## Starting the Prospector

### Background mode (recommended)
Registers a Windows Task Scheduler job that fires daily at 07:00 AND runs once immediately:
```powershell
cd C:\Users\WS\Desktop\projects\clypta\hermes
powershell -ExecutionPolicy Bypass -File start.ps1
```

Output is logged to `hermes/output/prospector.log`. To watch it live:
```powershell
Get-Content output\prospector.log -Wait
```

### Manual one-off run (foreground)
Shows output directly in the terminal — useful for testing:
```powershell
cd C:\Users\WS\Desktop\projects\clypta\hermes
powershell -ExecutionPolicy Bypass -File run-now.ps1
```

---

## Stopping the Prospector

Kills any running process and removes the daily scheduled task:
```powershell
cd C:\Users\WS\Desktop\projects\clypta\hermes
powershell -ExecutionPolicy Bypass -File stop.ps1
```

To only cancel the schedule without stopping the current run, use:
```powershell
Unregister-ScheduledTask -TaskName "ClypifyProspector" -Confirm:$false
```

---

## Viewing Reports

Reports are written to `hermes/output/leads-YYYY-MM-DD.html`. Open today's:
```powershell
start output\leads-$(Get-Date -Format yyyy-MM-dd).html
```

---

## Required Environment (.env)

File location: `hermes/.env` (git-ignored — never commit this file)

```
GOOGLE_API_KEY=...     # Primary LLM — Google AI Studio (free)
GROK_API_KEY=...       # Fallback LLM — xAI Grok
```

Reddit and Indie Hackers use public feeds — no API keys needed.
X/Twitter uses Nitter RSS — no API key needed.

---

## On Error

If `py run.py` fails:
- Check `hermes/.env` exists with both keys
- Check `hermes/seen.json` exists — create it if missing: `echo {} > seen.json`
- Check `hermes/output/prospector.log` for the full traceback
- Gemini key format should start with a valid Google AI Studio prefix
