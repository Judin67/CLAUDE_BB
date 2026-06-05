# JJ (VwapTrader1) — Market-Maker Playbook

> Reference doc: how a former penny-stock market maker says the low-float game
> actually works, distilled from JJ / **@VwapTrader1** ("Confessions of a Market
> Maker"). Source for the supply-side mechanics the dilution card + scanner model.
>
> **Status:** built from SteadyTrade **Ep 179**, **Ep 187 (GME)**, and the
> **Face2Face "Gorilla Trader" strategy** interview (all extracted). Still to fold
> in: "Interview With A Market Maker: Wild Stories" (yt `pmnJTVc-ih0`) — needs transcript.
>
> Attribution: **[JJ]** = directly his; **[L2 lore]** = corroborating trader knowledge.

---

## Who he is
~20-yr **penny-stock market maker** (MMID-level operator). Took **200+ companies public**, traded billions. Bouncer → phone sales → MM desk → (after a heart attack) retail educator. Co-hosts *Confessions of a Market Maker* with Ray. Frame: *"Wolf of Wall Street meets retail trading."*

## The doctrine (one line)
> **[JJ] "Trading is all about SUPPLY. Demand is artificially created."**
His desk job: **add liquidity so holders of cheap/free stock could sell it higher.** Retail sees volume + rising price → **chases** → MM **slams them with supply.**

There are **two kinds of buying**: real investment vs. **artificial price-driving** in penny stocks. **[JJ]**

---

## The MM manipulation toolkit (Ep 179, timestamped)

- **Bid-manipulation cycle** (~24–30:00): bid the market UP to attract retail → **pull the bids to trigger stop-losses** → repurchase lower. Rinse/repeat. **[JJ]**
- **Supply removal → vacuum rally** (~35:00): **pull all supply** to manufacture demand and force a **parabolic** move, then **suddenly dump supply back** into the chase. **[JJ]**
- **Wash trading** (~05:00): open multiple brokerage accounts, **wash-trade between them to manufacture volume** (the "activity" that pulls retail in). **[JJ]**
- **Wiping bids / lifting offers** (~30:00): aggressive order moves to clean out / reload inventory. **[JJ]**
- **Orchestrated squeezes** (~10:00): clients **wire funds to the MM's offshore account with specific buy instructions** → engineered squeeze. **[JJ]**
- **End-of-month squeezes** (~15:00): MMs **back away from offers** so they're not "offside" on inventory at marks → forced pop. **[JJ]**
- **Played Level 2 like a personal chessboard** — move orders/supply/price at will. **[JJ]**
- **Spoofing / fake walls** — large fake bids/asks to fake supply/demand, cancel after price moves. **[L2 lore]**

---

## Ep 187 — GME, PFOF & the plumbing

- **Payment for order flow (PFOF) [JJ]:** brokers route retail orders to MMs (e.g., Citadel); if the MM lacks inventory it **short-sells to fill you** → the MM **profits by shorting and pushing price down**. PFOF was pioneered by **Bernie Madoff**; now a core MM profit engine.
- **MMs short into retail [JJ]:** after a downturn they sell short to retail, then **cover on the bounce** ("buy back lower"); shorting also gives leverage to **drive price up**. Algos simplified the liquidity role.
- **Engineer squeezes by restricting DTC supply [JJ]:** *"simply removing supply can cause price to go up."* Withhold lendable supply at the DTC → squeeze (same supply-removal logic as the vacuum rally, at the settlement layer).
- **GME read [JJ]:** retail buying that *should* lift price but doesn't → **someone is selling into the buying** (insider/structural) — possibly a **distraction while other actions happen behind the scenes.** Robinhood's halt = DTCC collateral/infrastructure couldn't handle the surge, not a favor to retail.
- **Float caution [JJ]:** **check SEC filings for float — don't trust float figures alone** (reported ≠ tradable). ← validates the card's "shares-outstanding + verify true float" caveat.
- **Tell [JJ]:** *"there's always some manipulation happening"* — read price action via **TPO / market-profile**; learn market structure first.

---

## JJ on GME & the deal machine (Wall Street Coach pod — w/ Kim Ann Curtin)
> JJ confirmed here: heart attack + quintuple bypass → "grew a conscience," hides his face (still has live clients), nightclub bouncer → "gorilla of Wall Street."

- **Why GME ran [JJ]:** GME filed a **424B (Dec, w/ Jefferies) to sell up to $100M** common. Funds taking down a deal **pre-short their allocation** (take $20M → short $10M) → *that's* the "huge short interest." **Not an engineered squeeze — it happened because funds pre-shorted the offering.** *"Every time you give a company money you short their stock — the CEO runs through money like poop through a goose."*
- **The MM's real job [JJ]:** create **liquidity for insiders (tens of millions of free shares) to sell into.** GME = an MM's "wet dream" of liquidity; someone **"unloaded dump trucks of stock into the retail buying"** or it'd be "$1000 bid." Math: *"sell 5M people 100 shares at $5 = beautiful liquidity to sell into."*
- **Backdooring [JJ]:** insiders **sell behind shareholders' backs from a long position, then blame short sellers.** *"Every deal has a back door — sell quietly or people stop buying."* (Stratton Oakmont / Fiero brothers.)
- **Orchestrated squeezes [JJ]:** he was **paid to engineer short squeezes** so insiders could liquidate into them. Clients took down **3 clearing firms** ("for fun"); one ran deals **from jail** with $100M waiting.
- **Dollar-volume / 30% rule [JJ]:** tracks **dollar volume; his job = be ~30% of it.** GME $4B/day → liquidating accounts "better have $1.2B." *"Come in, take money out, and you don't know I was there — that's real trading."*
- **OPM [JJ]:** 200+ deals — give CEO $5M, months later he needs more (penthouse, S-class). Public IBs use **other people's money** → don't care what they fund.
- **Vancouver/offshore routing [JJ]:** promoter holds position in **Switzerland/Cayman/Hong Kong → routes through Canada → into the US.** ← validates the **🇨🇳/Cayman domicile flag**. Hedge funds now do the same in small caps ($5→$20).
- **Pirate MM / robbing order flow [JJ]:** $1 promo stock → sell 100k at .97 → **slam all bids down to 60¢** → **nominee bids 100k at 60¢** → 40¢×100k in ~15 min. Trade ahead of sell-offs.
- **PFOF [JJ]:** Madoff-pioneered. MMs short to fill you, buy back on the bid for the spread (millions×/day); **drop bids at EOD because day traders MUST exit**; brokers double-dip (commission + PFOF). Money-laundering plausible at $8–9B/day ($200–300M slips through unseen).

---

## How dilution is distributed (the core tell)

- **[JJ] "Outside supply doesn't care about price — only LIQUIDITY."** Promoters/clients with free/0-cost stock just need **volume to sell into**. → that's *why* catalysts/PR are manufactured: to create the demand to dump into.
- **The capped-tape tell [JJ/L2]:** when a **diluter is on the offer**, you see **massive volume on the ask but price won't advance** — they have a fixed block to move and **won't let it lift until it's gone.** When the offer finally **clears/lifts → supply exhausted → the real move.**
- **Hidden size [L2]:** MM *shows* 10k on the offer but actually sells **hundreds of thousands** (displayed size is a lie / iceberg).
- **The stock's source [JJ]:** *"0-cost stock sold by mysterious offshore companies"* → the **foreign/Cayman domicile + financier/placement-agent** layer.
- **Dilution MMIDs [L2]:** recurring distribution conduits — **VFIN** (Vfinance; makes markets in 6,000+ names, ~15B sh/mo), **VNDM, PERT, VERT**, plus lore list (ACAP, AGIS, BAMM, CLYP…). **NITE/ATDF/ETRF/ARCA** = retail routing flow.
- **Ownership illusion [JJ]:** retail doesn't "own" the shares — they're held by the **nominee for the DTC (Cede & Co.)**; matters for locates/lending/settlement.

## VWAP (his namesake)
- **[JJ/L2]** VWAP = the **institutional execution benchmark** (buy below / sell above). MMs manage **inventory** around it; algos **defend VWAP** in a trend (pullback = fair-value refill).
- In a low-float run, the **diluter distributes around/above VWAP**. **VWAP reclaim = demand still absorbing; VWAP loss after a run = distribution winning.**

## Absorption vs. exhaustion
- **Absorption:** steady large orders, **price doesn't move** (liquidity not disrupted) = stealth distribution (the capped tape above).
- **Exhaustion:** move runs out of fuel → reversal. The diluter's block is **gone** → cap lifts → price jumps to find new supply.

## His actual trading method now (market profile + VWAP) — Face2Face
- **VWAP + standard-deviation bands** — institutions execute above/below VWAP; SD bands mark **acceptance vs rejection** zones.
- **Market Profile / TPO** — the **value area** = where ~70% of volume traded (fair value); **cost-basis levels** = where sellers exited profitably (overhead supply).
- **Balance ranges** — find the balance/rectangle zone; **double the range to project the next target**.
- **P-profiles = trapped shorts**, **B-profiles = trapped longs** — the squeeze/flush setups.
- Identify **supply levels for shorting**; markets are **algorithmic** → math + structure over indicator-soup; focus on **inventory**.
- Background color: Indian roots, born Sri Lanka, raised Canada; cut his teeth in the **Vancouver** penny-stock world (offshore accounts to hide shorts, "moving market makers like chess pieces").

## Video 4 — "Reaper" (David Hanlon interview) — a DIFFERENT ex-MM (25 yrs)
> Note: this interviewee is **"Reaper"** (the grim-reaper-avatar guy), NOT JJ. Different bio, same world. Richest concrete source. (Transcript captured through ~51:00; tail pending.)

- **95% of MMs trade off orders, zero proprietary = riskless.** Hook into an institutional order (hedge fund hands you millions of shares) and work it.
- **The morning routine (controls the stock 9:15–~9:50):** pre-9:30 buy 300–400k in 50k/100k lots to test impact → at 9:30 **pound buy, knee-jerk price as high as possible** → 10 sec pre-open knee-jerk higher → at open **sell to the client + pull the bid → "back and fill" collapse** → **cover on the pullback.** Daily. Retail market orders = "license to steal." **→ never trade 9:00–9:30.**
- **Opposite-side tell:** *on the bid = they're really selling; on the offer = really buying.* Sits on the offer **showing size while buying via ECNs**; will dump 25–30k hitting bids to **start a downside panic.**
- **Tiny-print tell:** 20–30 consecutive 5/10/20-share prints = manipulation to coax sellers (a buy tell).
- **Stop hunting (confirmed):** they see & trigger stops then rip it back. Worth hunting **~$75k+ accumulation**; **<$25–50k ignored.** Use **mental stops + ready sell orders**, not hard stops (esp. OTC). Everyone's stops cluster at the obvious chart level → they plow it.
- **ECNs hide identity** (ARCA biggest/best fills; BATS by Knight/NITE). **Hedge funds use dark pools** (3–5M blocks), never show names; route via Citadel/NITE or sales traders.
- **Naked shorting = real** (98% biotech, cover same day/before settlement; "SEC knows, can't stop it").
- **ATM dilution (his last 10 yrs):** took biotechs' stock and **sold into the catalyst** to raise $10–100M. ("Lying thieving bankers.") = the dilution card.
- **OTC easier to manipulate than listed**; **PUMA** takes prop positions / "in bed with companies"; Citadel/NITE huge OTC flow.
- **PFOF/fills:** commission-free brokers sell flow → price trades *through* your limit unfilled; houses **cross** internal buyer/seller at your price.
- **How he trades now:** candlesticks (Nison) + Level 2; patient sniper, bids out, rarely chases; **alerts set night before within 5¢ of levels**; IBKR+Webull; **base hits, cut losses.** Tools: **whale wisdom** (13D/G >10%), tipranks, barchart, benzinga.

## The plumbing he says retail ignores
**T+1/T+2 settlement · inventory · locates · order routing · DTC/Cede.** Edge = knowing **who's on the other side and why** (the structural seller), not just the chart.

## How retail should orient (his advice)
- Focus on **supply/demand and price levels**, read **structure + who owns the float** (prefer real institutional ownership over fishy penny-float figures).
- Be the one who **sells into the manufactured demand**, not the one chasing it. Losing is usually **cycle-position** (chasing the parabolic he engineered), not direction.
- He steers beginners toward **micro futures** (no dilution / no offshore 0-cost supply) and away from offshore brokers.

---

## Complementary: the short-seller's side + Ortex data (The Friendly Bear / David)
> The other side of the table — how a pro retail short-seller *profits* from the above, and the data he uses. Sources: "90% Win Rate" strategy video + Ortex interview (James Kozinski).

**Short-seller stock-selection checklist [David]:**
- **Avoid float < 1M** (too manipulatable). **Premarket volume rotation = red flag** (✅ our card).
- **Borrow fee rate** (IBKR + aggregator) to reverse-engineer short interest; high/rising = crowded/squeeze risk.
- **Avoid >40% institutional ownership** (can't compete with algos).
- Check **insider lockup expirations**, **cash position**, **ATM offerings** (✅ dilution side).

**Ortex — the squeeze data layer [James/Ortex]:**
- **Daily estimated short interest** (ML over ~85–90% of securities-lending data) vs FINRA twice-a-month/7+ day lag; plus **live intraday SI** (~70% coverage: borrowed/returned/net).
- **Cost-to-borrow** (min/max/**average** — average matters); **utilization** (% lendable on loan, ~100% = none left); **% free float on loan**; **days-to-cover**; **shares on loan**; **FTD/threshold**.
- **Short Score (0–100)** — blends est. SI + CTB + utilization **vs the stock's own history**; high = primed for squeeze (an indicator, not raw SI).
- Caveat: on-loan ≠ always shorting (tax/dividend); CI widens on unusual days. CSV/**API (paid)** — the upgrade path for our squeeze block.

## Mapping to the WAT stack

| JJ concept | Have | Add |
|---|---|---|
| Supply > demand; structural seller | ✅ dilution card | — |
| 0-cost offshore stock | ✅ 🇨🇳/🌐 domicile + financier DB | — |
| Manufactured catalyst = exit liquidity | ✅ catalyst line | cross-ref catalyst date vs offering date |
| Float rotation = the churn he sells into | ✅ premarket rotation | — |
| Capped-ask absorption ("vol up, price flat") | ⚠️ | **absorption/distribution detector** (1m/10s vol-vs-range) |
| Supply removal → vacuum rally → dump back | ⚠️ | flag thin-offer vacuum + sudden supply return |
| VWAP as distribution/defense line | ✅ charts | **VWAP posture line on card** |
| Dilution MMIDs (VFIN/VNDM/PERT/VERT) | ❌ no L2 feed | **MMID watch** (ties to luld_scalp_infra: Massive WS + IBKR) |
| Supply exhausted = trigger | partial (Cascade exit) | **"block gone" exhaustion flag** (= locate_exhaustion) |

## Build ideas straight from his playbook
1. **Absorption/distribution detector** — quantify "huge volume, no price progress at a ceiling" from 1m/10s bars (vol z-score high + range compressed under a level). Pure Polygon, buildable now.
2. **VWAP posture** on the card (above/below · reclaim/loss after a run).
3. **MMID dilution watch** — flag VFIN/VNDM/PERT/VERT when present (needs Level-2 feed).
4. **Supply-exhaustion trigger** — the persistent offer finally clearing = squeeze ignition.
