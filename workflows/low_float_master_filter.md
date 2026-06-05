# Low Float Master Filter

> Pre-market reference + real-time grading. Read top-to-bottom as a morning SOP. Jump to any section mid-session by header.

## Objective

Capture every repeatable low float setup before it moves. No missed Day 3s. No missed sympathy names. No chasing a name you forgot to watch overnight.

**Three jobs this document does:**
1. Pre-market SOP — what to run through every morning before 9:30
2. Real-time grading — which playbook applies, how much conviction
3. Rules reference — execution, dilution, risk modifiers mid-trade

**When not to use this document:** If a name doesn't pass the stock selection filter (built separately), it doesn't enter this workflow at all.

---

## Section 1 — Pre-Market Daily Routine

Run these steps in order. Every morning. Non-negotiable.

---

### Step 1 — Limit Band Pre-Calculation (5:30 AM)

Limit bands are determined by the **prior day's closing price**. They are fixed before the open. You cannot calculate them fast enough in real-time — do it now.

**Band lookup table:**

| Prior Day Close | Band Width (each side) |
|----------------|----------------------|
| $0.01 – $0.99 | $0.05 |
| $1.00 – $1.99 | $0.10 |
| $2.00 – $2.99 | $0.15 |
| $3.00 – $4.99 | $0.20 |
| $5.00 – $9.99 | $0.50 |
| $10.00 – $19.99 | $1.00 |
| $20.00+ | Standard circuit breaker rules |

**For every ticker on any watchlist:**
- Record prior close
- Compute band width from table above
- Note upper band = expected open + band width
- Note lower band = expected open − band width
- A stock approaching its upper band = halt possible → pressure cooker forming

---

### Step 2 — SSR Status Check (5:45 AM)

Check FINRA's daily SSR list for all watchlist names. SSR triggers when a stock drops 10%+ from prior close.

**SSR on a gap-up day = squeeze candidate.** Shorts cannot hit the bid. They must offer up. This is mechanical friction in your favor.

Mark each watchlist name: SSR active or not.

---

### Step 3 — Dilution Research via AskEdgar MCP (6:00 – 6:45 AM)

For any **new name** from prior day's scan, run the full dilution protocol (Section 6). Use AskEdgar MCP directly in Claude — no manual EDGAR navigation needed.

Output: one classification per ticker → determines maximum allowable size.

Existing watchlist names: only re-run if there was a new filing overnight (AskEdgar can confirm this).

---

### Step 4 — Watchlist Population (7:00 – 8:00 AM)

Maintain four watchlists (Section 7). Move names between lists based on prior day's price action:

- Strong Day 1 (25%+, 5M+ vol) → add to **Day 2 Watch**
- Day 2 Watch name that printed inside bar + ≥50% volume contraction → promote to **Day 3 Liquidity Trap**
- Any name that moved 30%+ on 5M+ volume (last 20 sessions) → add to **HVD Support**
- Head-of-snake active today → build **Sympathy** list immediately

---

### Step 5 — Borrow Availability Check (8:00 AM)

Check HTB status on any name where short positioning matters (longs benefit from knowing shorts are trapped).

HTB + SSR = maximum squeeze fuel. The higher the annualized borrow rate, the more shorts are bleeding to stay short.

---

### Step 6 — Premarket Structure Read (8:00 – 9:25 AM)

For every active name: record premarket high, premarket low, premarket volume.

**Day 3 Liquidity Trap names specifically:**
- Tight premarket range on elevated RVOL = coiled spring
- Premarket gap already above Day 2 high = Day 3 squeeze may be starting pre-open, build position with clear stop below Day 2 high
- No premarket gap = watch for 9:30 opening range break above Day 2 high

---

### Step 7 — Catalyst Quality Grade (9:00 – 9:25 AM)

Assign each in-play name a catalyst tier from the Catalyst Catalog (Section 2). Tier feeds into the scoring system.

Combine with playbook identification: know WHICH playbook (LF-01 through LF-05) applies before the open, not after.

---

## Section 2 — Catalyst Catalog

