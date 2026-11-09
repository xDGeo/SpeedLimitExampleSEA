# Speed, posted limits and crashes or near-accidents: quantitative models for an advisory panel on an 80 km/h road

Compiled 2026-11-09. Evidence tags on each figure say how I obtained it:

- **[P]** read by me in the full primary source text (PDF text extracted locally).
- **[E]** read in the named source, but through an automated page extractor that returns a summary of the page rather than the raw text. Check before quoting.
- **[A]** only the abstract or catalogue record of the primary source was available.
- **[Q]** not read in the primary. Quoted in the named secondary source, which I did read.
- **[S]** search-engine summary only. The page was not opened or could not be opened, and the link is the best-matching search result, so the attribution may be wrong. Weakest tier, do not cite without checking.

Access failures that shape these notes: the open-access PDFs of Elvik 2013 and Elvik et al. 2019 are on `toi.brage.unit.no`, which did not resolve. The ITF/OECD PDF, NHTSA report, MDPI and ITS Knowledge Resources pages returned HTTP 403. So the **fitted tables of Elvik 2013 and Elvik et al. 2019 were not read directly**, and their numbers below are tagged [Q]. The full text of TOI 1034/2009 also returned 403, but its summary with the complete exponent table was read.

## Nilsson's Power Model: original exponents by crash severity

### Takeaway
Nilsson's classic exponents are 2 (all injury accidents), 3 (fatal and serious accidents) and 4 (fatal accidents), applied to the ratio of **mean traffic speed** after to before. The 2004 thesis gives no exponent for property-damage-only (PDO) or for slight injury as a separate class, and it says the model underestimates fatalities.

