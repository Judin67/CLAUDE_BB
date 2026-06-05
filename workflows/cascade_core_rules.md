# Trend Cascade — Core Rules

> **Single source of truth** for the **Trend Cascade** variant. If the code and this file disagree, this file wins. Last reconciled: 2026-05-29.
>
> **Validation status: UNVALIDATED.** Every specific number here (±0.02% slope band, 2-bar lookback, 10-bar pullback window, 0.25% proximity, 100k volume, time windows, exit threshold) is **provisional**. The only prior backtest was run on a *different model* and has been discarded. The logic is designed; the thresholds are hypotheses until backtested on *this* model. Don't mistake the figures for proven.

---

## What Cascade is

Cascade is a **framework**, not one trade: multi-timeframe alignment + cycle tracking gives a **direction-agnostic read** of where each timeframe sits in its cycle (loading → mid-trend → exhausted). What you do with that read is the execution layer.

- **Trend Cascade** *(this file)* — act on the **realignment**: enter the continuation after a pullback, with the higher timeframes behind you.
- **Fade Cascade** *(separate family — parabolic / overextension / trend-exhaustion)* — same engine, inverted: fade the move when the cycle tops out against the higher timeframe.

Same engine, different execution. Never say just "Cascade" — say which one.

**Use it on stocks in play only** — names with a catalyst that day (gap, news, earnings, sector move) pulling real volume. Not QQQ/SPY on a quiet day.

---

## The stack & gates

**Weekly → Daily → 4h → 65m → 30m → 5m → 1m → 10s.**

Each timeframe's **gate** is the timeframe directly above it. The higher timeframe gives **direction**, the lower gives **timing**. Before taking a signal on a timeframe, the ones above it must already point the same way.

| Trading TF | Gate |
|---|---|
| 10s | 1m |
| 1m | 5m |
| 5m | 30m |
| 30m | 65m |
| 65m | 4h |
| 4h | Daily |
| Daily | Weekly |

**Slope, every timeframe:** 9-SMA, **percent** slope, 2-bar lookback. FLAT band = **±0.02%** (UP > +0.02, DOWN < −0.02, else FLAT). Every rule below is stated relative to your entry TF and its gate — the framework is identical at every level, only the labels change.

---

## The cycle

One cycle = a timeframe's momentum aligning with the higher trend → pulling back against it → realigning. On the 9-SMA slope: positive → negative (the pullback) → crossing back above zero (**the realignment, where the signal fires**).

Cycles run **sequentially up the chain**: 10s → 1m → 5m → 30m. Each completed cycle signals the next timeframe up is loading. Two layers of opportunity:
- **Sequence:** follow the cycle up the chain — after each entry, anticipate the same setup one TF up.
- **In-between:** smaller timeframes throw real tradeable signals while the larger cycle builds.

**Two pullback types:**
- **Type 1 (shallow):** price dips, 9-SMA stays roughly intact. Discretionary, small size, no algo signal.
- **Type 2 (deep):** 9-SMA slope **flips against** the trend, then snaps back. This is the edge — what the algo detects and what you size into.

---

## Alert ("get ready")

- **Long:** your TF's 9-SMA slope turns **negative** while the **gate** is still positive.
- **Short:** your TF's slope turns **positive** while the gate is still negative.

---

## Entry

