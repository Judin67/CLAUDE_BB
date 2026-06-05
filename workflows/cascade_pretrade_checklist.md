# Cascade — Pre-Trade Checklist

Use this every morning before touching a hotkey. It takes 5 minutes.

---

## Step 1 — Premarket Read (before 9:30)

Start here, not at the open. Cycles begin premarket.

**On each ticker in play:**

- [ ] Is there a real catalyst? (gap, news, earnings, sector move) — if not, skip
- [ ] What is the 30m 9-SMA slope direction? This is your day bias. Up = long side. Down = short side.
- [ ] What is the 5m 9-SMA slope doing? Does it agree with the 30m?
- [ ] Is the 5m currently in a pullback against the 30m, or already realigning?
- [ ] Volume check: is there enough volume for the signal to be real? (need ~100k/min bar at open)

**Key question:** Where is the cycle right now — early, mid, or near completion?
- If the 5m just completed a cycle premarket, the 30m is loading → big move potential at open
- If the 5m is mid-pullback, wait for it to complete before sizing in

---

## Step 2 — Bias Assignment (before 9:30)

For each ticker, write down one line:

> `TICKER — [Long / Short / No trade] — Gate: [30m slope direction] — 5m: [aligned / pulling back / opposing]`

Example: `NVDA — Long — Gate: 30m positive — 5m: pulling back (loading)`

This forces you to commit to a bias before price moves.

---

## Step 3 — Opening Window (9:30–10:30)

This is your primary window. Best signals, highest win rate.

**At the signal:**

- [ ] Is the 30m slope still in the same direction you read premarket?
- [ ] Is the 5m slope aligned with the 30m?
- [ ] Did the 1m 9-SMA pull back against the trend within the last 10 bars?
- [ ] Is the 1m 9-SMA now crossing back in the direction of the trend? → **Signal fires here**
- [ ] Proximity: is price within 0.25% of the 5m 9-SMA? If yes, full confidence. If extended, reduce or skip.
- [ ] Confirmed or Unconfirmed? Has a new intraday HOD/LOD been made?
  - Confirmed (new HOD/LOD) → full algo size
  - Unconfirmed (no new HOD/LOD yet) → reduced size, discretionary
- [ ] Type 1 or Type 2 pullback?
  - Type 2 (slope fully flipped then snapped back) → full sizing rules apply
  - Type 1 (shallow, barely flipped) → small size only, discretionary

**Size assignment:**
Use your grade grid. Grade determines which hotkey row you use.

| Setup quality | Grade | Hotkey row |
|---|---|---|
| Best confluence, Type 2, Confirmed | A | Q–P row |
| Solid but less clean | B | A–; row |
| Marginal, feeler/filler | C | Z–/ row |

---

## Step 4 — Dead Zone (10:30–13:00)

Step back. The 5m is pulling back against the 30m trend. Signals exist but the structure is working against you at a higher level.

- No full-size entries
- You can watch and read cycles — use this time to identify what the 30m is loading
- If you must trade: discretionary only, C-grade size maximum

---

## Step 5 — Afternoon Re-entry (13:00–16:00)

Re-engage only if the 30m trend is still intact.

- [ ] Is the 30m slope still in the same direction as the morning bias?
- [ ] Did the 5m realign after the dead zone? If yes, the cycle is live again.
- [ ] Apply same signal checklist as Step 3

---

## Step 6 — In the Trade

**Exit — reads on the gate (one TF up), executes on your entry TF.**

| Entry TF | Gate (read exit here) |
|---|---|
| 1m | 5m |
| 5m | 30m |
| 30m | 65m |
| 65m | 4h |

**Arming:** the exit cycle turns on only after a **new HOD/LOD confirms the leg.** No new extreme → nothing to trail or measure yet.

Three stages, once armed:
1. **Gate bar-break trail** — break of the prior gate candle → partial / add / acknowledge where you are in the exit cycle.
2. **ROC exhaustion on the gate** — leg anchored at the initial stop, grows with the leg → climax present (threshold to calibrate).
3. **Get flat on the entry TF** — exit objectively on the entry-TF bar break, into the exhaustion.

If the leg fades with no ROC climax, the gate bar-break trail is the exit. ROC is an exit signal for a position already held — not an entry filter.

**Discretionary exits (use judgment):**
- Price is extended and showing exhaustion (wicks, volume dying)
- Price closes through the gate SMA (not just approaches)
- Opposite Type 2 fires against your position on the entry TF

**After a new HOD/LOD:**
- Smaller timeframes are live again — trade them as confirmation the next cycle up is loading
- Sequential order: 10s → 1m → 5m → 30m, each cycle building toward the next

**Scaling:**
Each hotkey entry has its own independent stop. You can layer positions at different levels without one stop killing the whole trade.

---

## Quick Reference

```
LONG setup:    30m slope UP + 5m slope UP + 1m pulled back + 1m realigning → entry
SHORT setup:   30m slope DOWN + 5m slope DOWN + 1m pulled back UP + 1m realigning DOWN → entry

Proximity:     Price within 0.25% of 5m 9-SMA → full confidence
Type 2:        Full sizing. Type 1: small only.
Confirmed:     New HOD/LOD made → full algo. Unconfirmed: reduced size.
Dead zone:     10:30–13:00 → step back.
Exit:          New H/L arms it → gate bar-break trail → gate ROC exhaustion → get flat on entry-TF bar break.
```
