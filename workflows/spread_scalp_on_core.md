# Workflow: Spread Scalp on Core (Making the Market)

## Objective
While holding a directional core position, scalp the bid-ask spread at key liquidity levels using a small fraction of original risk. The core provides directional protection; the scalp layer collects spread income by queue-jumping visible walls.

---

## Prerequisites — All Must Be True

| Condition | Detail |
|-----------|--------|
| Active core position | Short (or long) with a clear original entry and defined risk |
| Unrealized cushion | At least ~$2 of P&L buffer on the core before initiating scalps |
| Wide spread | Bid-ask spread ~$1 or wider (typical in IPOs, low-float names) |
| Visible wall | Large bid (or ask) sitting at or near a round number |
| Stock type | IPO or low-float name where spread is structurally wide |

---

## Scalp Sizing

- **Range:** 5–15% of original core risk
- **Example:** Core risk was $500 → scalp risk budget = $25–$75 per attempt
- Size is intentionally small — the edge is repetition, not size
- Do not increase scalp size because a wall looks "huge" — walls can be spoofed

---

## Entry Rules (Short Core Example)

1. Core is short, price is declining, cushion is building
2. Price approaches a round number with a visible large bid wall
3. Bid **a few cents above the wall** (e.g., wall at $497.00 → bid $497.03–$497.05)
   - Goal: get filled before the wall, not behind it
   - You are providing liquidity slightly above the wall's price

---

## Stop Rules

- **Stop = the wall breaks**
- If the wall absorbs and price trades through it, hit out immediately
- Do not wait for a close below or a second test — exit on the break
- The core short benefits if the wall breaks, so the scalp stop does not hurt overall P&L materially

---

## Target Rules

- Target: lift within the spread — aim to exit at or near the ask side
- Typical target range: $0.30–$0.80 depending on spread width
- Do not hold for more than the spread width — exit at the end of the spread at most
- If price stalls mid-spread and does not lift, exit flat rather than giving back to the stop

---

## Repetition

- This trade can be run **multiple times** on the same core position
- Each attempt is independent — a stop-out on one does not prevent the next
- Reset conditions before each attempt:
  - Cushion still intact on core (at least ~$1.50 remaining after any scalp losses)
  - A new or freshly refreshed wall is present
  - Spread is still wide enough to justify the attempt

---

## Risk Budget Tracking

Track cumulative scalp losses against the core cushion:
- If scalp losses consume more than 50% of core cushion → stop running the scalp layer for that session
- Preserve the core position — scalps are additive, not the primary trade

---

## Edge Summary

- Wide spread = fat reward per scalp relative to tight stop
- Queue-jumping (bidding above wall) = better fill than passive wall participants
- Core short = built-in hedge if wall breaks and price continues down
- Repetition = multiple bites at the same structural level

---

## What This Is Not

- Not a replacement for the core trade
- Not a strategy for tight-spread liquid names (spread must be ~$1+)
- Not a reason to add to the core or change its stop

---

## Notes / Lessons Learned

*(Update this section as you run the trade live)*