Catalysts are **not playbooks**. They explain why the name is in play. The playbook (Section 3) tells you how to trade it based on where the stock is in its move cycle.

| Catalyst | What it creates | Example tickers |
|----------|----------------|-----------------|
| Big-name partnership | Retail narrative magnet regardless of deal economics | LIDR (NVDA), CMBM (Starlink), FLYX (Starlink) |
| PIPE announcement | Institutional floor — investors want price higher | ORBS |
| Special dividend | Tightens effective float, distorts supply/demand, shorts must pay the dividend | SOGP |
| Reverse merger | New float, new narrative, prior resistance becomes support | SGN |
| Strategic alternatives | Acquisition floor bid after a collapse | QNCX, IRBT |
| Reddit / social theme | Retail coordination, shareable narrative drives parabolic | BYND |
| Macro sector theme | AI, metals, space, defense, crypto, biotech, oil, EV, quantum, robotics | RIME, NAMM, SIDU, IRBT |
| Private placement | Capital narrative + shelf dilution path; EFFECT filing = hard exit trigger | CJET |
| SEC filing trigger | EFFECT, reverse split, 8-K offering — monitor via AskEdgar MCP | various |

**Catalyst tiers for scoring:**
- **Tier 1:** Special dividend, NVDA/Starlink-class partnership, PIPE, reverse merger close, strategic alternatives
- **Tier 2:** Macro sector theme alignment, private placement, hot SEC filing trigger
- **Tier 3:** Social mention, sympathy to a Tier 1/2 name, generic press release

**Theme hotness gauge:** 2+ large-caps in the same sector up >5% today = theme is hot. If the top sector name is up >10%, it is very hot. Small caps follow large caps by 1–3 days — watch large-cap sector leaders as early warning.

> **Note — Private Placement exit trigger:** Watch for the EFFECT filing via AskEdgar MCP. The moment the shelf registration goes effective, institutional selling begins. This is a hard exit signal regardless of price action.

---

## Section 3 — Playbook Catalog

Five repeatable execution structures. The catalyst explains the why. The playbook tells you how to trade it based on where the stock is in its cycle.

**Template for each playbook:**
- **Trigger:** What condition activates this setup
- **Grade B:** Minimum baseline to consider the trade
- **Grade A:** Strong setup, elevated conviction
- **Grade A+:** Maximum conviction
- **Entry / Stop / Target**
- **Reference tickers**

---

### LF-01: Day 1 Gap Runner

**Trigger:** First big move day on a new catalyst. Stock is gapping 20%+ premarket on genuinely new news.

**Grade B:**
- Gap 15%+
- Catalyst Tier 1 or 2
- Float <50M
- RVOL >5x
- Not a serial diluter

**Grade A:**
- Gap 25%+
- Float <20M
- Catalyst Tier 1
- SSR triggered by the gap
- HTB borrow confirmed
- Opening drive without immediate fade

**Grade A+:**
- Gap 40%+
- Float <10M
- Catalyst Tier 1 + macro theme alignment
- Premarket halt already occurred (pressure built before open)
- Multiple checks in favor (see Section 4)

**Entry:** Opening range breakout (first 5-min high). Or VWAP reclaim after brief opening fade if the thesis is still intact.

**Stop:** Opening range low (first 5-min low). Or premarket low if holding clean above it into open.

**Target:** Prior resistance on daily chart. Scale out at momentum waves — never wait for a single target.

**Reference tickers:** LIDR, CMBM, BMGL, PROK, THAR

---

### LF-02: Day 2 Continuation

**Playbook name:** Gap-up on Day 2 after a strong Day 1.