**Long — all true at once:**
1. **TF two above** your entry TF (the gate's gate, = day bias) sloping up (> +0.02%). Flat/down → no long.
2. **Gate** also sloping up. Gate and day bias must agree.
3. Entry TF slope **went negative within the last 10 bars** (confirms the Type 2 pullback).
4. Entry TF slope **now crossing back above zero** — the realignment fires here.

**Short:** flip everything — day bias < −0.02%, gate down, entry TF slope was positive in the last 10 bars and now crossing back below zero.

*Example (1m entry): 30m up + 5m up + 1m went negative in last 10 bars + 1m now crossing back up → long.*

---

## After entry, new highs/lows, and ceilings

- After entry, **only signals on your entry TF or higher count** until price makes a new intraday H/L. Smaller-TF signals are part of the cycle you already entered — ignore them.
- A **new H/L confirms structure** and frees the smaller timeframes again.
- **Each level has a ceiling:** the 10s/1m window stays open until 5m momentum breaks; the 5m window until 30m breaks; the 30m window until 65m breaks; the 65m window until 4h breaks. Move up the stack as each ceiling breaks; each new H/L resets the window.

**Rule of thumb (master gate):** when **any** timeframe is in its Type 2 pullback, take no signals from any timeframe below it until it realigns. If the 30m is pulling back against the 4h, no 5m/1m signal is valid until the 30m realigns. The dead zone is just the most common case of this.

---

## Signal tiers & size

- **Confirmed** = Type 2 *after* a new intraday H/L → full algo, **full size**.
- **Unconfirmed** = Type 2 *before* a new H/L → valid but unproven, **reduced size**, discretionary.
- **Type 1** → **small size** only.

Never mix Confirmed and Unconfirmed in the same execution framework.

---

## Filters

- **Volume:** minimum avg **100k per 1m bar**. Below that, don't trade — signals get unreliable.
- **Proximity:** price within **0.25% of the gate 9-SMA** at entry. Close = full confidence; extended = reduce or skip.
- **Time:**
  - **9:30–10:30** — opening trend window, cleanest signals, highest win rate.
  - **10:30–13:00** — dead zone (5m pulling back against 30m). Algo skips; discretion only, low confidence.
  - **13:00–16:00** — re-engage if the 30m trend is still intact.

---

## Stop

- **Long:** lowest low of the pullback bars (where slope was negative before turning back up, within the last 10 bars).
- **Short:** highest high of those pullback bars.

---

## Repeat-signal rule

Once a signal fires on a timeframe, no smaller-TF signal counts until a new intraday H/L — it's firing inside the same cycle the larger TF already used, so it's noise. A fresh **same-TF** signal is valid (new cycle context).

---

## Cycle reading before entry

Start reading cycles from **premarket**, not the 9:30 open — a cycle that began at 9:15 may already be mid-phase or exhausted by the open. Identify which timeframe cycle is active and where it is in its phase before acting. A valid signal in the wrong cycle phase is still a bad trade.

---

## Exit

The exit **reads on the gate** and **executes on your entry TF** — same relativity as everything else.

**Arming:** the exit turns on only when price makes a **new HOD/LOD that confirms the leg.** No new extreme = no confirmed leg = nothing to measure. (Same switch that confirms the entry leg.)

**Three stages, in order:**

1. **Trail on the gate bar-break.** Price breaks (wick-through) the prior **gate** candle's low (long) / high (short) → partial, add, or just note where you are. The management layer — it **lags**, so it manages, it doesn't fire.

2. **Candle-range velocity exhaustion on the gate — the leading signal.** You're already in confirmed momentum (the leg) — you're not detecting it, you're reading its pulse. Decompose the leg into its **gate candles** and measure each candle's **range = high − low** (full wick-to-wick travel) — distance per bar = the **velocity** of the move.
   - **Velocity** = the candle range itself (how fast price is moving this bar).
   - **Acceleration** = ΔRange (this range vs the prior — is the move speeding up).
   - **Exhaustion** = range velocity spikes to an extreme, then acceleration rolls over (ranges stop expanding / contract).
   - **Z-score the range** against its baseline distribution for that TF/context so the extreme is comparable across names and one threshold applies.
   - Clock starts at the new HOD/LOD that armed the leg; the anchor/stop is only the leg's start + your risk, not the thing measured from.
   - *(Range, not close — the wick is real travel. Z-score over ATR — ATR is a laggy averaged speed; the live candle range reads instantaneous velocity and its acceleration, which is what marks the blow-off.)*

3. **Get flat on the entry TF.** Once exhaustion is present, drop to the timeframe you entered on and exit on its **bar break** (wick-through the prior entry-TF candle) — the objective trigger to get out *into* the exhaustion rather than guessing the top.

**Ordering:** gate trail runs throughout → gate range-velocity exhaustion confirms the climax → entry-TF bar break executes. **Bar-break arms, range-velocity exhaustion fires — in that order** (strict, no override).

**Two outcomes:** leg **blows off** → range-velocity exhaustion fires → exit into the climax. Leg **fades** (no climax) → the **gate bar-break trail is the exit.**

**Notes:** candle-range velocity is an exit signal for a position already held — never a standalone detector or entry filter. A "break" = **wick-through** (a wick beyond the prior candle counts), consistent with measuring velocity on the full candle range.

**Discretionary overlays:** price *closes* through the gate 9-SMA; visible exhaustion (long wicks, dying volume); opposite Type 2 signal fires against you on the entry TF.

---

## Still open (calibration — needs real stocks-in-play data)

1. **The Z baseline for candle range** — lookback length + what "context" means (time-of-day / regime / per-name vs pooled).
2. **The threshold** — which Z-range / ΔRange reading counts as "exhausted, get flat."

Everything else — entry, stop, filters, sizing, exit logic — is defined. These two are numbers to fit from data, not design holes.

---

## Refined pullback entry (PROVISIONAL — drafted 2026-06-01 from the DELL session)

> Status: **provisional, unvalidated.** This is a sharper articulation of the entry above, not a replacement. Every threshold here is a hypothesis until backtested. The slope-cross entry above still stands as the "confirmed" variant.

**Core idea:** the cascade pullback entry is **trend-following on the gate, mean-reversion on the entry TF.** The higher TF picks direction; the entry itself fades a small-TF stretch back to its mean, *in the trend's direction.* Naked mean-reversion is a coin flip; trend-gated mean-reversion is the edge — you only fade dips the higher trend will refill.

**The trigger sequence (long; flip for short):**
1. **30m up** (day bias intact).
2. **5m (gate) wick touches its 9-SMA**, slope **flat-ish** (decelerating, not steeply down). Touch = the **wick/low** reaching the SMA, *not* the close.
3. Drop to the **1m** → take the **bar-break** (wick-through the prior 1m candle's high) at the **1m's own leg-2**.
4. **Stop = the touch low** (the stretch extreme). Tight by construction, because you entered at the mean.

**Leg-1 vs leg-2 (the fakeout filter):** a gate pullback runs in legs.
- **Leg 1** = price far from the gate SMA, gate slope steeply against you → **don't touch** (knife / flag-fail).
- **Leg 2** = price near the gate SMA, gate slope **flattening**, and the stretch *shrinking even as price makes a marginally lower low* (decelerating momentum) → **this is the trade.**

**Two entries into the same pullback:**
- **Aggressive** = the touch + 1m bar-break (early, at the mean, tight stop, less confirmed).
- **Confirmed** = the original 1m slope-cross with the gate up (later, wider stop, more proven).
- Run them as a scale (starter on the break, add on the cross) or use the cross as a second shot if the break is missed. **For *live* trading prefer the bar-break** — the slope-cross lags and invites reaction-lag on top (the DELL fill came in ~$4 above the bar-break level for this reason).

**Gate cycle position decides which trade it is (and the size):**
- **Gate behind you** (5m has completed its pullback / touched / realigning) → **CORE**: full size, long runway, hold the leg.
- **Gate ahead of you** (5m hasn't pulled back yet — you're *between cycles*) → **SCALP only**: the signal can still be valid, but the runway is short (the upcoming gate pullback is the ceiling), so the **EV is compressed** → small size, tight stop, quick target. Short runway + wide stop = pass.

**Touch depth = size dial:** full touch / pokes through the gate SMA = deep **Type 2** = full size; shallow, never quite reaches (strong trends pull back shallow) = **Type 1** = small only. Don't bend "almost touched" into a touch — that's discretion creeping back in.

**Fractal note:** this entire structure is scale-invariant — it runs on any adjacent TF pair (Weekly/Daily/4h, Daily/4h/65m, 4h/65m/30m, … 5m/1m/10s). Pick the pair by **account size, daily stop, and hold tolerance**, not by the chart. Don't keep zooming past your floor — edge dies in microstructure noise (overtrading).

**Still to calibrate (backtest these — don't guess live):**
1. The **flat-ish** band for the gate slope (what counts as "decelerated enough").
2. The **stretch** metric — % from SMA, z-score (consistent with the exit's z-scored range), or an ATR band.
3. **SMA vs EMA** (and length) for the 9-period line — EMA cuts lag but adds whipsaw; decide by data, not instinct.
