# VocabScroll 🃏

A mobile-first German ↔ English flashcard app that replaces mindless social media scrolling with vocabulary learning — one card at a time.

**Live app:** `https://<your-username>.github.io/vocabscroll`

---

## Features

| Feature | Details |
|---|---|
| 🃏 Flashcards | Flip animation, tap or swipe |
| 🧠 Spaced Repetition | SM-2 algorithm — cards you miss come back sooner |
| 📊 CEFR Levels | A1 / A2 / B1 / B2 / C1 / C2 filter |
| 🔀 Modes | DE→EN · EN→DE · Random mix · Due cards only |
| 💾 Progress sync | Saved in `localStorage` — persists across sessions |
| 📱 PWA | Installable on home screen (iOS & Android) |
| ⌨️ Keyboard | Space/↑↓ = flip · →/L = correct · ←/J = missed · S = skip |

---

## How spaced repetition works

Each card tracks its own review interval using the **SM-2** algorithm:

- ✓ **Got it** → interval grows (1d → 6d → ~15d → …)
- ✗ **Missed** → resets to 1 day
- The interval is shown in the bottom-right corner of each card
- Orange = **due now**
- Use **⏰ Due** mode to review only cards that need attention today

A card is considered **mastered** when it has been correctly reviewed ≥ 3 times with an interval ≥ 21 days.

---

## Install as an app (PWA)

**iOS (Safari):** Share → Add to Home Screen  
**Android (Chrome):** Menu → Add to Home Screen / Install App

---

## Vocabulary coverage

| Level | Focus |
|---|---|
| A1 | Core verbs (sein, haben, gehen…), numbers, greetings, basic nouns |
| A2 | Everyday verbs, common nouns, simple phrases |
| B1 | Abstract nouns, modal verbs, intermediate vocabulary |
| B2 | Academic/professional vocabulary, complex verbs |
| C1 | Advanced expressions, nuanced adjectives |
| C2 | Near-native precision vocabulary |

---

## File structure

```
vocabscroll/
├── index.html      ← The entire app (single file)
├── manifest.json   ← PWA manifest
├── icon-192.svg    ← App icon (small)
├── icon-512.svg    ← App icon (large)
└── README.md
```

---

## Roadmap

- [ ] Arabic translations (DE ↔ AR mode)
- [ ] Gamification (XP, levels, daily goals, badges)
- [ ] Custom card editor (add your own vocab)
- [ ] Grammar rules deck
- [ ] Daily streak with push notifications

---

## Development workflow

This app is built collaboratively with **Claude (Anthropic)**. To update:

1. Share the raw file URL with Claude:  
   `https://raw.githubusercontent.com/<user>/vocabscroll/main/index.html`
2. Describe the changes you want
3. Download the updated `index.html`
4. Replace the file in this repo and commit

---

*Built with vanilla HTML/CSS/JS — no frameworks, no build step, no dependencies.*