### Cited Findings
- Model form: crashes_after / crashes_before = (v_after / v_before)^n, with v = average speed on the road. Stated by SWOV for Nilsson 1982, and by FHWA as LO2 = LO1 × (v2/v1)^n. [P] for [SWOV 2012 fact sheet](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf), [E] for [FHWA-HRT-17-098 ch. 2](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm).
- **All injury accidents, n = 2.** The change in injury accidents "can be regarded as proportional to the square of the relative change in speed". Context: Swedish speed-limit before/after studies. [P] [Nilsson 2004, Bulletin 221, Lund](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- **Fatal accidents, n = 4.** Change in fatal accidents proportional to the fourth power of the relative speed change, derived from the fatal share of injury accidents also scaling with the square. [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- **Fatal and serious accidents, n = 3.** Nilsson says the exponent "should for these accidents be somewhere between 2 and 4" and chose 3. This is a reasoned choice, not an estimated value. [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- **PDO: no exponent in the thesis.** A text search for property damage finds one passage, saying only that the model "ought to include these accidents". [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf). **Slight injury is not a separate class** in the thesis.
- Fatalities: the thesis abstract says the model is valid for injury accidents, fatal accidents and number injured, "but not for the number of fatalities", which it underestimates. Elvik's summary of the proposal: exponent above 4 and below 8 for fatalities, between 3 and 6 for fatal and serious injuries, between 2 and 4 for all injured. [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf); [P] [Elvik, Christensen, Amundsen 2004, TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf).
- Validation case, Sweden 1979, limit 110 to 90 km/h, mean speed 105 to 94 km/h. Observed vs predicted change: fatal accidents -52% (95% CI -90, -10) vs -36%; fatal and serious -34% (-49, -13) vs -28%; all injury -25% (-37, -11) vs -20%. [P] Table 21, [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- Fit against a meta-analysis data set, R²: fatal accidents 0.67 for the power model vs 0.82 for linear regression; all injury 0.69 vs 0.73. [P] Table 24, [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- Nilsson's own scope: the model answers what happens "if the average speed is changed by x %... and everything else remains unchanged". He notes statistical studies of speed in urban areas are rare. [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- The exponents 4, 3 and 2 are not mutually consistent because the categories overlap (fatal accidents are counted in all three). Elvik reformulated them as mutually exclusive classes for that reason. [P] [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf).

### Inferences
- A constant exponent assumes the same percentage effect at any speed. Use it only as a historical baseline, and prefer the updated values below.

### Gaps
- Nilsson 1982 (the original OECD symposium paper) was not retrieved. The 2/3/4 attribution to it is via SWOV and FHWA.

## Elvik's re-analyses and the Exponential Model: coefficients by severity and road type

### Takeaway
Estimates have moved over 20 years and differ markedly by publication, most of all for injury crashes (Power exponent 1.2 to 3.9; exponential β 0.034 to 0.06). Elvik 2009 is the only source I read directly with a full severity-by-road-type table and CIs, and it merges rural roads with freeways. No exponential coefficients by road type were found.

### Cited Findings

**Elvik, Christensen, Amundsen 2004 (TOI 740/2004).** 98 studies, 460 estimates. Modified, mutually exclusive classes, best estimate (95% CI). All road types pooled. [P] [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf)

| Severity | Exponent | 95% CI |
|---|---|---|
| Fatalities | 4.5 | 4.1 to 4.9 |
| Seriously injured road users | 3.0 | 2.2 to 3.8 |
| Slightly injured road users | 1.5 | 1.0 to 2.0 |
| All injured (severity not stated) | 2.7 | 0.9 to 4.5 |
| Fatal accidents | 3.6 | 2.4 to 4.8 |
| Serious injury accidents | 2.4 | 1.1 to 3.7 |
| Slight injury accidents | 1.2 | 0.1 to 2.3 |
| All injury accidents | 2.0 | 1.3 to 2.7 |
| PDO accidents | 1.0 | 0.2 to 1.8 |

**Elvik 2009 (TOI 1034/2009), Table S1.** 115 studies, 526 estimates. Exponents differ between road environments, because they vary with initial speed. [P] for the summary, [TOI 1034/2009 summary](https://www.toi.no/getfile.php/1313212-1259661631/Publikasjoner/T%C3%98I%20rapporter/2009/1034-2009/1034-2009-Sum.pdf). Same table reproduced in [SWOV 2012](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf) [P] and [FHWA-HRT-17-098](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm) [E].

| Severity | Rural/freeway (95% CI) | Urban/residential (95% CI) | All roads (95% CI) |
|---|---|---|---|
| Fatal accidents | 4.1 (2.9, 5.3) | 2.6 (0.3, 4.9) | 3.5 (2.4, 4.6) |
| Fatalities | 4.6 (4.0, 5.2) | 3.0 (-0.5, 6.5) | 4.3 (3.7, 4.9) |
| Serious injury accidents | 2.6 (-2.7, 7.9) | 1.5 (0.9, 2.1) | 2.0 (1.4, 2.6) |
| Seriously injured road users | 3.5 (0.5, 5.5) | 2.0 (0.8, 3.2) | 3.0 (2.0, 4.0) |
| Slight injury accidents | 1.1 (0.0, 2.2) | 1.0 (0.6, 1.4) | 1.0 (0.7, 1.3) |
| Slightly injured road users | 1.4 (0.5, 2.3) | 1.1 (0.9, 1.3) | 1.3 (1.1, 1.5) |
| All injury accidents | 1.6 (0.9, 2.3) | 1.2 (0.7, 1.7) | 1.5 (1.2, 1.8) |
| All injured road users | 2.2 (1.8, 2.6) | 1.4 (0.4, 2.4), CI "specified informally" | 2.0 (1.6, 2.4) |
| PDO accidents | 1.5 (0.1, 2.9) | 0.8 (0.1, 1.5) | 1.0 (0.5, 1.5) |

- Weakness: the CI for rural serious-injury accidents (-2.7, 7.9) includes zero and negative values, so that cell is close to uninformative. Elvik adjusted the "all" rows downward for consistency with the severity-specific rows. [P] [TOI 1034/2009 summary](https://www.toi.no/getfile.php/1313212-1259661631/Publikasjoner/T%C3%98I%20rapporter/2009/1034-2009/1034-2009-Sum.pdf).
- Trend: "tendency for the exponents to become smaller over time". [P] same source.
- **Road types.** Elvik 2009 does not separate freeways from rural roads. Cameron and Elvik 2010 (460 estimates from the 2004 data set, split into urban arterial, residential, rural highway, freeway) found the power for serious casualties on urban arterials significantly below rural highways, and rural highways significantly below freeways. They found Nilsson's model satisfactory for rural highways and freeways but not directly applicable to urban arterials, and found no evidence for monotonically increasing powers with severity on urban arterials. [A] [Cameron & Elvik 2010, AAP 42(6) 1908-1915, record](https://www.science.gov/topicpages/n/nilsson+model.html). Numeric powers by road type not retrieved.

**Exponential Model.** Form: relative accidents = α · e^(β·x), x = mean speed, so crashes_after / crashes_before = exp(β · (v_after − v_before)). [P] [Elvik 2014, TOI 1296/2014, p.1](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf) (in Norwegian); ratio form also in [Ambros & Kieć 2025](https://doi.org/10.1186/s12544-025-00753-6) [P]. Proposed by Hauer and Bonneson 2006 and Hauer 2009, fitted to the Elvik 2004 data [S, snippet of Elvik 2013 text](https://toi.brage.unit.no/toi-xmlui/bitstream/11250/2602719/2/Elvik_10.1016_j.aap.2012.07.012.pdf).

**Elvik 2013 and Elvik 2014.** Table 4.1 of TOI 1296/2014 compares the two fits on data binned by 10 km/h of initial speed. It includes the Elvik 2013 accident results and new Elvik 2014 results for killed and seriously injured. Standard errors in brackets. All [P] from [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf); the accident rows are therefore Elvik 2013 values [Q].

| Dependent variable | Power exponent, unweighted / weighted | Exponential β, unweighted / weighted | R² Exp, unweighted / weighted |
|---|---|---|---|
| Fatal accidents | 4.177 (0.293) / 4.234 (0.587) | 0.069 (0.004) / 0.069 (0.012) | 0.985 / 0.981 |
| Injury accidents | 2.059 (0.140) / 2.124 (0.062) | 0.034 (0.001) / 0.034 (0.001) | 0.996 / 0.994 |
| PDO accidents | 1.856 (0.097) / 1.911 (0.070) | 0.031 (0.002) / 0.032 (0.001) | 0.987 / 0.992 |
| Fatalities (killed) | 3.697 (0.475) / 4.446 (0.403) | 0.060 (0.005) / 0.065 (0.006) | 0.934 / 0.932 |
| Seriously injured | 3.802 (0.279) / 3.795 (0.530) | 0.063 (0.004) / 0.065 (0.008) | 0.969 / 0.971 |
| Slightly injured | 2.367 (0.218) / 2.320 (0.018) | 0.044 (0.005) / 0.039 (0.000) | 0.934 / 0.988 |

- Elvik 2014 then hand-adjusted the coefficients so that predictions matched total counts. Revised β (Table 4.3): killed 0.065, seriously injured 0.061, slightly injured 0.028, injury accidents 0.034 (unadjusted), fatal accidents 0.045. Elvik rejects the revised fatal-accident model because it can predict under one death per fatal accident, so only the killed model is used. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf). Note: Table 4.3 came out of the PDF as split columns. I matched revised values to rows by order, and the 0.028 value is confirmed in the body text.
- Elvik 2013 finding: exponents should vary continuously with initial speed, and the effect of a given relative change is largest at the highest initial speeds. [A] [Elvik 2013, AAP 50, 854-860, DOI 10.1016/j.aap.2012.07.012](https://vbn.aau.dk/da/publications/a-re-parameterisation-of-the-power-model-of-the-relationship-betw).

**Elvik, Vadeby, Hels, van Schagen 2019.** Studies with data fully or partly from after 2000. Both models "fit the data very well", the relationship "remains strong", and it is the same at individual driver level as at aggregate mean level. [A] [AAP 123, 114-122, DOI 10.1016/j.aap.2018.11.014](https://trid.trb.org/View/1569665).
- Best estimates: **Power 5.5 for fatalities and 3.9 for injury crashes; Exponential 0.08 for fatalities and 0.06 for injury crashes.** [Q] quoted from Elvik et al. 2019 by [Ambros & Kieć 2025](https://doi.org/10.1186/s12544-025-00753-6). No CIs or road-type split available to me.
- Elvik's own 2018 slides: fitted traffic speed vs injury accidents as y = 3E-06 x^3.8601 (R² 0.9726) and y = 0.3776 e^(0.0619x) (R² 0.9181). They use exponential coefficients 0.08 fatal, 0.06 serious, 0.04 slight. [E] [Elvik, ICTCT workshop Porto 2018, third-party copy](https://api.sambuz.com/doc/speed-is-an-important-risk-factor-a-comprehensive-and-pdf-document-539697). Attribution of 0.06 and 0.04 to serious and slight is also seen in an Elvik manuscript via snippet, [S](https://core.ac.uk/download/491284529.pdf), where 0.06 and 0.04 are credited to Elvik 2014.

**ITF/OECD 2018.** Only a trade-press summary was available, giving Nilsson-style figures for a 1% speed change: about +2% injury, +3% severe, +4% fatal crashes. [S] [World Highways](https://www.worldhighways.com/news/safer-speeds-required-says-new-report). The report's own tables were not read.

### Inferences
- **Conflict: injury-crash β.** 0.034 (Elvik 2013/2014, Table 4.1) vs 0.06 (Elvik et al. 2019 as quoted). This is about a factor of 1.8 and matters more than Power vs Exponential. Likewise injury exponents run 1.2 (urban 2009) to 3.9 (2019).
- **Conflict: serious-injury β.** Attributions of 0.06 to serious injuries credit Elvik 2014, whose Table 4.1/4.3 gives 0.061 to 0.065 for seriously injured persons. This is consistent. But the same 0.06 is reported by Ambros & Kieć as an injury-crash value from Elvik 2019, which is a different quantity. Treat "0.06" as ambiguous until the 2019 table is read.
- Arithmetic link between the two models (my derivation): near speed v, an exponential β behaves like a local Power exponent n = β·v. So β = 0.08 gives n = 3.2, 4.0, 4.8, 5.6, 6.4 at 40, 50, 60, 70, 80 km/h, and β = 0.06 gives 2.4, 3.0, 3.6, 4.2, 4.8. The 2019 pairs are mutually consistent at a mean speed of about 65 to 69 km/h (5.5/0.08 = 69; 3.9/0.06 = 65).

### Gaps
- Elvik 2013 Table 1 and Elvik 2019 tables, including any CIs for β and any road-type split, could not be read. **No published exponential coefficient by road type was found.**
- Separate freeway exponents with CIs: only the qualitative ordering from Cameron and Elvik 2010.
- Handbook of Road Safety Measures tables: not retrieved.

## Which model is preferred at 40 to 80 km/h, and where do the models disagree?

### Takeaway
Neither model has been declared the winner in this speed band. Elvik's reports say both are usable, with the Exponential better for injury and PDO accidents and for modelling part of the speed distribution. At 40 to 80 km/h the two can differ by a large share for fatal outcomes. Effects become weaker and less predictable at low speeds, especially below about 60 km/h.

### Cited Findings
- Re-analyses by Hauer, Bonneson, and Cameron and Elvik conclude that the effect of a given relative change depends on initial speed, "not consistent with the Power Model". Changes below about 60 km/h tend to have smaller effects than changes above about 60 km/h. [P] [TOI 1034/2009 summary](https://www.toi.no/getfile.php/1313212-1259661631/Publikasjoner/T%C3%98I%20rapporter/2009/1034-2009/1034-2009-Sum.pdf).
- Elvik 2013 as summarised in Elvik 2014: exponential clearly better for injury accidents; roughly equal for fatal accidents, with Power "possibly a little better"; exponential better for PDO. The comparison covered accidents only, not victims. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf).
- Elvik 2014 conclusion: both models are good descriptions and can be used. The Exponential's advantage is that it can estimate effects for part of a speed distribution, for example when the fastest 20% slow down; the Power Model only applies to the whole distribution. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf).
- Elvik et al. 2019 abstract: "The Power Model and the Exponential Model both fit the data very well". [A] [TRID record](https://trid.trb.org/View/1569665).
- R² alone does not decide it. Fatal accidents, relative counts vs speed bin (highest bin = 100), Table 4.2 of Elvik 2014, R² 0.987 Power and 0.985 Exponential. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf):

| Speed bin km/h | Data | Power fit | Exponential fit |
|---|---|---|---|
| 115 | 100.0 | 116.4 | 181.6 |
| 95 | 62.0 | 51.8 | 45.7 |
| 85 | 37.5 | 32.4 | 22.9 |
| 75 | 13.0 | 19.1 | 11.5 |
| 65 | 8.0 | 10.4 | 5.8 |
| 55 | 4.0 | 5.1 | 2.9 |
| 45 | 0.9 | 2.2 | 1.5 |

- Elvik states the Exponential overpredicts the total by 17% and the 115 km/h bin by about 82%. [P] same table.
- Constant-exponent objection: the Power Model implies the same percentage effect from 100 to 80 km/h as from 10 to 8 km/h, which Elvik calls unreasonable. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf).
- Mirror-image behaviour: SWOV's worked examples using Elvik 2009 exponents give a 1 km/h drop from 120 km/h as -3.8% fatalities and -2.9% serious injuries, but from 50 km/h as -5.9% fatalities and -4% serious injuries. [P] [SWOV 2012](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf).
- Low-speed, site-level test: 238 locations in 23 samples, target limits 20 to 50 km/h, mean speed before about 33 to 64 km/h by original-limit category, injury crashes, β = 0.06. Expected and observed crash changes show "almost no correlation" at site level. Overall slope is significantly positive but below 1 (overprediction). Five of nine categories showed no significant relationship, including vehicle-activated signs. The authors say the model output should not be used as a predictive tool for exact values, especially at low speed. No control for traffic volume. [P] [Ambros & Kieć 2025, ETRR 17:59, DOI 10.1186/s12544-025-00753-6](https://doi.org/10.1186/s12544-025-00753-6).

### Inferences
- For an 80 km/h road, Exponential with β by severity is the better default: constant percentage effect per km/h, no blow-up at low speed, and it fits injury and PDO accidents better. Mean speeds on such a road sit around 60 to 80 km/h, which is in the "higher" regime of Elvik's split.
- In the table above the two models err in opposite directions in the band that matters: Power is above the data at 55 to 75 km/h, and Exponential is below it. This is one fatal-accident data set, so it does not show which model is right for other severities.

### Gaps
- No head-to-head test isolated to the 40 to 80 km/h band was found. Ambros & Kieć addresses lower speeds and physical traffic calming.

## Compliance: how much does mean speed move when the posted limit changes?

### Takeaway
A posted-limit change moves mean speed by about a quarter of the change on average (R² about 0.49 across studies), with an observed range of roughly 15% to 55% across the cases below. Adding engineering measures raises it. Whether an advisory display lowers it is my expectation, not a measured result. **No published ratio was found for advisory panels on an 80 km/h road.**

### Cited Findings
- **Elvik et al. 2004 regression:** Δmean = 0.2525 · Δlimit − 1.2204, R² = 0.487, on a plot whose limit-change axis runs from -40 to +40 km/h (the spread of actual points was not extractable). "The change in the mean speed of traffic induced by a change in speed limit appears to be around 25% of the change in speed limit", so about 2.5 km/h per 10 km/h. Mean speed almost always moves in the same direction as the limit. Variation is large. Combining with engineering measures gives larger effects. Police enforcement changes are in most cases below 3 km/h. [P] Figure 23 and the text on pp. 93-94, [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf).
- **Percent ratios, interurban, meta-analysis of 108 results from the Elvik 2004 database:** reductions, mean-speed ratio 0.93 (SD 0.04) vs limit ratio 0.82 (SD 0.04); increases, 1.04 (SD 0.04) vs 1.17 (SD 0.05). [A] [Musicant, Bar-Gera, Schechtman 2016, TRR 2601, 42-49, DOI 10.3141/2601-06](https://trid.trb.org/View/1393349). My arithmetic in percentage terms: reductions about 0.39, increases about 0.24.
- **Modified model directly on limits:** crash ratio = (limit_after / limit_before)^k, k = 0.99 (SD 0.46) for increases and 1.24 (SD 0.44) for reductions, "nearly proportional to the change in speed limit". For comparison the Nilsson power on mean speed was 3.73 (SD 2.61) for increases and 2.81 (SD 0.65) for reductions. Crash severity not stated in the abstract. [A] [Musicant et al. 2016](https://trid.trb.org/View/1393349).
- Sweden: -10 km/h limit gives -2 to -3 km/h in mean speed; +10 km/h gives +3 km/h. [E] Transport Scotland's [National Speed Management Review 2024, Appendix B](https://www.transport.gov.scot/publication/national-speed-management-review-2024/appendix-b-summary-of-literature-review/), citing Vadeby 2018. A presentation seen only as a snippet says +10 gives +3 to +4. [S, itf-oecd docs](https://www.itf-oecd.org/sites/default/files/docs/speed-changes-crash-risk.pdf); that URL returned 403 and may not be the ITF report itself.
- Case data from Elvik et al. 2019, reproduced by Transport Scotland. [E] Mean speed before and after, ratio is mine:

| Study, country, length | Limit km/h | Mean km/h | Mean change / limit change |
|---|---|---|---|
| Long et al. 2006, Australia, 1060 km | 110 to 100 | 99.4 to 97.5 | 0.19 |
| Christensen & Ragnøy 2007, Norway, 393 km | 90 to 80 | 85.1 to 82.2 | 0.29 |
| **Elvik 2013, Norway, 15.6 km** | **80 to 60** | **76.3 to 69.9** | **0.32** |
| Vadeby & Forsman 2018, Sweden, 2831 km | 110 to 100 | 100.5 to 98.4 | 0.21 |

- The Elvik 2013 row is the closest match by speed. It is not the AAP re-parameterisation paper. Elvik 2014 cites an "Elvik 2013" study of winter environmental speed limits on main roads in Oslo, and I infer this row is that study (same author, year and country; not confirmed). If so, it is a short urban main-road case with an environmental rationale, not a rural road. [P for the Oslo description] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf).
- Sweden 1979, 110 to 90 km/h: about 11 km/h mean reduction (105 to 94), ratio about 0.55. Sweden 1967 to 1972: 90 vs 110 limit corresponded to 5 to 7 km/h, ratio 0.25 to 0.35. [P] [Nilsson 2004](https://lup.lub.lu.se/search/files/4394446/1693353.pdf).
- Flanders, 90 to 70 km/h, regional roads, January 2017: **V85** (not mean) 88.1 to 85.3 km/h in the first year (-2.84) and to 79.7 km/h by 2019 (-8.39), ratio about 0.14 short-term and 0.42 long-term. Crash change: accidents -5.5% (CI ratio 0.893 to 1.000), casualties -10.6% (0.853 to 0.937), slightly injured -8.5% (0.870 to 0.962), seriously injured and killed -22.7% (0.679 to 0.880). Conference slides, not peer-reviewed, study period and controls not fully stated. [P] [Lammar, ETSC PIN conference 2024](https://etsc.eu/wp-content/uploads/10_Pascal-Lammar.pdf).
- US: raising 55 to 65 mph gave about +3 mph, and 65 to 75 mph another about +3 mph, a ratio of about 0.3. [E] Kockelman et al. 2006 quoted in [FHWA-HRT-17-098](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm).
- US multi-site: after raising limits, drivers were less likely to exceed them; after lowering, more likely. No consistent crash pattern; 12 segments, freeways to collectors, no numeric speed result on the page. [E] [Kim, Romo, McDonough 2023, AAA Foundation](https://aaafoundation.org/a-multi-site-examination-for-the-impact-of-changes-in-posted-speed-limit-on-traffic-safety).
- New Zealand review: "typically 2-3 km/h per 10 km/h change in limit". Hamilton 50 to 40 km/h residential areas changed mean speeds by 0 to 3 km/h. A road already at mean 43 km/h on a 50 limit may simply land around 40 after a 40 limit. These figures "may be higher-end estimates... owing to publication bias". [P] [Koorey 2019, The Mechanics and Politics of Changing a Speed Limit](https://viastrada.nz/sites/default/files/2019-03/TG2019-ResearchPaper-GKoorey-SpeedLimits-final.pdf).
- Physical measures vs signs (low speeds): zones with signs only are the least effective category. Mean before and after: Zone (limit) 44.4 to 38.4 km/h; vehicle-activated signs 53.8 to 47.7 km/h (n = 10); vertical measures 49.3 to 36.8; horizontal 59.0 to 51.0. [P] [Ambros & Kieć 2025](https://doi.org/10.1186/s12544-025-00753-6). These are limits of 20 to 50 km/h on urban streets.
- Compliance measurement: in one Norwegian study on 80 and 90 km/h roads, 36% of loop-detector data were discarded after quality control. Hours with mean below 60 km/h were excluded as congestion because limits are assumed not to influence speed in congested traffic. [P] [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf), citing Ragnøy and Muskaug 2003.

**Variable and advisory limits**
- FHWA synthesis: VSL success "relies to a significant degree on driver compliance", many US systems are advisory or unenforceable. One agency reported low compliance until enforcement was added. No compliance rates on the summary page. [E] [FHWA-HOP-17-003 executive summary](https://ops.fhwa.dot.gov/publications/fhwahop17003/es.htm); interview material [S, Appendix B](https://ops.fhwa.dot.gov/publications/fhwahop17003/app_b.htm).
- Advisory work-zone VSL, Missouri (uncongested and rural sites): reduced mean speed, speed variance and V85 downstream of the sign in rural sites; average speeds lower with the sign in urban sites. No values on the page. [E] [Edara, Sun, Hou 2013](https://rosap.ntl.bts.gov/view/dot/26306). A snippet reports compliance about eight times greater with the system and notes higher speed variance attributed to the advisory nature of signs. [S](https://publications.iowa.gov/14932). Page could not be opened.
- Advisory VSL on the Padua-Mestre motorway: compliance improved 2 to 8 percentage points by lane when active, with overall compliance moderate. Observational, active vs inactive days. [S, attribution uncertain](https://www.itskrs.its.dot.gov/2025-b01998).
- Swedish E4 near Södertälje, mandatory: compliance "surprisingly high" in dense traffic. Single case. [S](https://kth.se/ctr/news/the-impact-of-varying-speed-limits-on-traffic-conditions-a-case-study-on-the-e4-around-sodertalje-1.1221366).

### Inferences
- Candidate formula, for a road of current limit L0 = 80 and current mean v0:
  - `dv = r * (L_candidate - L0)` and `v1 = v0 + dv`. Default `r = 0.25`, with sensitivity `r = 0.15` to `0.55`. If `v0 <= L_candidate`, set `dv = 0`, because drivers already below the new limit have no reason to slow down (Koorey's reasoning above, not a fitted rule).
  - `CMF_s = exp(beta_s * dv)` for severity s, with `beta` from the 2019 values or the 2013/14 values. Keep both as bounds until the 2019 table is verified.
- Do not use the regression intercept of -1.2 km/h blindly: the passage I read does not explain it.
- Advisory status: the evidence above is mostly for regulatory limits. An advisory panel should get a lower `r` than 0.25 until field data exist. There is no published number to set this; treat it as a calibration parameter.
- Illustrative scenario (my arithmetic, not a finding). Mean v0 = 76.3 km/h (the Norwegian before value above). Values are CMF, 1.0 = no change.

| Candidate limit | r | v1 | Fatalities, Power n=4.6 (2009) | n=5.5 (2019) | Exp β=0.08 | Injury crashes, Power n=1.6 (2009) | n=3.9 (2019) | Exp β=0.06 | Exp β=0.034 | PDO, Power n=1.5 | Exp β=0.032 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70 | 0.25 | 73.8 | 0.858 | 0.833 | 0.819 | 0.948 | 0.878 | 0.861 | 0.919 | 0.951 | 0.923 |
| 60 | 0.25 | 71.3 | 0.732 | 0.689 | 0.670 | 0.897 | 0.768 | 0.741 | 0.844 | 0.903 | 0.852 |
| 50 | 0.25 | 68.8 | 0.621 | 0.566 | 0.549 | 0.847 | 0.668 | 0.638 | 0.775 | 0.856 | 0.787 |
| 40 | 0.25 | 66.3 | 0.524 | 0.462 | 0.449 | 0.799 | 0.578 | 0.549 | 0.712 | 0.810 | 0.726 |
| 70 | 0.55 | 70.8 | 0.709 | 0.663 | 0.644 | 0.887 | 0.747 | 0.719 | 0.829 | 0.894 | 0.839 |
| 60 | 0.55 | 65.3 | 0.489 | 0.425 | 0.415 | 0.780 | 0.545 | 0.517 | 0.688 | 0.792 | 0.703 |
| 50 | 0.55 | 59.8 | 0.326 | 0.262 | 0.267 | 0.677 | 0.387 | 0.372 | 0.571 | 0.694 | 0.590 |
| 40 | 0.55 | 54.3 | 0.209 | 0.154 | 0.172 | 0.580 | 0.265 | 0.267 | 0.473 | 0.600 | 0.495 |

- Direct alternative from Musicant et al.: limit-ratio exponent 1.24 (range ±1 SD, 0.80 to 1.68) for reductions gives crash ratios of 0.85 (0.80 to 0.90) at 70, 0.70 (0.62 to 0.79) at 60, 0.56 (0.45 to 0.69) at 50, and 0.42 (0.31 to 0.57) at 40. The mean limit ratio in the data was 0.82 (SD 0.04), so 70 km/h (0.875) is inside the evidence, and 60, 50 and 40 km/h (0.75, 0.625, 0.5) are extrapolations.
- Compare with the Power and Exponential route at r = 0.25: the injury-crash CMF at 40 km/h spans 0.55 to 0.80. The spread across models is itself the honest uncertainty to expose in the panel's logic.

### Gaps
- Handbook of Road Safety Measures compliance figures: not retrieved; Elvik 2004 is used instead.
- Koorey says "over 200" studies for Elvik 2004, while the report's meta-analysis had 98 studies with 460 estimates. Figure 23's point count was not stated in the passage read. Cite Elvik 2004 directly.
- Direction asymmetry (reductions vs increases): Musicant's percent results differ (0.39 vs 0.24), but Elvik's figure is one pooled slope and Vadeby reports the opposite sign of asymmetry in km/h. No resolution found.
- No field study of a dynamic advisory display at 40 to 80 km/h with published mean speed by displayed value was found. A figure I saw only in a search-tool summary (mean speed -3.4 km/h at an 80 vs 100 km/h display, labelled Danish-derived) could not be traced to a source and is excluded.

## Speed variance: does it have its own effect separate from mean speed?

### Takeaway
Probably yes for crash frequency, but not as a usable formula, and the effect is confounded with mean speed. Elvik 2014 regards the harm of high variation as beyond reasonable doubt, yet explicitly says it cannot yet be expressed as a function, and the affected crashes are probably mostly PDO.

### Cited Findings
- Elvik 2014 (loop-detector era studies after about 2000): high speed variation, especially in dense traffic, increases accidents. Few studies report severity, but most are probably PDO rear-end or lane-change crashes. Studies are too heterogeneous for meta-analysis. It is "beyond reasonable doubt" that high variation is unfavourable, and it is not yet possible to quantify the relationship as one or more functions. [P] (translated from Norwegian) §7, [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf). Same point in the [English summary](https://www.toi.no/getfile.php/1335303-1394518314/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-Sum.pdf) [P].
- Metric: coefficient of variation (SD / mean) is the most suitable and most used. Example from Norwegian automatic enforcement: 8.38/91.18 = 0.092 before and 5.87/85.42 = 0.069 after. [P] [TOI 1296/2014](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf).
- Confounding: Elvik 2004 says mean and variance are often strongly correlated and hard to separate, and the Power Model applies to mean speed. [P] [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf).
- U-shaped curve is suspect: Solomon-style U curves can be statistical or measurement artefacts (White & Nelson 1970, Hauer 2003, and how crash involvement is counted). [P] [TOI 740/2004](https://www.trg.dk/elvik/740-2004.pdf).
- Later Australian studies: faster-than-average vehicles have higher crash rates, slower ones do not (Kloeden et al. 1997, 2001, 2002). Roads with larger variance mostly less safe (Aarts & van Schagen 2006). [P] [SWOV 2012](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf).
- Aggregate correlations between dispersion and crash rate do not imply individual-level risk. Davis 2002 ecological-fallacy argument [AAP 34, 343-346]. [Q] via [TOI 1296/2014 references](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf) and [E] [FHWA-HRT-17-098](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm).
- Limits that are too low may raise variance: artificially low posted limits may increase speed variability on two-lane rural highways, which may be associated with more crashes (Donnell et al. 2016). In Montana, limits 5 mph below engineering-recommended values were associated with fewer crashes, 10 mph below with more fatal-plus-injury crashes but fewer total, and 15 to 25 mph below with no significant association. [E] [FHWA-HRT-17-098](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm).
- Advisory work-zone limits: higher variance has been attributed to some drivers complying and others not. [S](https://publications.iowa.gov/14932).
- Elvik's unified framework uses a normal speed distribution in half-SD bins, sets relative risk 1.0 at the mean, and applies exponential coefficients, which lets a change in variance or truncation be modelled. [E] [Elvik 2018 slides](https://api.sambuz.com/doc/speed-is-an-important-risk-factor-a-comprehensive-and-pdf-document-539697). Its worked 80 to 70 km/h example gives a fatality change from 1.18 to 0.59, which depends on assumed post-change speeds that I could not see. The same slides show a total fatality contribution falling only from 1.182 to 1.092 in another scenario, so the two figures must not be quoted without their scenario.

### Inferences
- For an engineering formula: do not add a variance multiplier with an invented coefficient. Report CV as a separate flag or logged metric. A lower advisory value that increases dispersion (some comply, some do not) is a plausible way to worsen risk, and the published evidence for this is suggestive rather than quantified.

### Gaps
- Aarts & van Schagen 2006 (AAP 38(2) 215-224) was not opened (SWOV page blocked by bot check). Claims come through SWOV 2012.
- No coefficient linking CV to crashes on 80 km/h rural roads was found.

## Near-accidents, traffic conflicts and surrogate safety measures: does the Power Model transfer?

### Takeaway
**I found no study estimating a Power or Exponential relationship between speed and near-accidents, conflicts or surrogate measures.** The evidence is mostly simulation that compares scenarios, plus methodological work warning that near-crashes are not interchangeable with crashes. Applying crash exponents to near-accidents has no empirical basis in the sources found.

### Cited Findings
- Field-observed conflict study of a limit change, with TTC: searches found none (query set included Tarko, Hydén, TTC, conflicts, before-after).
- VSL motorway, microsimulation (PTV VISSIM + SSAM, TTC and MaxDeltaV), calibrated with a driving simulator (60 participants). Scenarios at 1700 veh/h/lane with limits 120, 100, 80 km/h. Total conflicts 11,544 (no VMS) vs 10,742 (-7%, one VMS) vs 8,785 (-24%, VMS every 2 km). MaxDeltaV > 20 km/h: 1,616 vs 1,383 (-14%) vs 1,006 (-38%). Major-road rear-end conflicts -12% and -39%; lane-change conflicts -25% and -59%. Network mean speed barely moved, 64.52 to 63.60 km/h. Portion read does not mention a Power Model. Simulated conflicts, not observed. [E] [Oskarbski et al. 2020, Sensors 20(18) 5057, DOI 10.3390/s20185057](https://pmc.ncbi.nlm.nih.gov/articles/PMC7571130/).
- That result shows conflict changes without a matching mean-speed change, which is the opposite of what a mean-speed Power Model would predict (my reading).
- ITF/OECD slide deck on lowered urban limits used SSAM with TTC = 0.5 s scenarios. Simulation only. [S](https://itf-oecd.org/sites/default/files/docs/lowered-speed-limits-urban-areas-impact.pdf).
- A freeway-bottleneck study reported time-exposed TTC -36.27% and time-integrated TTC -40.16%, simulation conference paper, abstract only. [S](https://ascelibrary.com/doi/10.1061/9780784484869.159).
- Near-crash validity: near-crashes occur about 10 to 15 times as often as crashes, and the identical-causal-mechanism assumption is hard to evaluate. [S] [NHTSA DOT HS 811 382](https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/dot_hs_811_382.pdf); page returned 403.
- Surrogate measure validation: no single measure performs well on all dimensions; TTC is the most efficient but weak on timeliness and robustness. Naturalistic driving data. [S] [Lu et al., AAP 2021, TU Delft record](https://repository.tudelft.nl/record/uuid:a1963b16-ade9-44ff-8be3-fb97f9ef9199).
- Individual-level crash risk: Dingus et al. 2016 (SHRP2, PNAS) reported an odds ratio of 12.8 (95% CI 10.1 to 16.2) for "speeding over limit and too fast for conditions". Young's re-analysis separates exceeding the limit, 5.4 (2.7 to 10.1), from exceeding a safe speed without exceeding the limit, 71.5 (36.0 to 136.2), and disputes the pooling. Crash data, not near-crash, not a speed-function. [S] [Young, Safety 2017](https://mdpi.com/2313-576X/3/4/28), which I could not open. This is a critique, so it is not neutral.
- Physical severity link: pedestrian survival in a car crash is about 90% at 40 km/h, under 50% at 80 km/h, 10% at 100 km/h (Rosén et al. 2011). [P] [SWOV 2012](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf). Note FHWA words this as fatality risk about 10% at 40 km/h, approaching 100% at 100 km/h [E], and the two are consistent at 100 km/h only approximately.
- Area-wide calming, Cochrane: 22 controlled before-and-after studies, total crashes RR 0.89 (0.76 to 1.05), deaths 0.79 (0.23 to 2.68), searches last updated 2008. It concerns physically calmed zones. [S] [Bunn et al., Cochrane CD003110](https://cochranelibrary.com/es/cdsr/doi/10.1002/14651858.CD003110/full/ru). No Campbell review of speed limits or speed cameras was found; speed-camera work (Pilkington & Kinra, BMJ 2005) is enforcement. [S](https://www.bmj.com/content/330/7487/331.full).

### Inferences
- Near-accidents should be handled by a separate, locally measured model (for example hard-braking or low-TTC events per vehicle-km vs local speed). The crash formula should not be applied to them.

### Conflicts, weak evidence, and what does not transfer
1. **Mean actual speed, not posted limit.** The Power and Exponential models describe changes in mean traffic speed. A posted limit acts only through whatever compliance ratio applies. Elvik et al. 2004 and Nilsson 2004 both state or assume this.
2. **Limit vs speed confounding in the source data.** Most of the speed-change evidence comes from limit changes, so "effect of mean speed" and "effect of a limit change" overlap (SWOV says this directly), but the crash effects in these studies may include enforcement, publicity and regression to the mean.
3. **Advisory vs legal.** Almost all compliance evidence is for regulatory limits. Advisory limits are not equivalent, and the VSL evidence is largely enforcement-dependent.
4. **Dynamic vs static.** Models are built on static long-term limit changes (months to years). They do not cover minute-scale changes. Flanders shows V85 at 14% of the limit change after one year and 42% after three years, so short-run effects may differ a lot.
5. **Traffic state.** Elvik 2004 notes limits are assumed not to influence mean speed in congestion. The model has no state dependence.
6. **Near-accidents and surrogates.** No transfer established. Conflict counts in simulation are not crash rates, and the exponents have no conflict-based estimates.
7. **Small-site validity.** Ambros & Kieć find almost no correlation between predicted and observed crash change at individual sites. Predictions are network-average tendencies, not site forecasts.
8. **Heterogeneity and exposure.** Elvik's estimates assume everything else equal. Rural/freeway pooling hides road-type differences. Nilsson's model assumes unchanged exposure, and limit changes can shift traffic.
9. **Elvik 2009 CIs include zero** for rural serious injury accidents (-2.7, 7.9) and Elvik 2009 urban fatalities (-0.5, 6.5).
10. **Age of the evidence.** Exponents trended downward through 2009, while Elvik 2019 values (5.5, 3.9) go the other way for post-2000 studies. Vehicle-safety change is not modelled.

### Gaps
- WHO, ETSC primary reports, the ITF/OECD 2018 report and the Handbook of Road Safety Measures were not read. Their figures appear here only where noted.
- No evidence was found of a Power Model fitted to TTC, headway, or conflict counts on 80 km/h roads.
- TOI 1296/2014 is in Norwegian, so all paraphrases and translations of it are mine.

### Source register
Full citations, as verified from title pages or catalogue records unless noted.

- Nilsson, G. (2004). *Traffic Safety Dimensions and the Power Model to Describe the Effect of Speed on Safety*. Bulletin 221, Lund Institute of Technology. [PDF](https://lup.lub.lu.se/search/files/4394446/1693353.pdf); [record](https://lup.lub.lu.se/record/21612).
- Elvik, R., Christensen, P., Amundsen, A. (2004). *Speed and road accidents: an evaluation of the Power Model*. TOI report 740/2004, Oslo. [PDF](https://www.trg.dk/elvik/740-2004.pdf).
- Elvik, R. (2009). *The Power Model of the relationship between speed and road safety: update and new analyses*. TOI report 1034/2009, Oslo. [Summary PDF](https://www.toi.no/getfile.php/1313212-1259661631/Publikasjoner/T%C3%98I%20rapporter/2009/1034-2009/1034-2009-Sum.pdf); [full report](https://www.toi.no/getfile.php?mmfileid=13206) (403 when tried).
- Cameron, M.H., Elvik, R. (2010). Nilsson's Power Model connecting speed and road trauma: applicability by road type and alternative models for urban roads. *Accident Analysis and Prevention* 42(6), 1908-1915. [PubMed](https://pubmed.ncbi.nlm.nih.gov/20728642/); [abstract copy](https://www.science.gov/topicpages/n/nilsson+model.html).
- Elvik, R. (2013). A re-parameterisation of the Power Model of the relationship between the speed of traffic and the number of accidents and accident victims. *Accident Analysis and Prevention* 50, 854-860. [DOI 10.1016/j.aap.2012.07.012](https://doi.org/10.1016/j.aap.2012.07.012).
- Elvik, R. (2014). *Fart og trafikksikkerhet: nye modeller* (Speed and road safety: new models). TOI report 1296/2014, Oslo, in Norwegian. [PDF](https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-elektronisk.pdf); [English summary](https://www.toi.no/getfile.php/1335303-1394518314/Publikasjoner/T%C3%98I%20rapporter/2014/1296-2014/1296-2014-Sum.pdf).
- Elvik, R., Vadeby, A., Hels, T., van Schagen, I. (2019). Updated estimates of the relationship between speed and road safety at the aggregate and individual levels. *Accident Analysis and Prevention* 123, 114-122. [DOI 10.1016/j.aap.2018.11.014](https://doi.org/10.1016/j.aap.2018.11.014); [TRID](https://trid.trb.org/View/1569665).
- Musicant, O., Bar-Gera, H., Schechtman, E. (2016). Impact of Speed Limit Change on Driving Speed and Road Safety on Interurban Roads: Meta-Analysis. *Transportation Research Record* 2601, 42-49. [DOI 10.3141/2601-06](https://doi.org/10.3141/2601-06); [TRID](https://trid.trb.org/View/1393349).
- Ambros, J., Kieć, M. (2025). *European Transport Research Review* 17:59, on the applicability of speed-crash models at low speeds. [DOI 10.1186/s12544-025-00753-6](https://doi.org/10.1186/s12544-025-00753-6).
- SWOV (April 2012). *The relation between speed and crashes*. SWOV Fact sheet. [Third-party copy](https://www.littlerock.gov/media/2484/the-relation-between-speed-and-crashes.pdf).
- FHWA (2018, per page). *Self-Enforcing Roadways: A Guidance Report*, FHWA-HRT-17-098, ch. 2. [HTML](https://www.fhwa.dot.gov/publications/research/safety/17098/003.cfm).
- FHWA (2017). *Synthesis of Variable Speed Limit Signs*, FHWA-HOP-17-003. [Executive summary](https://ops.fhwa.dot.gov/publications/fhwahop17003/es.htm).
- Transport Scotland (2024). *National Speed Management Review*, Appendix B. [HTML](https://www.transport.gov.scot/publication/national-speed-management-review-2024/appendix-b-summary-of-literature-review/).
- Koorey, G. (2019, per file name: NZ Transportation Group conference). *The Mechanics and Politics of Changing a Speed Limit*. [PDF](https://viastrada.nz/sites/default/files/2019-03/TG2019-ResearchPaper-GKoorey-SpeedLimits-final.pdf).
- Lammar, P. (2024). *Reducing speeds on rural roads (from 90 km/h to 70 km/h in Flanders, Belgium)*. Slides, ETSC PIN Conference, Brussels, 19 June 2024. [PDF](https://etsc.eu/wp-content/uploads/10_Pascal-Lammar.pdf).
- Kim, W., Romo, A., McDonough, J. (2023). *A Multi-Site Examination for the Impact of Changes in Posted Speed Limit on Traffic Safety*. AAA Foundation for Traffic Safety. [Page](https://aaafoundation.org/a-multi-site-examination-for-the-impact-of-changes-in-posted-speed-limit-on-traffic-safety).
- Elvik, R. (2018). Slides, 31st ICTCT Workshop, Porto, on a unified framework for speed and road safety. [Third-party copy](https://api.sambuz.com/doc/speed-is-an-important-risk-factor-a-comprehensive-and-pdf-document-539697).
- Edara, P.K., Sun, C., Hou, Y. (2013). *Evaluation of Variable Advisory Speed Limits in Work Zones*. InTrans Project 06-277, TPF-5(081). [ROSA P](https://rosap.ntl.bts.gov/view/dot/26306).
- Oskarbski, J., Kamiński, T., Kyamakya, K., Chedjou, J.C., Żarski, K., Pędzierska, M. (2020). Assessment of the Speed Management Impact on Road Traffic Safety on the Sections of Motorways and Expressways Using Simulation Methods. *Sensors* 20(18), 5057. [DOI 10.3390/s20185057](https://doi.org/10.3390/s20185057).
- Davis, G.A. (2002). Is the claim that "variance kills" an ecological fallacy? *Accident Analysis and Prevention* 34, 343-346 (citation from TOI 1296/2014 reference list; not read).
- Aarts, L., van Schagen, I. (2006). Driving speed and the risk of road crashes: a review. *Accident Analysis and Prevention* 38(2), 215-224 (citation from SWOV 2012 reference list; not read).