**Trigger:** Stock had a strong Day 1 (25%+, closed in top 25% of day's range). Day 2 opens with a gap-up. Day 1 shorts who survived are now trapped again above their stops.

**Grade B:**
- Day 1 move 25%+, volume 5M+
- Day 1 close in top 25% of day's range
- Day 2 premarket gap 5%+
- Float <50M

**Grade A:**
- Day 1 closed near HOD (top 10% of range)
- Day 2 gap >10%
- SSR active on Day 2
- No visible premarket selling pressure on tape

**Grade A+:**
- Day 1 was 40%+ move, closed at HOD
- Day 2 gap >15%
- SSR active
- Float rotation on Day 1 was >2x (more volume than shares exist)

**Entry:** Opening print if gapping into clean air with no prior resistance nearby. Or first 1-min VWAP hold after opening range establishes.

**Stop:** Day 2 opening range low. If violated, the gap-up is failing and Day 1 shorts are regaining control.

**Target:** 1x Day 1 range added to Day 2 open. Or prior week highs.

**Risk flag:** If Day 1 close was below midpoint of day's range — reduce to half size (gap may be an exhaustion gap, not continuation).

**Reference tickers:** OPEN, BGLC, MBIO, ABVE

---

### LF-03: Liquidity Trap (3-Day Cycle)

**Trigger:** Day 1 massive move. Day 2 is an inside day with volume contraction. Day 3 forces trapped participants to re-enter aggressively.

**How the trap works:**
- Day 1 traps late shorts and aggressive chasers through extreme volatility
- Day 2 low volume creates the illusion the move is dead; shorts grow complacent; weak hands exit
- Day 3 breakout above Day 2 high forces all Day 2 shorts to cover simultaneously in thin liquidity

**Grade B:**
- Day 1 move 30%+, volume 5M+
- Day 2 inside bar (Day 2 high < Day 1 high, Day 2 low > Day 1 low)
- Day 2 volume ≥50% below Day 1 volume
- Float <50M

**Grade A:**
- Day 2 volume is 60%+ below Day 1
- Day 2 closes near Day 1's close (not breaking down into EOD)
- SSR active on Day 3
- Float <20M

**Grade A+:**
- Day 2 volume is 70%+ below Day 1
- Day 3 premarket gap already above Day 2 high (squeeze starting pre-open)
- Limit bands calculated premarket show the gap is within 1 band of continuation
- HTB borrow confirmed

**Entry:** Day 3 break above Day 2 high — the trigger point where all Day 2 shorts get stopped simultaneously. If Day 3 premarket is already above Day 2 high and pulling back to it, that pullback is the entry with a tight stop.

**Stop:** Day 2 low. If Day 3 opens gap-down below Day 2 low — setup is dead, do not trade.

**Target:** Day 1 HOD (first target). Then extension based on ATR.

> **Do not forget these.** The Day 3 setup is easy to miss if you don't maintain the Day 3 watchlist every evening. This is the most documented pattern in the research and also the easiest to sleep through.

**Reference tickers:** BNAI, ATCH, IRBT, CYPH, IRBT, UGRO, EVTV

---

### LF-04: High-Volume Day Support

**Trigger:** A prior session with 30%+ move and 5M+ volume created a key reference level. Stock has since pulled back toward that level. The high-volume day's VWAP and close become support.

**Why it works:** High-volume days represent committed positioning. The market tends to return to and respect these levels because the participants who traded that day are still present and defending their cost basis.

**Grade B:**
- Prior session move 30%+, volume 5M+
- Current price pulled back to within 10% of that day's VWAP or close
- RVOL on current day still elevated (>2x)
- Catalyst is still active or new related catalyst

**Grade A:**
- Stock has based above the HVD close for 2+ sessions without breaking down
- Reclaim of HVD VWAP with intraday volume expansion
- No dilution event since the high-volume day

**Grade A+:**
- 3+ sessions basing tightly above the HVD level (volume contracting each day)
- Breakout day has RVOL >5x
- SSR or HTB in favor

**Entry:** Reclaim of HVD VWAP or close price, confirmed with at least one full 5-min bar holding above the level.

**Stop:** Below the HVD low. If that breaks, the support thesis is invalidated.

**Target:** HVD HOD (first target), then Fibonacci extension from HVD base.

**Scan to build this watchlist:** 30%+ move + 5M+ volume. Any name hitting this scan goes on the HVD Support watchlist for up to 20 sessions.

**Reference tickers:** MBIO (July 7 2025), KLTO (June 9 2025)

---

### LF-05: Sympathy Play

**Trigger:** A "head of snake" name is in an active Day 1 move (20%+). Find correlated names in the same sector or theme that haven't moved yet. Strength or weakness in the leading stock triggers correlated momentum in related names.

**How to identify the head of snake:** The name with the primary catalyst, the highest volume, and the earliest move. Everything else in the sector is a sympathy name.

**Grade B:**
- Head-of-snake is up 20%+ and accelerating or holding gains
- Sympathy candidate is in the same sector/theme
- Sympathy name float <100M
- Sympathy RVOL beginning to expand (>2x)
- Sympathy name has not yet broken out (at <50% of its own day's range)

**Grade A:**
- Head-of-snake is up 40%+ and parabolic
- Sympathy float <30M
- Sympathy has a secondary supporting catalyst (amplifying factor)
- SSR possible on sympathy if it begins gapping

**Grade A+:**
- Head-of-snake is the hottest name of the month
- Multiple sympathy names all activating simultaneously (sector-wide)
- Sympathy name is the most liquid name in the sector (gets the most overflow)

**Entry:** Sympathy name's breakout above its own premarket high or prior day high. Do not chase a sympathy that is already extended — entry is on the sympathy name's own structure, not the head's move.

**Stop:** Sympathy name's VWAP. Exit sympathy immediately if the head-of-snake fades below 50% of its day's move — the correlation breaks on head reversal and sympathy will fall faster.

**Target:** Sympathy moves typically run 30–50% of the head-of-snake's move. Use that ratio as a price target reference.

> **Key rule:** You trade the sympathy only while the head is strong. When the head fades, exit the sympathy — do not wait for your own stop to be hit.

**Sector map (build this over time):**
- OPEN → AIRE, FFAI, OPAD
- Space theme → SIDU, MNTS, FLYX
- Metals/gold → NAMM, BGL
- Add pairs as you observe them

**Reference tickers:** OPEN / AIRE / FFAI / OPAD (July 2025)

---

## Section 4 — Checks In Your Favor

These are **not playbooks**. They are conditions that increase conviction in any of LF-01 through LF-05. Stack as many as possible before sizing up.

| Check | What it means |
|-------|--------------|
| SSR active | Shorts cannot hit the bid — mechanical squeeze friction |
| Tight limit bands | Price moves in capped increments — halts trap shorts and build pressure |
| HTB borrow | Hard to locate shares to short — supply of selling limited |
| Halts already occurred | Each halt adds pent-up pressure for the re-open |
| Cold market / complacent shorts | First runner after a dry spell — shorts are lazy and over-positioned |
| Float rotation >1x | More volume traded than shares that exist — extreme supply pressure |
| Level 2 wall at key level | Significant size = stop reference AND add-point if you're positioned against it |
| Multi-exchange orders at same level | ARCA + NASDAQ + BATS simultaneously = institutional size, not a spoofer |
| Tape: buying volume not moving price | Hidden seller absorbing — find the level, trade against it as a wall |
| Premarket structure tight / coiling | Compressed range on elevated RVOL = spring loading for Day 3 open |
| Macro theme hot | 2+ large-cap sector names up >5% today |

**General rule:** 3+ checks in favor on top of a graded playbook = A+ conviction. Fewer checks = scale back size.

**Cold market exception:** When markets have been slow and a name finally moves, traders aggressively chase it with larger size due to frustration. This is a psychological dynamic — factor it in as a check in your favor for the squeeze (more chasers = more trapped), but personally size down in cold markets (grade setups higher, be more selective).

---

## Section 5 — Filter Scoring System

> **[Placeholder — to be completed by Judin]**
> 
> This section will define the numeric scoring system applied pre-market to each candidate to produce a grade (B / A / A+) and a position size multiplier. The scoring inputs are: float, RVOL, catalyst tier, theme, technical checks, and risk deductions from the dilution classification.

---

## Section 6 — Dilution Research Protocol

**Tool:** AskEdgar MCP — call it directly in any Claude conversation. No manual EDGAR navigation.

Ask AskEdgar to pull for any ticker: shelf registration status, offering history, warrant terms, ATM programs, reverse split filings, cash position from latest 10-Q or 20-F.

---

### Sequential Research Steps

Run in order. Each step adds or removes risk flags.

**Step 1 — Shelf Check**
Is there an active S-3, F-3, S-1, or F-1 registration?
If an EFFECT filing is present → the shelf is live right now. Dilution can happen at any moment.

**Step 2 — Offering Frequency**
Count 8-K capital raise filings in the last 12 months.
>2 raises in 12 months = "Frequent Raiser." Flag it.

**Step 3 — Warrant Check**
From the most recent prospectus or 8-K: what are the warrant exercise prices?
If exercise price is within 20% of current price → warrants are near-money. Management has incentive to sell stock and let warrants convert.

**Step 4 — Cash Runway**
Latest 10-Q or 20-F: cash on hand ÷ quarterly cash burn = quarters of runway.
<2 quarters of cash = company WILL raise capital. This is a near-certain dilution signal regardless of what management says.

**Step 5 — ATM Facility**
Search for "At-the-Market" or "ATM" in any recent filing.
If an ATM is active: management can sell shares directly into the market at any price, at any time, without announcing it first. This is the most dangerous dilution mechanism for a momentum trade.

**Step 6 — Reverse Split History**
How many reverse splits in the last 5 years?
Pattern: reverse split → stock pops → management sells → repeat. Two or more splits = serial diluter territory.

**Step 7 — Underwriter Pattern**
Do the same underwriters or placement agents appear repeatedly?
The same financiers across multiple deals = institutional dilution machine. The ticker changes; the behavior repeats.

---

### Dilution Classification

| Risk Flags | Classification | Max Position Size |
|-----------|---------------|------------------|
| 0–1 | Clean | 100% |
| 2 | Moderate | 50% |
| 3–4 | High Risk | 25% |
| 5+ or serial pattern | Serial Diluter | Long: 0% |

**Serial Diluter = any 4 of the following:**
- 3+ offerings in the last 12 months
- Active ATM facility
- Warrants repriced or restructured multiple times
- 2+ reverse splits in the last 5 years
- Cash runway under 1 quarter
- Same underwriter appearing on 3+ deals
- Float doubles within 6 months of every major run

---

### What to Store Per Ticker (Research Note Format)

Every name researched gets a record saved. This is how institutional patterns are recognized over time.

```
Ticker:
Company name:
Date researched:
Theme / catalyst:
Float:
Market cap:
Cash position:
Burn rate:
Underwriter(s):
Offering history:
Warrant details:
ATM status:
Shelf status (S-3/F-3 active?):
Reverse split history:
Dilution classification:
Notes on management behavior:
Notes on post-spike financing behavior:
```

> **Historical data note:** Even if a ticker gets delisted, renamed, or merged — AskEdgar and Databento's security master can often still track it. Always save the company name and exact date of any event, not just the ticker. Tickers get reused.

---

## Section 7 — Four Watchlists

**Daily maintenance = 15 minutes every evening. Non-negotiable. Missed maintenance = missed Day 3 trades.**

---

### Watchlist 1 — Day 2 Watch

**Entry criteria:** Stock had a 25%+ move on 5M+ volume today.

**Track per name:**
- Day 1 close price
- Day 1 HOD
- Day 1 VWAP
- Float
- Volume rank vs ADV
- Dilution classification

**Morning action:**
- Gap up 5%+ premarket → active watch, apply LF-02
- Gap down 5%+ → momentum is failing, remove from list

**Expiration:** Name ages off after Day 2 close. If Day 2 was an inside bar with ≥50% volume contraction → promote directly to Day 3 Liquidity Trap watchlist.

---

### Watchlist 2 — Day 3 Liquidity Trap

**Entry criteria:** A Day 2 Watch name that printed an inside bar with ≥50% volume contraction vs Day 1.

**Track per name:**
- Day 2 high (the breakout trigger)
- Day 2 low (the stop)
- Day 1 HOD (first target)
- Day 1 volume (reference for confirming Day 2 contraction)
- Current premarket structure

**Morning action:**
- Premarket gap above Day 2 high → Day 3 squeeze may already be running, build position with stop below Day 2 high
- No premarket gap → set alert for 9:30 opening range break above Day 2 high

**Expiration:** Ages off after Day 3 resolves (either squeezed or failed below Day 2 low).

---

### Watchlist 3 — High-Volume Day Support

**Entry criteria:** Any stock that moved 30%+ on 5M+ volume in the last 20 sessions.

**Track per name:**
- HVD date
- HVD VWAP
- HVD close
- HVD HOD
- HVD low
- Current price relative to each of those levels

**Weekly review:** Is the name still holding above the HVD level? Has a new high-volume day (down or up) invalidated the old reference?

**How to populate:** Run `fetch_polygon.py` with the 30%+ / 5M+ scan criteria. Every name that qualifies goes on this list.

**Expiration:** Remove when price closes below the HVD low for 3 consecutive sessions. The level is no longer being defended.

---

### Watchlist 4 — Sympathy

**Entry criteria:** A head-of-snake name is in an active Day 1 move of 20%+.

**Built fresh every time a new head-of-snake activates.**

**Track per name:**
- Head-of-snake ticker and its current % move
- Each sympathy candidate: ticker, float, RVOL, distance from own HOD
- Sector/theme connecting them

**How to find sympathy candidates:**
- Same sector/industry classification as the head
- Same macro theme (space, AI, metals, etc.)
- Names that have moved in tandem with the head historically (build the sector map below)

**Clear the list:** When the head-of-snake fades below 50% of its day's move, exit all sympathy positions and clear the list.

**Sector map (add pairs as observed):**

| Head of Snake | Known Sympathy Names |
|--------------|---------------------|
| OPEN | AIRE, FFAI, OPAD |
| Space theme leader | SIDU, MNTS, FLYX |
| Gold/silver theme leader | NAMM, BGL |
| *(add as observed)* | |

---

## Section 8 — Risk Modifier Rules

Applied after grading. These affect **position size only** — not the setup grade.

| Risk Factor | Size Multiplier |
|-------------|----------------|
| China / HK origin | 0.5x |
| Serial diluter confirmed | 0.0x (do not trade long) |
| Active shelf + <2 quarters cash | 0.5x |
| Warrants within 20% of current price | 0.7x |
| ATM facility active | 0.6x |
| Diluted within last 30 days | 0.5x |
| Reverse split in last 12 months | 0.7x |
| Cold market (first runner after dry spell) | 0.6x |

**Multiple modifiers compound multiplicatively:**
> ATM active (0.6x) × diluted 3 weeks ago (0.5x) = **0.3x normal size**

**China / HK rule:** Immediately reduce risk on any company with Chinese or Hong Kong domicile, regardless of how clean the setup looks. Not a ban — a mandatory haircut.

---

## Section 9 — Execution Framework

### Level 2 Reading

**Real wall vs. spoofer:**
- Wall that refreshes after being partially taken = real seller. Use it as a stop reference and as an add-point if you are positioned against it.
- Wall that disappears when price approaches = spoofer. Ignore it.

**Institutional presence:**
- Same size offered simultaneously on ARCA, NASDAQ, and BATS at the same price = institutional seller. Do not fight it.
- Single-exchange wall = smaller participant, potentially moveable.

**Hidden seller:**
- Consistent aggressive buying on tape (green prints above ask) but price is not moving up = hidden seller absorbing every buyer. Do not trade against a hidden seller. Find the level where this is happening and treat it as resistance until it breaks.

---

### Tape Reading

- Green prints above ask = aggressive buying (buyers lifting the offer)
- Red prints below bid = aggressive selling (sellers hitting the bid)
- Large block print between bid and ask = off-exchange negotiated trade (directional signal — note the direction)
- Volume expanding but price not moving = supply/demand in balance at a contested level

---

### Halt Behavior

- Never enter on the re-open of a halt. Wait 30–60 seconds for direction to establish.
- Up-halt = pressure cooker. Pent-up demand + trapped shorts. Re-open is often violent.
- Multiple halts in one session = squeeze fuel accumulating with each halt.
- Down-halt on a long thesis = warning sign. Assess before the re-open whether the thesis still holds.

---

### SSR Execution

On an SSR day, shorts cannot hit the bid — they must offer up. Implications:
- You can buy more aggressively than normal (no one is banging the bid)
- Your stop fills may be better than expected (less aggressive selling pressure at your exit level)
- SSR names that lose VWAP rarely recover quickly — VWAP is a meaningful line on SSR days

---

### Time of Day Filter

| Window | Character | Action |
|--------|-----------|--------|
| 9:30 – 9:45 | Opening volatility | Day 1 (LF-01) and Day 3 (LF-03) entries only — thesis must be clear before the open |
| 9:45 – 10:30 | First confirmation window | Best entry window for LF-02, LF-04, LF-05 |
| 10:30 – 11:30 | Dead zone begins | Scale down, avoid new entries |
| 11:30 – 1:00 | True dead zone | Fresh catalyst entries only |
| 1:00 – 2:00 | Afternoon reactivation | Check RVOL on Day 1 names that held VWAP all day |
| 2:00 – 3:30 | EOD setup window | Identify Day 2 candidates, build overnight watchlist |
| 3:30 – 4:00 | Closing print | Avoid new entries |

---

### Scale-In Framework

- **Wave 1:** 40% of intended position on initial breakout
- **Wave 2:** 40% on first flag/base confirmation (price holds 2+ minutes above entry level)
- **Wave 3:** 20% on continuation (only if Wave 1 and Wave 2 are profitable)
- Never reach full position before Wave 2 confirms

---

### Exit Rules

- Sell into strength: 25% at first target, 25% at second target, trail remainder with stop at prior flag level
- Do not wait for a single exit price — momentum names do not ring a bell at the top
- When the head-of-snake fades: exit sympathy names before your own stop is hit

---

## Section 10 — Trade Log & Self-Calibration

### Per-Trade Record

For every trade taken from this system:

| Field | Entry |
|-------|-------|
| Date | |
| Ticker | |
| Playbook ID | LF-01 / LF-02 / LF-03 / LF-04 / LF-05 |
| Catalyst type | (from Section 2) |
| Checks in favor | (list which ones applied) |
| Dilution classification | Clean / Moderate / High / Serial |
| Risk modifiers applied | (list, with size multiplier used) |
| Entry price | |
| Stop price | |
| Exit price | |
| P&L | |
| Setup played out? | Yes / No / Partial |
| Notes | |

---

### Monthly Review Questions

1. Which playbook IDs had the highest win rate?
2. Which playbook IDs had the worst win rate?
3. Were checks in favor predictive? (More checks = better result?)
4. Were any risk modifiers ignored? Did that hurt?
5. Were any Day 3 or HVD setups missed due to watchlist not being maintained?
6. Was the dilution classification accurate? Did any "Clean" names dilute unexpectedly?

**Calibration rule:** After 20 trades on a given playbook ID — if win rate <40%, tighten the baseline criteria. If win rate >70%, the criteria may be too conservative (missing trades).

---

## Notes / Lessons Learned

*(One line per lesson: date — ticker — what happened — what changed)*

- 2025-05 — BMGL — Day 1 runner + next day short opportunity; both sides have a playbook in low float
- 2025-07 — OPEN — Day 2 continuation + sympathy names (AIRE, FFAI, OPAD); always identify the head first
- 2025-08 — SOGP — special dividend tightened effective float; model this as extreme float distortion, not just a catalyst
- 2025-11 — CYPH — SSR + $0.15 limit bands + complacent shorts after cold market = textbook squeeze setup
- 2025-12 — IRBT — Day 3 Liquidity Trap sometimes begins in premarket; check structure before open
- 2026-01 — EVTV — $0.40 prior close → $0.15 bands + float rotation = limit-up continuation; bands must be calculated premarket
- 2026-01 — FLYX — SSR + 10% bands + Starlink catalyst = aggressive reversal; halts increase, not decrease, squeeze pressure
- 2026-03 — UGRO — float was so small that any volume created violent moves; float size is the multiplier on everything else
