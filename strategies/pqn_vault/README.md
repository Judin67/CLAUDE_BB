# PQN Strategy Vault — index

> 66 strategies from the PyQuant News *Alpha Strategy Vault* (pro.pyquantnews.com), saved as Google Docs in
> the Drive folder [`PQN strategy vault`](https://drive.google.com/drive/folders/1Fm8yz5CU-pXE9F3OgR_MmOqr4qOhbrpM). Triaged 2026-09-14 against Massive (Polygon) + free SEC EDGAR.
> **This file is generated** by `python tools/vault_index.py index` from each page's front matter — do not hand-edit.
> Edit the page, then rerun. One page per strategy, all the same shape. PQN's rules are kept as written and never
> blended with Judin's own models (Cascade / Dr. S / low-float stack).

**66 strategies · 52 buildable · 3 partial · 11 blocked · 0 built · 0 backtested**

## How to use this folder
- **Find a strategy:** the table below. ID → page (rules, data map, open questions, status) → PQN doc (full write-up + pseudo-code).
- **Status lives on the page** (front matter): `data_status` buildable/partial/blocked · `build_status` not started/built/backtested · `verdict` keep/dead/indicator only.
- **Backtest a strategy:** put that ONE strategy on `PROJECT_QUEUE.md` first (WIP = 1), resolve its *Open questions* with Judin, run the open checks its tier needs, build as a `tools/` script, and land outputs in `results/<ID>/` ending in `tools/backtest_eda.py`. Then set `build_status` on the page and rerun `index`.
- **Data map, known traps, open checks, build checklist:** [`workflows/pqn_strategy_vault.md`](../../workflows/pqn_strategy_vault.md).

## Scoreboard
| Tier | Meaning | Count |
|---|---|---|
| A | ETFs, price only | 11 |
| B | Calendar timing | 8 |
| C | Single stocks, price + market cap | 12 |
| D | Single stocks + fundamentals | 12 |
| E | Short interest | 2 |
| F | Earnings-date event studies | 4 |
| G | EDGAR filings | 2 |
| H | Options | 1 |
| P | Partial / heavy lift | 3 |
| X | Blocked | 11 |
| **Total** | | **66** |

## All strategies
| ID | Name | Tier | Data | Build | Verdict | Doc | Page | Results |
|---|---|---|---|---|---|---|---|---|
| A1 | Asset Class Trend-Following | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1JglHYFlMP9VWnPT7uHqczP59x5Nft6evbbvw_FhOHMo) | [page](A01_asset_class_trend_following.md) | — |
| A2 | Momentum Asset Allocation | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1kN8RzAnnSj-pB-DfM5CgHTunXulrX-mpeg7j_ZyBRaI) | [page](A02_momentum_asset_allocation.md) | — |
| A3 | Sector Momentum – Rotational System | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1a_TrkiN1ZFNWx6D9ZpEQkwNGlza5pYnREeKvSsvVDa0) | [page](A03_sector_momentum_rotational_system.md) | — |
| A4 | Industry Momentum – Riding Industry Bubbles | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1wbZoB7rb2gKncGuYCkAsWooHJMdE2-EtBoMdhg1WxDU) | [page](A04_industry_momentum_riding_industry_bubbles.md) | — |
| A5 | Momentum Factor and Style Rotation Effect | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1uTaBrM1b8uBAlTCfA03J52atKW4l4WXD8yZnCbn4-GM) | [page](A05_momentum_factor_and_style_rotation_effect.md) | — |
| A6 | Paired Switching | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1_6rfZ8GuIf3KTHkPWz69aBWxZ6FHZZDdUHb3NSLBess) | [page](A06_paired_switching.md) | — |
| A7 | Momentum Factor Effect in Country Equity Indexes | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1piimfk9FbbbethjO9JRWtxzow3wHsWgCKzXrlzO3rEE) | [page](A07_momentum_factor_effect_in_country_equity_indexes.md) | — |
| A8 | Betting Against Beta – International Equities | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1EJxooz0QLoHpCUED8ZFV1G5avR0PcUtoGuJxVPrIzqQ) | [page](A08_betting_against_beta_international_equities.md) | — |
| A9 | Pairs Trading with Country ETFs | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1NaTrxGmqhb1mKFErgoIhLktCcVVARVlyDz11okL3Hxg) | [page](A09_pairs_trading_with_country_etfs.md) | — |
| A10 | Reversal Effect in International Equity ETFs | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1vJc7mrxIWouW92oZpB-chb8FvuRdL-TG-KJZt2jLeko) | [page](A10_reversal_effect_in_international_equity_etfs.md) | — |
| A11 | Crude Oil Predicts Equity Returns | A | buildable | not started | — | [doc](https://docs.google.com/document/d/1vWZeA2aGAAhQ1-zru-zN91Jf86pRFcyxbGsAjSB9X9U) | [page](A11_crude_oil_predicts_equity_returns.md) | — |
| B1 | Turn of the Month in Equity Indexes | B | buildable | not started | — | [doc](https://docs.google.com/document/d/155xMH35zOooazrZtnWIv_lOYaCAbUcNvEfPUN6s5cUM) | [page](B01_turn_of_the_month_in_equity_indexes.md) | — |
| B2 | Payday Anomaly | B | buildable | not started | — | [doc](https://docs.google.com/document/d/11iKmTCPy2mpSm3Qq7O-HPkHOABwNSSWmceOaTHZnrj4) | [page](B02_payday_anomaly.md) | — |
| B3 | Pre-Holiday Effect | B | buildable | not started | — | [doc](https://docs.google.com/document/d/14zmrK7AL44Jaui7IGrOa0G0YrY7NwQLqpkrLxbeqM2A) | [page](B03_pre_holiday_effect.md) | — |
| B4 | Market Seasonality Effect ("Sell in May") | B | buildable | not started | — | [doc](https://docs.google.com/document/d/1QyvrMw68hQbO6zLMTT0Z3A2Yrh2w8Snubm1MuHzVlI8) | [page](B04_market_seasonality_effect_sell_in_may.md) | — |
| B5 | January Effect in Stocks | B | buildable | not started | — | [doc](https://docs.google.com/document/d/1emd4lCGTKUzwLO6eaBAF9KXuf__KwveLJ-ZVQPEnsg0) | [page](B05_january_effect_in_stocks.md) | — |
| B6 | January Barometer | B | buildable | not started | — | [doc](https://docs.google.com/document/d/1ssGNLSlF8xhMI01JS_y532ilXBt7yL2yVzVamAfpr40) | [page](B06_january_barometer.md) | — |
| B7 | Option-Expiration Week Effect | B | buildable | not started | — | [doc](https://docs.google.com/document/d/1BNgEtbfsQ7PxprkF6t9_bIAGfiqhqXdVVI03IZcqh_4) | [page](B07_option_expiration_week_effect.md) | — |
| B8 | FOMC Meeting Effect in Stocks | B | buildable | not started | — | [doc](https://docs.google.com/document/d/11-bvVVTK2mwZZPnObZ9N2t23GOtiAe_8MRUMS2LjawI) | [page](B08_fomc_meeting_effect_in_stocks.md) | — |
| C1 | Momentum Factor Effect in Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1WAFaqL8mcwO6NX0gzM3KSgGXXoo1t9JpoU2P3_UZkcE) | [page](C01_momentum_factor_effect_in_stocks.md) | — |
| C2 | Momentum Effect in Stocks in Small Portfolios | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1k3H-LCs2Ivh397m9ymtzdYa9vdMnapqaX1C-h7nlZrU) | [page](C02_momentum_effect_in_stocks_in_small_portfolios.md) | — |
| C3 | Consistent Momentum Strategy | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1ituRqBq-sZ8ufV2S2cKHSrAvoeeDGbMRWI_ZXJ6aXBc) | [page](C03_consistent_momentum_strategy.md) | — |
| C4 | Momentum and Reversal Combined with Volatility Effect | C | buildable | not started | — | [doc](https://docs.google.com/document/d/17Futo0lXZWY8N1rv8_MF4Z6ctzwc3n9H2D9NAgRFbjw) | [page](C04_momentum_and_reversal_combined_with_volatility_e.md) | — |
| C5 | 12 Month Cycle in Cross-Section of Stock Returns | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1caLFzVMFjjWbJ-1Kv5JPnH6yGXoMFxcibTA_kXzGteY) | [page](C05_12_month_cycle_in_cross_section_of_stock_returns.md) | — |
| C6 | 52-Weeks High Effect (industry version) | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1wFWGfx_m4bkebNVzYgpNiXhMs2gDCrkjPcRBz_MsjGg) | [page](C06_52_weeks_high_effect_industry_version.md) | — |
| C7 | Low Volatility Factor Effect in Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1dKtSYcmOGPTT17oaQhM4sB1ZboFT0jHL3wwN76CMA-U) | [page](C07_low_volatility_factor_effect_in_stocks.md) | — |
| C8 | Betting Against Beta Factor in Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1L01M0INDTtNl8qy81L9VLr74vzpOIz_Nkxw2G1hKgiE) | [page](C08_betting_against_beta_factor_in_stocks.md) | — |
| C9 | Short Term Reversal Effect in Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1ppuNA000L-wRst1Jx_kTStU6ybL_OUJabVQNLxW9KcI) | [page](C09_short_term_reversal_effect_in_stocks.md) | — |
| C10 | Trend-following Effect in Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1JiPCN6xHibzCSvx_W21AtXDOXEF84XWKrwZk6pOGUyA) | [page](C10_trend_following_effect_in_stocks.md) | — |
| C11 | Pairs Trading with Stocks | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1QBZVjCiggvYe3DAKN2x3Tl2j43cv0K-ozC354Sabs5Q) | [page](C11_pairs_trading_with_stocks.md) | — |
| C12 | Size Factor – Small Capitalization Premium | C | buildable | not started | — | [doc](https://docs.google.com/document/d/1NpfkhRi_DLDPAoOmIqEaJIfrHahc-A3VgX3ApCe0x5g) | [page](C12_size_factor_small_capitalization_premium.md) | — |
| D1 | Value (Book-to-Market) Factor | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1rvA0z6KY0twu2K9ZbOdzJ_ScvIXyEJ_vMDp1yQCVwNA) | [page](D01_value_book_to_market_factor.md) | — |
| D2 | Asset Growth Effect | D | buildable | not started | — | [doc](https://docs.google.com/document/d/11RHEq9lQkEimz7fAjgZpt5X3lXGCONi8qQBww35W_jQ) | [page](D02_asset_growth_effect.md) | — |
| D3 | Investment Factor (CMA) | D | buildable | not started | — | [doc](https://docs.google.com/document/d/15DttfkACMYhA4rNcibxfy2qy-Oon-RQXWNlf-LH7J5s) | [page](D03_investment_factor_cma.md) | — |
| D4 | Momentum Factor Combined with Asset Growth Effect | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1_9Be-PKr5juaZXS_8VfMRTGLpYDgkXDkzxxy64DfQaY) | [page](D04_momentum_factor_combined_with_asset_growth_effec.md) | — |
| D5 | ROA Effect within Stocks | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1JetnwYgOyYanbeZAGcjmgXtojvd2fCWYMz4B6P9Do6Y) | [page](D05_roa_effect_within_stocks.md) | — |
| D6 | Earnings Quality Factor | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1aJpl6FvBcxZTuHdOA94lFGiyQ64YWlrSOnxIatZnuH0) | [page](D06_earnings_quality_factor.md) | — |
| D7 | Accrual Anomaly | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1BLjB3B_Kmr0KOrMBviA-sP8skTmIdkfQtiAvP7aLeC4) | [page](D07_accrual_anomaly.md) | — |
| D8 | Net Payout Yield Effect | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1cQVy6bz5z-QL_TrEo4kWVLG8sPI36udDKF8cy3Zt1Lo) | [page](D08_net_payout_yield_effect.md) | — |
| D9 | Net Current Asset Value (NCAV) Effect | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1GXr0uF0mllBBNy-tzk9JAgnRJbRbQ_NUdhW9y2WWfBE) | [page](D09_net_current_asset_value_ncav_effect.md) | — |
| D10 | R&D Expenditures and Stock Returns | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1vtXza48RFncO9Dbe2kBtj8e6DbR-SSwcxKEZM8FopHQ) | [page](D10_r_d_expenditures_and_stock_returns.md) | — |
| D11 | Combining Fundamental FSCORE and Short-Term Reversals | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1w7AsVp92FeMId7eG0-_jGLmEnaCj_9VY6vu8PpXVbRc) | [page](D11_combining_fundamental_fscore_and_short_term_reve.md) | — |
| D12 | Residual Momentum Factor | D | buildable | not started | — | [doc](https://docs.google.com/document/d/1eFzpWCTXd2TXcmjPFDhdkhLle_ArmG6l_WYL84zwfic) | [page](D12_residual_momentum_factor.md) | — |
| E1 | Short Interest Effect – Long-Short Version | E | buildable | not started | — | [doc](https://docs.google.com/document/d/1ixWnVQrQvhdlXDx8IMHPNL2fk3DZjcawb8KHsx0AEVg) | [page](E01_short_interest_effect_long_short_version.md) | — |
| E2 | Short Interest Effect – Long-Only Version | E | buildable | not started | — | [doc](https://docs.google.com/document/d/194GKwEsOT-xyir1tbNAhZujQLjN3o0CAhN9s_0fp9TQ) | [page](E02_short_interest_effect_long_only_version.md) | — |
| F1 | Post-Earnings Announcement Drift (PEAD) | F | buildable | not started | — | [doc](https://docs.google.com/document/d/1rGfek7rRYiz8DHOnVCebpxRD65s36ypOYYJahrixCnE) | [page](F01_post_earnings_announcement_drift_pead.md) | — |
| F2 | Earnings Announcement Premium | F | buildable | not started | — | [doc](https://docs.google.com/document/d/1EKf9S4WSsLaUU2chH2upgp24jAEMB8_w-THi_0s5otM) | [page](F02_earnings_announcement_premium.md) | — |
| F3 | Reversal in Post-Earnings Announcement Drift | F | buildable | not started | — | [doc](https://docs.google.com/document/d/11DwRW_rZJQaxk_4_pjYZU5difFX-zjMrWI2B0-8QYKA) | [page](F03_reversal_in_post_earnings_announcement_drift.md) | — |
| F4 | Reversal During Earnings Announcements | F | buildable | not started | — | [doc](https://docs.google.com/document/d/1j65KQMekLBbpBDwo9pj2pWJctWU631g2Oj4SLdUdXSk) | [page](F04_reversal_during_earnings_announcements.md) | — |
| G1 | Alpha Cloning – Following 13F Filings | G | buildable | not started | — | [doc](https://docs.google.com/document/d/1PF665ifntd6PT8qWqq-LkFr3AVgrEO-krIH3L3ddhUU) | [page](G01_alpha_cloning_following_13f_filings.md) | — |
| G2 | The Positive Similarity of Company Filings and Stock Returns | G | buildable | not started | — | [doc](https://docs.google.com/document/d/1ZIkrPRUwlGoKhFRSG8Cz-paJ1SxYBLxQjE_etVAir-w) | [page](G02_the_positive_similarity_of_company_filings_and_s.md) | — |
| H1 | Volatility Risk Premium Effect | H | buildable | not started | — | [doc](https://docs.google.com/document/d/1ot9RQrzWiUtuRF4t-9lHmhlm017BXk0Tt_145QmeeyE) | [page](H01_volatility_risk_premium_effect.md) | — |
| P1 | Earnings Announcements Combined with Stock Repurchases | P | partial | not started | — | [doc](https://docs.google.com/document/d/10Fa9Fj1588ArDTrlir2pu6QGfEOxUcg_MOCh8kjhacM) | [page](P01_earnings_announcements_combined_with_stock_repur.md) | — |
| P2 | FED Model | P | partial | not started | — | [doc](https://docs.google.com/document/d/1DBOtXeefnB06eCGr2wNXkhKYf8NbahcSJI5vxv3M0I4) | [page](P02_fed_model.md) | — |
| P3 | How to Use Lexical Density of Company Filings | P | partial | not started | — | [doc](https://docs.google.com/document/d/1dbTdnrjQXb6zqWFLkr8s1jFYPJBX3cG63ykPox5NuAg) | [page](P03_how_to_use_lexical_density_of_company_filings.md) | — |
| X1 | Dispersion Trading | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1OHXWMedpBSWXyMlOOOLVllU1g6NA1Tu5jZTRbznaXYo) | [page](X01_dispersion_trading.md) | — |
| X2 | ESG Level Factor Investing | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1h9SDFv2ESZP-fILAj7K4c2GFB4VtoHAPLV4fLHjoLFI) | [page](X02_esg_level_factor_investing.md) | — |
| X3 | ESG Factor Momentum | X | blocked | not started | — | [doc](https://docs.google.com/document/d/12AM9Dk7PlyVgbCg_uztP6iCq2dbymP1EC9k_eBPIFsM) | [page](X03_esg_factor_momentum.md) | — |
| X4 | ESG, Price Momentum & Stochastic Optimization | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1Hb2BZWMPZIaaiWQQUchlpkuGXy3GvfkIH9lIUbg0pNs) | [page](X04_esg_price_momentum_stochastic_optimization.md) | — |
| X5 | Momentum in Mutual Fund Returns | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1u7lc-qkWMmN1XbUSiS0QkgKlWOf3aiByr9Wqt1qpHKw) | [page](X05_momentum_in_mutual_fund_returns.md) | — |
| X6 | Value Factor – CAPE within Countries | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1U5s_n8lAXoV2PQZkvBckNJ_aPNK1SjHlqzHJBcivpwA) | [page](X06_value_factor_cape_within_countries.md) | — |
| X7 | Exploiting Term Structure of VIX Futures | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1GZYAo7AnKY1GmVO5DVnJ1vc_JPsnOJn3yYZTwaeSRrA) | [page](X07_exploiting_term_structure_of_vix_futures.md) | — |
| X8 | Synthetic Lending Rates Predict Market Return | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1uZ2XgTa3gv7R58BwKllYH3qgfrTsNbJKzNJLndXtrto) | [page](X08_synthetic_lending_rates_predict_market_return.md) | — |
| X9 | Time Series Momentum | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1-LsZC0-CwqC466XA7QWhknyG4RKMThfl7mz0ZEFjcFw) | [page](X09_time_series_momentum.md) | — |
| X10 | Short Term Reversal with Futures | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1sCWqIDX8TA93jdBKhC6K3e2zv4Pwi5srQPqe3Fk2pcI) | [page](X10_short_term_reversal_with_futures.md) | — |
| X11 | Soccer Clubs' Stocks Arbitrage | X | blocked | not started | — | [doc](https://docs.google.com/document/d/1LaUBfTeYY_g77Pr0MMdNhHsa7XfEgbOWeLfP9J4FU1E) | [page](X11_soccer_clubs_stocks_arbitrage.md) | — |
