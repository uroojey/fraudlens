# FraudLens — Daily Build Prompt (30-Day Growth Plan)

Copy this prompt at the start of each day's session. Only the day number changes.

---

```
Day [X] of the FraudLens 30-Day Growth Plan.

Context: FraudLens is a fraud detection product (Streamlit app + Power BI report,
sharing one trained Logistic Regression model) built as a 10-day capstone for the
#60DayClaudeChallenge, now being extended via a 30-day growth plan.

Read the 30-day-growth-plan.md file (attached/uploaded) and find Day [X]'s
milestone. Use it as the source of truth. Do not redesign the project or jump
ahead to a different day's milestone.

Also read (if needed for context): README.md, challenge-retrospective.md,
docs/ARCHITECTURE.md, model_notes.md, and the existing codebase.

Standing rules:
- Assume I need step-by-step guidance for any manual task (installing packages,
  configuring services, running commands, deploying) — explain using real
  button/menu names and exact terminal commands.
- Wait for my confirmation and a screenshot before moving to the next step.
- Never assume I've completed a step.
- Use only free tools/services unless I explicitly approve a paid one.
- Prioritize working code over lengthy explanation — generate complete,
  copy-pasteable files, not snippets or placeholders.
- If today's milestone conflicts with something already built, or reveals a
  problem with a previous day's work, stop and explain the conflict before
  proceeding — don't silently redesign past decisions.
- Test whatever you build before telling me it's done. If something breaks,
  debug it completely before moving forward.

Today's goal: complete exactly Day [X]'s milestone from 30-day-growth-plan.md,
verify it works, help me commit and push to GitHub with a clear commit message,
and give me a short summary of what was done and what Day [X+1] will cover.
```

---

**Usage notes:**
- Replace `[X]` with the current day number (1-30) and `[X+1]` with the next day.
- If you skip a day, just use the correct day number when you resume — the plan doesn't assume daily consistency.
- If a milestone turns out to need more than one day, that's fine — tell Claude explicitly ("Day 9 isn't done yet, continue it") rather than forcing progress to the next milestone prematurely.