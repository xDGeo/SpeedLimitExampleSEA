# Darkness, icy surfaces, crash risk and safe stopping: numbers for a physics-based advisory formula

Research date: 2026-11-09. Target: a stopping-distance check at 40, 50, 60, 70 and 80 km/h on dry, wet, snow and black-ice surfaces, in daylight and darkness.

**Read-status tags, on every figure:**
- **[P]** I read the relevant part of the primary source. PDFs were read through text extraction, and tables were checked by text position where the extraction scrambled them.
- **[A]** I read only the abstract or bibliographic record of the primary source.
- **[S]** I saw it only quoted in another source that I read.
- **[U]** I saw it only in a search-engine result summary and did not open the page. Treat as unverified.
- **[C]** My own calculation from the cited inputs.

**Primary sources I could not open:** AASHTO Green Book (paywalled); NCHRP 400 (the PDF is a scan with no text layer); RVS and RAL (no accessible text); Elvik's Handbook; Malin 2019 full text; Johansson 2009 full text; Green 2000 full text. Each is listed in the Gaps of the question it affects.

## Stopping sight distance formula and parameters (AASHTO and European equivalents)

### Takeaway
AASHTO's design check is SSD = 0.278·V·t + 0.039·V²/a with t = 2.5 s and a = 3.4 m/s². That deceleration is a chosen comfort value equal to μ ≈ 0.35, so it is not a friction measurement and cannot represent ice. For surfaces, use the friction form v·t/3.6 + v²/(254·μ) with a surface-specific μ.

### Cited Findings
- **US customary form, in force:** SSD = 1.47·V·t + 1.075·V²/a, with t = 2.5 s, a = 11.2 ft/s², V in mph, SSD in ft. Reproduced from Green Book 2011 Eq. 3-2. [P of the state manual; S for AASHTO] — [Iowa DOT Design Manual, Section 6D-1 Sight Distance, revised 2015-07-02](https://documents.iowa.gov/home/download/9592894)
- **Green Book 2011 Table 3-3, level grade (calculated / design, ft):** 25 mph 151.9 / 155; 30 mph 196.7 / 200; 35 mph 246.3 / 250; 40 mph 300.6 / 305; 45 mph 359.8 / 360; 50 mph 423.8 / 425; 55 mph 492.5 / 495; 60 mph 566.0 / 570. [P of Iowa's reproduction; S for AASHTO] — [Iowa DOT 6D-1](https://documents.iowa.gov/home/download/9592894)
- **Grades:** the same manual says vertical grades above 3% affect the braking component, shortening it on upgrades and lengthening it on downgrades. [P] — [Iowa DOT 6D-1](https://documents.iowa.gov/home/download/9592894)
- **Metric form:** SSD = 0.278·V·t + 0.039·V²/a (V km/h, a m/s²); one third-party table lists 40 km/h as 46.2 m calculated and 50 m design. [U; the page was not identified among the results of that search] — search results for the Green Book formula, for example [Carmanah](https://carmanah.com/articles/stopping-sight-distances-for-crosswalks/)
- **Parameter history in the Green Book:** 2001 and 2004 editions use design speed, t = 2.5 s, deceleration 3.4 m/s², eye height 1.07 m, object height 0.6 m. The switch from a friction factor to a "comfortable deceleration rate" came in 2001, based on NCHRP 400 (Fambro et al. 1997). [P of the review; S for AASHTO and NCHRP] — [Cheng, Yuan, Shi, Huang 2011, "Revision of calculation of stopping sight distance", Baltic Journal of Road and Bridge Engineering 6(2):96–101, doi:10.3846/bjrbe.2011.13](https://bjrbe-journals.rtu.lv/bjrbe/article/download/bjrbe.2011.13/127/364)
- **Reaction-time rationale:** t = 2.5 s was "found to be adequate" for about 90% of drivers in the studies cited (Fambro 1997; Johansson and Rumar 1971; Normann 1953), while some field measurements suggest 2.0 s is enough (Durth and Bernhard 2000; Mavromatis et al. 2005). [P of the review; S for the underlying studies] — [Cheng et al. 2011](https://bjrbe-journals.rtu.lv/bjrbe/article/download/bjrbe.2011.13/127/364)
- **Older friction-based Green Book values:** wet locked-wheel friction factors of about 0.27 to 0.50 across editions and speeds; for example, one edition runs from 0.36 at 50.7 km/h to 0.29 at 118.3 km/h. [P of the review, but its Table 1 extracted out of order, so I cannot assign each range to a specific edition] — [Cheng et al. 2011](https://bjrbe-journals.rtu.lv/bjrbe/article/download/bjrbe.2011.13/127/364)
- **Europe, model structure:** Austria, Germany and Greece use a model with a speed-dependent longitudinal friction factor and an aerodynamic drag force (Harwood et al. 1995). Most other countries still base SSD on a friction factor. [P of the review; S for Harwood; the equation itself was an image I could not read] — [Cheng et al. 2011](https://bjrbe-journals.rtu.lv/bjrbe/article/download/bjrbe.2011.13/127/364)
- **Germany, RAL 2012:** mean braking deceleration 3.7 m/s² for RAL; reaction time 2 s, described as the value in most international guidelines; actual sight distance on most of the route should be at least 30% above the required stopping sight distance. [U; the KIT lecture script returned HTTP 404 when opened] — [KIT, Entwurf und Bau von Straßen, 2013](https://www.ise.kit.edu/KIT_EuB_SE_2013.pdf)
- **Germany, calculator:** a constant tangential friction coefficient of 0.377 with g = 9.81 m/s². [U; the page does not tie it to RAL] — [bauformeln.de, Haltesichtweite](https://www.bauformeln.de/strassenbau/entwurfsformeln/haltesichtweite/)

### Inferences
- **Equivalent μ.** 3.4 / 9.81 = 0.347. [C] German 0.377 × 9.81 = 3.70 m/s², which matches the 3.7 m/s² in the KIT snippet, suggesting the two come from one model. This match is my inference and neither source states it. [C]
- **Formula for the advisor** (v km/h, t s, μ dimensionless, G grade as a decimal, + uphill): D_stop = v·t/3.6 + v²/(254·(μ+G)), where 254 = 2·9.81·3.6². The grade term is standard physics; I saw the Green Book's sign convention in text but could not read its equation image. [C]
- **Inverse, for a maximum speed given available distance D:** v_max = 3.6·a·(−t + √(t² + 2D/a)), where a = μ·g on level ground. [C]
- **Check of the formula against the design table:** with t = 2.5 and a = 3.4, the formula gives 45.9, 63.1, 82.5, 104.2 and 128.2 m at 40 to 80 km/h, level grade. The rounded AASHTO constants give 46.2, 63.4, 83.0, 104.9 and 129.0 m. [C] I did not read AASHTO's metric design table.

**Computed D_stop in metres, level grade [C].** The μ values come from the friction section below. Columns are scenarios and do not map one-to-one onto surfaces.

| t = 2.5 s | Reaction distance | μ 0.80 dry (VTI low end) | μ 0.70 wet (VTI low end) | a 3.4 (AASHTO design) | μ 0.25 packed snow (VTI mid) | μ 0.15 black ice (VTI low end) | μ 0.08 rig ice (Lund, 4 kN) | μ 0.05 wet black ice (VTI low end) |
|---|---|---|---|---|---|---|---|---|
| 40 km/h | 27.8 | 35.6 | 36.8 | 45.9 | 52.9 | 69.7 | 106.4 | 153.6 |
| 50 km/h | 34.7 | 47.0 | 48.8 | 63.1 | 74.0 | 100.3 | 157.6 | 231.4 |
| 60 km/h | 41.7 | 59.4 | 61.9 | 82.5 | 98.3 | 136.1 | 218.6 | 324.8 |
| 70 km/h | 48.6 | 72.7 | 76.1 | 104.1 | 125.7 | 177.1 | 289.5 | 434.0 |
| 80 km/h | 55.6 | 87.0 | 91.5 | 128.1 | 156.2 | 223.4 | 370.2 | 558.9 |

| t = 1.5 s | Reaction distance | μ 0.80 | μ 0.70 | a 3.4 | μ 0.25 | μ 0.15 | μ 0.08 | μ 0.05 |
|---|---|---|---|---|---|---|---|---|
| 40 km/h | 16.7 | 24.5 | 25.7 | 34.8 | 41.8 | 58.6 | 95.3 | 142.5 |
| 50 km/h | 20.8 | 33.1 | 34.9 | 49.2 | 60.2 | 86.4 | 143.7 | 217.5 |
| 60 km/h | 25.0 | 42.7 | 45.2 | 65.8 | 81.6 | 119.4 | 202.0 | 308.2 |
| 70 km/h | 29.2 | 53.3 | 56.7 | 84.7 | 106.2 | 157.6 | 270.0 | 414.6 |
| 80 km/h | 33.3 | 64.8 | 69.3 | 105.9 | 134.0 | 201.1 | 348.0 | 536.7 |

- **Limit of transfer:** AASHTO's 3.4 m/s² is a design comfort value for roads kept free of ice, and its 0.6 m object height is a geometric convention. Neither says anything about ice or about what can be seen at night.
- **The two parameters sit in different places in the safety margin:** on dry roads AASHTO's a = 3.4 is far below the available grip, so the formula is conservative. On packed snow and ice the available grip is below 3.4 m/s², so AASHTO distances are unsafe unless μ replaces a.

### Gaps
- The AASHTO Green Book itself was not accessible, so the metric design table (expected rounded values at 40 to 80 km/h) is not verified. Only the 40 km/h snippet was seen.
- The reasoning for 3.4 m/s² (share of drivers who exceed it, wet-road basis) should come from NCHRP 400. That PDF is image-only and I did not OCR it.
- FHWA's mitigation-strategies page on stopping sight distance now redirects to a generic landing page, so I did not read it.
- RVS 03.03.23 (Austria) was not found in any accessible form. The RAL 2012 equation and table were not read. The formula form suggested by the search tool for RAL (S_h = v·t/3.6 + v²/(254·(f ± s/100))) was offered from its background knowledge, so I do not cite it as a source.

## Tyre-road friction coefficients by surface

### Takeaway
A Swedish review gives dry 0.8–1.0, wet 0.7–0.8, packed snow 0.20–0.30, black ice 0.15–0.30 and wet black ice 0.05–0.10, all from 17%-slip skiddometers. Instrumented tyre tests on prepared ice came in much lower, at 0.08 for non-studded tyres and 0.16 for studded. "Black ice" therefore has no single μ, and a default of 0.15 with a 0.05–0.08 stress case is defensible.

### Cited Findings
- **Swedish survey summary, skiddometer at 17% slip (BV11 and SFT devices)** [P] — [Wallman and Åström 2001, *Friction measurement methods and the correlation between road friction and traffic safety: a literature review*, VTI meddelande 911A, p. 37](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf) (summarising mainly Öberg's SFT survey, described on p. 35, and Öberg and Gregersen):

| Surface | Friction number |
|---|---|
| Dry, bare | 0.8–1.0 |
| Wet, bare | 0.7–0.8 |
| Packed snow | 0.20–0.30 |
| Loose snow / slush | 0.20–0.50 (higher when tyres reach the pavement) |
| Black ice | 0.15–0.30 |
| Loose snow on black ice | 0.15–0.25 |
| Wet black ice | 0.05–0.10 |

- **Comparability warning:** every country has its own instruments and methods, so values reported internationally are "not directly comparable". Friction values are also very sensitive to the test tyre, and even batches of a standard test tyre differ. [P] — [VTI 911A, abstract on p. 3 and summary on p. 6; tyre sensitivity on p. 11](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Ice temperature:** the higher the ice temperature, the more slippery the surface. Northern Sweden can have black ice for weeks at low temperature with "comparatively high" friction. Whitehurst and Ivey give a locked-wheel stopping-distance multiplier against ice temperature, referenced to −4 °C (25 °F). [P; the multiplier curve is a figure with no extractable numbers] — [VTI 911A, p. 38–39](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Variation within a surface class:** similar-looking winter surfaces can have very different friction, and friction varies across and along the road. In Öberg's survey the span within one road condition was often larger than the difference between condition means. With about 1 cm of wet snow, a coarse surface dressing kept "bare-ground friction" while smooth asphalt concrete had "ice/snow friction". [P] — [VTI 911A, p. 35 and p. 42](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Instrumented tyre tests:** VTI measurements at Colmis Proving Ground, Arjeplog, 2006, braking torque ramped from free rolling to lock-up, values fitted with a brush model. Tyres were Continental ContiWinterContact TS810 215/55R16 (winter), Continental ContiSportContact 225/45R17 (summer) and Gislaved Nordfrost 3 215/55R16 (studded). [P] — [Svendenius 2007, *Validation of the Brush Model towards VTI-measurement data recorded in Arjeplog 2006*, Technical Report TFRT-7617, Lund University, Tables 4 and 6](https://lup.lub.lu.se/search/files/4590032/8627412.pdf)

| Tyre, 4 kN load | Snow μ | Ice μ |
|---|---|---|
| Winter, non-studded | 0.40 | 0.078 |
| Summer | 0.26 | 0.077 |
| Studded winter | 0.51 | 0.16 |

- **Same report, load and wet effects:** winter tyre on snow 0.40, 0.40 and 0.41 at 2, 4 and 6 kN; on ice 0.10, 0.078 and 0.081. Winter tyre on wet asphalt 0.977, 1.02 and 1.05 (data from a separate source, the report's ref. 3). [P] The report warns that ice results are hard to evaluate because the very low force gives a large spread of data points. [P] — [Svendenius 2007](https://lup.lub.lu.se/search/files/4590032/8627412.pdf)
- **Studded vs non-studded on ice:** studded tyres as a group remain superior on ice, and tyre age from 5 to 15 years had no significant influence on ice friction. [U] — VTI report in catalogue results, [bibliotek.vti.se/bib/250731](https://bibliotek.vti.se/bib/250731) or [254591](https://bibliotek.vti.se/bib/254591) (I could not tell which record held this)
- **ABS on packed snow:** brake tests with the BV12 rig and a passenger car on more than 40 tyres estimated that ABS retardation reaches about 85% of the slip-curve peak friction on hard packed snow. [U; a VTI-linked study, exact record not identified] — candidate: [Tire Science and Technology 45(3), p. 175](https://tst.kglmeridian.com/view/journals/tist/45/3/article-p175.xml)
- **Finland's acceptance limits for wet friction by speed limit:** 0.4 where 80 km/h is the highest speed, 0.5 at 100 km/h and 0.6 at 120 km/h (PANK 5201 or TIE 475). Sweden's acceptable level in the reported tunnel case was 0.50 with the SFT. [P] — [VTI 911A, p. 20](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)

### Inferences
- **Suggested μ per surface for the advisor:**

| Surface | Default | Range to expose | Basis |
|---|---|---|---|
| Dry | 0.8 | 0.8–1.0 | VTI skiddometer |
| Wet | 0.35 for a conservative check; 0.7 as measured | 0.35–0.8 | AASHTO equivalent; VTI skiddometer |
| Packed snow | 0.25 (0.40 only with verified winter tyres) | 0.20–0.40 | VTI; Svendenius |
| Black ice | 0.15 | 0.05–0.30 | VTI; Svendenius rig ice 0.08 |

- **Conflict to surface in the design:** VTI's black ice (0.15–0.30) and the rig ice (0.08 non-studded, 0.16 studded) differ by roughly a factor of two. The likely reasons are different ice preparation, temperature and instrument. I could not confirm which applies, and the rig report does not give ice temperature in the part I read.
- **Skiddometer values are device friction numbers, not car deceleration.** They come from a measuring wheel at 17% slip. Using them directly as μ is optimistic to an unknown degree, since a full car with ABS and load transfer does not hold peak slip. The 85% figure above is the only quantification I saw, and it is unverified and specific to packed snow.
- **Summer vs winter tyres on ice were indistinguishable at 4 kN** (0.077 vs 0.078) in one test of one tyre each. Do not build a tyre multiplier for ice from this. On snow the difference is clear (0.26 vs 0.40).

### Gaps
- No NHTSA, Transport Canada or VTT friction values were found or verified. The Tire Science and Technology 2017 study of 77 winter tyres was seen as a search listing only, with no numbers.
- No verified μ-vs-temperature function; the Whitehurst and Ivey curve exists only as a figure in VTI 911A.
- No verified measurement of full-vehicle ABS stopping on black ice in a controlled test.

## Driver perception-reaction time, including at night and for unexpected hazards

### Takeaway
Review figures run about 0.7–0.75 s for expected, 1.25 s for unexpected and 1.5 s for surprise events, and a classic hill-crest test found a 95th percentile of about 1.6 s. Design practice uses 2.5 s. I found no verified night-specific reaction-time value, so darkness should reach the formula through detection distance and not through an invented longer t.

### Cited Findings
- **Green (2000), "How long does it take to stop? Methodological analysis of driver perception-brake times":** fully expected about 0.70–0.75 s; unexpected but common signal such as a lead car braking about 1.25 s; surprise such as an object suddenly entering the path about 1.5 s. Expectancy roughly doubles reaction time from fully expected to surprise. [U; a catalogue-page summary, and the catalogue URL returned 404 when opened] — [drivingresearch catalogue entry](https://drivingresearch.pages.dev/catalog/green-2000-how-long-does-it-take-to-stop/)
- **Critique of those values:** a later commentary reports that in critical conditions median yellow-light response is under 1.0 s, and that on-road data do not clearly support a 1.5 s mean for surprise events; it calls for more real-world data accounting for urgency. [U; I infer from the listing that this record is the commentary, and did not open it] — [record 10.1207/STHF0203_2](https://www.informahealthcare.com/doi/abs/10.1207/STHF0203_2)
- **Olson and Sivak (1986):** unalerted subjects meeting an obstacle in their lane while cresting a hill; 95th percentile perception-response time about 1.6 s for both age groups. Published in *Human Factors* 28(1):91–96, Feb 1986. [U from search summary of the PubMed record] — [PubMed 3710489](https://pubmed.ncbi.nlm.nih.gov/3710489/)
- **Critique of 1.6 s:** later commentators call it a best-case value in highly optimized conditions, and say low visibility, complexity, uncertainty, alertness and age may lengthen response. [U] — [Marc Green, "Let's Get Real About Perception-Response Time"](https://www.visualexpert.com/Resources/realprt.html); [TRID 913048](https://trid.trb.org/view/913048)
- **2.5 s as a design value** covers about 90% of drivers in the studies cited by the review above. [P of review; S for the studies] — [Cheng et al. 2011](https://bjrbe-journals.rtu.lv/bjrbe/article/download/bjrbe.2011.13/127/364)

### Inferences
- **Suggested range:** t = 2.5 s as the conservative default and t = 1.5 s as the alert-driver sensitivity case. The 1.5 s value spans Green's surprise figure and approximately Olson's 95th percentile, both unverified at full-text level.
- **Do not add a verified "night penalty" to t.** I found none. If the implementation needs one, label it as an assumption and expose it as a tunable parameter.
- At 80 km/h, moving from 1.5 to 2.5 s adds 22.2 m regardless of surface. [C] This matters most on dry roads, where it is about a third of the total.

### Gaps
- No verified night-specific perception-reaction time. Candidate sources not reached: Plainis and Murray; NCHRP 270 (Olson et al. 1984).
- Johansson and Rumar (1971) was seen only as a reference in Cheng et al., so I cannot quote its numbers.
- Green's full text was not read, and I did not confirm the journal volume or DOI suffix from a page I read.
- I could not confirm whether Olson and Sivak's test was in daylight.

## Low-beam headlight sight distance and "overdriving" headlights

### Takeaway
AAA measured low beams revealing a non-reflective object at 300 ft (91 m) for halogen reflectors and 450 ft (137 m) for LEDs, which it equates to maximum safe speeds of 39 to 52 mph (63 to 84 km/h) on AASHTO assumptions. Dark-clothed pedestrians and small road objects can be seen far later, so the assumed obstacle is the key input.

### Cited Findings
- **AAA headlamp test, May 2015** (Automobile Club of Southern California Automotive Research Center and AAA National Office; light meters, DOT headlamp certification method, human observation; averaged results). Low beam lighted distance, and AAA's "max vehicle speed" to keep a fully lit stopping sight distance: halogen reflector 300 ft / 39 mph; halogen projector 400 ft / 45 mph; HID 400 ft / 45 mph; LED 450 ft / 52 mph. High beam: halogen reflector 400 ft / 48 mph; projector, HID and LED 500 ft / 55 mph. The speeds are based on AASHTO 4th ed. 2004 and Caltrans Highway Design Manual 6th ed. 2012. [P] — [AAA Fact Sheet, *Test Results: Automotive Headlamp Systems*, May 2015](https://newsroom.aaa.com/wp-content/uploads/2019/06/AET-Headlights-Fact-Sheet.pdf)
- **Same fact sheet:** low beams let a driver "perceive a non-reflective object" at those distances. Even the most advanced systems reduce the ability to see an object at night by as much as 60% against daylight. The fact sheet does not state the object's size or contrast. [P] — [AAA 2015](https://newsroom.aaa.com/wp-content/uploads/2019/06/AET-Headlights-Fact-Sheet.pdf)
- **FHWA Smart Road test, December 2005, closed test facility, 25 mph on the second night.** Approximate values pooled across all headlamp systems, so they are not low-beam-only: detection of a black parallel pedestrian about 355 ft (108 m), recognition about 300 ft (91 m); black cyclist detection about 520 ft (158 m); child's bicycle detection about 425 ft (130 m); tyre tread detection about 205 ft (62 m), recognition about 175 ft (53 m); white pedestrians and cyclist detection about 805–845 ft (245–258 m). Halogen low beam specifically: child's bicycle detection about 450 ft (137 m). [P via an automated reading of the report's figure descriptions; values are approximate] — [FHWA-HRT-04-134, *Enhanced Night Visibility Series, Volume III: Phase II, Study 1: Visual Performance During Nighttime Driving in Clear Weather*, 2005](https://www.fhwa.dot.gov/publications/research/safety/humanfac/04134/508txt.cfm)
- **IIHS ratings use illuminance, not detection:** visibility is the distance at which 5 lux is reached and continuously maintained. For no demerits on low beams: straightaway right edge 100 m (critical value 70 m), straightaway left edge 60 m (40 m); curves 60–70 m (40–50 m). High beams: straightaway 150 m (120 m). [P] — [IIHS, *Headlight Test and Rating Protocol (Version II)*, November 2016](https://www.iihs.org/media/714fb5d9-b769-48ae-9fec-49bca8fd8ada/G2TuBg/Ratings/Protocols/current/headlight_test_rating_protocol.pdf)
- **Recognition in a mixed-age road study:** drivers recognized only 5% of pedestrians in the hardest condition (low beams, black clothing, glare). Without glare, mean recognition distance ranged from 0.0 m (older drivers, low beam, black clothing) to 220 m (younger drivers, high beam, biomotion clothing). [U; a SWOV record of the study, authors and year not confirmed from a page I read] — [SWOV, "Limitations in drivers' ability to recognize pedestrians at night"](https://swov.nl/en/publicatie/limitations-drivers-ability-recognize-pedestrians-night)
- **Older figure:** pedestrians in dark clothing are often noticed at under 30 m with standard low beams, attributed to Olson and Sivak. [U; a later paper's statement] — [MDPI Engineering Proceedings 150(1):18](https://www.mdpi.com/2673-4591/150/1/18)
- **Assured clear distance:** Leibowitz, Owens and Tyrrell's paper addresses the rule's implications for night safety. Only the listing was seen, with no numbers. [U] — [Accident Analysis & Prevention, *The assured clear distance ahead rule*](https://www.sciencedirect.com/science/article/abs/pii/S0001457597000675)
- **Selective degradation hypothesis:** steering can be as good at night as in daytime, while recognising infrequent hazards is seriously degraded, leaving drivers overconfident. [U] — [Leibowitz and Owens, *Nighttime Driving and Visual Degradation*](https://www.semanticscholar.org/paper/Nighttime-Driving-and-Visual-Degradation-Leibowitz-Owens/b4c330e01035e34ef021d8ff398f4211e7cd3498)

### Inferences
- **Maximum speed, in km/h, for a given detection distance [C].** Formula above, level road, t = 2.5 s / 1.5 s:

| Detection distance | Example basis | μ 0.8 | a 3.4 (μ 0.347) | μ 0.25 | μ 0.15 | μ 0.08 |
|---|---|---|---|---|---|---|
| 30 m | Dark pedestrian, older low-beam figure [U] | 35 / 46 | 29 / 36 | 27 / 32 | 23 / 27 | 19 / 21 |
| 62 m | Tyre tread detection, FHWA pooled | 62 / 78 | 49 / 58 | 44 / 51 | 37 / 41 | 29 / 32 |
| 91 m | AAA halogen reflector low beam | 83 / 100 | 64 / 73 | 57 / 64 | 47 / 52 | 37 / 39 |
| 108 m | Black pedestrian, FHWA pooled | 94 / 112 | 72 / 81 | 64 / 71 | 52 / 57 | 40 / 43 |

- **The advisor must combine both limits:** D_available = min(geometric sight distance, detection distance for the chosen obstacle). In daylight the geometric limit normally controls. At night the detection limit normally controls.
- **Check of AAA's speeds [C]:** AASHTO stopping distance at 39, 52 and 55 mph is 88.3 m, 137.6 m and 150.4 m, which match 300, 450 and 500 ft. For 400 ft the same formula gives about 48 mph, so AAA's stated 45 mph is more conservative than the formula. The fact sheet does not explain the difference.
- **Limits of transfer:** the FHWA values come from a closed road with participants looking for objects, so real unalerted detection will be shorter. AAA's object is undefined. IIHS measures light on the road and not perception. Detection distance is not a single property of the car: it changes with obstacle contrast, glare, age, wet-road reflectance and headlamp aim.
- **A surface effect I did not quantify:** wet and snow-covered surfaces change road luminance and glare, but I found no verified detection-distance adjustment for them.

### Gaps
- No UMTRI headlamp detection figures were verified (Sullivan and Flannagan's pedestrian scenarios, Mefford et al. on high-beam use).
- The Olson and Sivak <30 m figure and the claim attributed to Owens et al. 2007 that speeds must stay below 40 mph for dark-clad pedestrians were seen only in search summaries, and I did not pin the second one to a specific page.
- The FHWA report's low-beam-specific values by clothing appear only in figures I could not read numerically.

## Crash-risk ratios: darkness vs daylight, and icy, snowy or wet vs dry

### Takeaway
Darkness raises injury-crash risk by about 30% urban and 50% rural after controlling for time of day, and by about 2× in raw Nordic exposure rates. Against dry bare roads, wet roads are 1.2–1.6×, snow about 2.5–3×, and ice commonly about 4–8×, with Finnish estimates up to 30–50×. Ice and darkness combine at less than the product of the two.

### Cited Findings
**Darkness**
- **Johansson, Wanvik and Elvik (2009), *Accident Analysis & Prevention* 41(4):809–815,** case-control method using hours that are dark in one part of the year and light in another; Norway, Sweden and the Netherlands. Darkness raises injury-accident risk by nearly 30% on urban roads, nearly 50% on rural roads, and about 40% for both combined (adjusted). [A; Europe PMC record] — [doi:10.1016/j.aap.2009.04.003](https://doi.org/10.1016/j.aap.2009.04.003)
- **Conflicting quotation:** one paper citing Johansson and colleagues reports a 52% risk increase for Sweden, Norway and the Netherlands in total, in a bicyclist context. [U] — [European Transport Research Review, 2010](https://rd.springer.com/content/pdf/10.1007/s12544-010-0034-1.pdf)
- **Definition caveat:** some authors include civil twilight in darkness and others exclude it, which changes the odds ratio. [U] — [Safety 4(1):10](https://mdpi.com/2313-576X/4/1/10) (HTTP 403 when opened)
- **Swedish rates, accidents per million axle-pair km, Table 4.1** (Wallman et al., data from Nilsson), winter = October–April. [P, table verified by text position] — [VTI 911A, p. 39](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)

| Region | Light | Bare, all year | Bare, summer | Bare, Oct–Apr | Ice/snow |
|---|---|---|---|---|---|
| Northern | Daylight | 0.37 | 0.41 | 0.28 | 1.07 |
| Northern | Darkness | 0.83 | 1.38 | 0.60 | 1.43 |
| Central | Daylight | 0.46 | 0.51 | 0.39 | 2.67 |
| Central | Darkness | 1.01 | 1.69 | 0.76 | 3.30 |
| Southern | Daylight | 0.55 | 0.59 | 0.49 | 5.29 |
| Southern | Darkness | 1.06 | 1.48 | 0.91 | 7.93 |

- **Finnish rates, 1974–77, per 100 million vehicle-km:** daylight 97, dawn or dusk 222, lit road in darkness 189, unlit road in darkness 146. [S; a study reviewed in Finnish] — [Malmivuo and Kärki 2002, *Ajokeliin liittyvä riski*, Tiehallinnon selvityksiä 39/2002, PDF p. 17](https://www.tieh.fi/julkaisut/pdf/ajokeliin_liittyva_riski.pdf)
- **Wallman, Wretling and Öberg 1997 (VTI rapport 423A) table, relative rates:** bare road daylight 1, dark 2; ice/snow daylight 2–20, dark 4–14. [S] — [Malmivuo and Kärki 2002, Table 8, PDF p. 27](https://www.tieh.fi/julkaisut/pdf/ajokeliin_liittyva_riski.pdf)
- **Darkness and winter surface:** in one reviewed study, risk in darkness was twice daytime risk overall, yet ice and snow risk was the same in dark and light. [S] — [Malmivuo and Kärki 2002, PDF p. 25](https://www.tieh.fi/julkaisut/pdf/ajokeliin_liittyva_riski.pdf)
- **Road lighting effect (Wanvik 2009, Dutch data 1987–2006, 763,000 injury and 3.3 million property-damage accidents):** about −49% fatal and −46% injury crashes; another analysis reports −50% [−53, −47] for injury accidents in darkness; pedestrian risk −72%, cyclist −58%. These measure the effect of lighting within darkness, not darkness against daylight. [U; I could not tell which of these pages held which figure] — [Wanvik 2009, ScienceDirect listing](https://www.sciencedirect.com/science/article/abs/pii/S0001457508001917); [Fotios and Price 2017](https://eprints.whiterose.ac.uk/116229/10/Fotios%20Price%202017%20accidents%20and%20lighting.pdf); [University of Sheffield Lighting Research Group, written evidence](https://committees.parliament.uk/writtenevidence/102429/pdf/)
- **AAA quoting NHTSA:** 25% of driving occurs in darkness and 50% of crashes occur then. [S] — [AAA 2015](https://newsroom.aaa.com/wp-content/uploads/2019/06/AET-Headlights-Fact-Sheet.pdf)

**Surface**
- **Sweden, nationwide observations, winters 1993/94–1996/97 (Wallman), Table 4.2, all accidents except wildlife; D+SI = dead and seriously injured.** Rates were not given a unit in the caption. [P, verified by text position] — [VTI 911A, p. 41](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)

| Surface | All roads, All / D+SI | Salted (A1–A4), All / D+SI | Sanded (B1–B2), All / D+SI |
|---|---|---|---|
| Dry, bare | 0.25 / 0.02 | 0.25 / 0.02 | 0.20 / 0.03 |
| Wet or moist | 0.30 / 0.03 | 0.30 / 0.03 | 0.30 / 0.03 |
| Loose snow or slush | 1.40 / 0.14 | 1.60 / 0.15 | 0.90 / 0.12 |
| Thick ice or packed snow | 0.70 / 0.07 | 1.90 / 0.13 | 0.55 / 0.05 |
| Black ice or hoarfrost | 1.30 / 0.13 | 2.80 / 0.26 | 0.55 / 0.07 |

- **Norway (Sakshaug and Vaa), personal injuries per million vehicle-km, Table 4.3:** dry winter 0.12; wet winter 0.16; loose snow 0.30; packed snow 0.31; ice 0.53; hoarfrost 0.53; slush 0.18 (marked unreliable); dry summer 0.14; wet summer 0.18. [P] — [VTI 911A, p. 41](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Norway, by friction, Table 4.4:** μ < 0.15: 0.80; 0.15–0.24: 0.55; 0.25–0.34: 0.25; 0.35–0.44: 0.20. [P] — [VTI 911A, p. 42](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **VTI's own verdict:** winter risk-friction estimates are "few and unreliable", though always with much larger risks than at bare road. [P] — [VTI 911A, abstract and p. 42](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Finland, literature comparison, Malmivuo and Kärki 2002** [P of the English summary; S for the reviewed studies] — [Tiehallinnon selvityksiä 39/2002](https://www.tieh.fi/julkaisut/pdf/ajokeliin_liittyva_riski.pdf):
  - Icy conditions 30–50× bare and dry on coastal main roads (their 2002 estimate); Wallman's Swedish figure is 8× at equivalent shares of icy conditions (PDF p. 7).
  - 1974–77 coastal zone, bare dry : bare wet : snowy : icy = 1 : 1.6 : 1.7 : 8.0 (77, 123, 131 and 615 per 100 million vehicle-km) (p. 17).
  - Another study: bare : snowy : slushy : icy = 1 : 1.3 : 2.5 : 6.2 (p. 18).
  - Polvinen 1987, winter 1984/85: ice 25–35× dry on main roads and 11–13× on other public roads (p. 20).
  - Malmivuo and Peltola 1997: bare : snowy : slushy : icy = 1 : 8 : 12 : 17 for all accidents, 1 : 9 : 18 : 24 for injury accidents, 1 : 3 : 5 : 13 for deaths; the authors themselves strongly doubted reliability (p. 22).
  - Slippery vs good grip in maintenance classes Isk, I and Is: 4.2× southern, 2.1–3.3× central, 3.0× northern Finland (p. 22).
  - Police data 1970–74: ice and snow 3–20× bare road (p. 24).
  - Risk is higher where such conditions are rarer, and ice-road risk correlates with its share of traffic (p. 20–21).
  - Largest single contrast: 56× for icy surface in darkness on an unlit road in rain without anti-skid treatment, against bare dry road in cloudy daylight (p. 18).
- **Malin, Norros and Innamaa (2019), *Accident Analysis & Prevention* 122:181–188:** 10,646 police-reported accidents on 43 Finnish main roads, 2014–2016, using a Palm probability method. The abstract gives no numeric relative risks. [A] — [doi:10.1016/j.aap.2018.10.014](https://doi.org/10.1016/j.aap.2018.10.014)
- **Finnish finding quoted without naming the paper:** crash risk during snowfall more than twice, and during sleet almost 1.5×, the average, from 10,000+ crashes on 43 major roads in 2014–2016. [U] — [SWOV fact, Weather](https://swov.nl/en/fact/weather-11-which-weather-conditions-are-most-common-crashes-and-how-dangerous-are-they)
- **Road temperature:** risk rises quickly as the road surface falls from +2 °C to −2 °C and peaks at −2 °C, remaining above the above-freezing level at colder temperatures. [U] — [arXiv:2508.07881](https://arxiv.org/pdf/2508.07881)
- **North America:** snow can raise the crash rate by 84% and the injury rate by 75%, and reported increases range from 30 to 250%; these are attributed to the Strong, Ye and Shi review. [U] — [Strong et al. 2010, listing](https://www.researchgate.net/publication/248987317_Safety_Effects_of_Winter_Weather_The_State_of_Knowledge_and_Remaining_Challenges)
- **Canada:** Andrey (2010), 10 cities, 1984–2002; relative risk during snow 2.54 and rain 1.65, for casualty collisions. [U; flagged in the summary as unconfirmed] Snowfall relative risk was unchanged over time while rainfall risk fell about 0.0174 per year. [U] — [Andrey 2010, *Journal of Transport Geography*](https://www.researchgate.net/publication/248452817_Long-term_trends_in_weather-related_crash_risks); [Andrey and Hambly, PIARC 2010](https://proceedings-quebec2010.piarc.org/EN/programme/EN/IP2-0144-Andrey-E.pdf)
- **Reporting bias caution:** crash rates during winter storms may be inflated by lower volumes and higher reporting. [U] — [Strong et al. 2010 listing](https://www.researchgate.net/publication/248987317_Safety_Effects_of_Winter_Weather_The_State_of_Knowledge_and_Remaining_Challenges)

### Inferences
- **Ratios calculated from VTI Table 4.2, all roads, vs dry [C]:** wet 1.2; thick ice or packed snow 2.8; black ice or hoarfrost 5.2; loose snow or slush 5.6. For deaths and serious injuries: wet 1.5; thick ice or packed snow 3.5; black ice 6.5.
- **Black ice varies sharply with maintenance class [C]:** on salted roads 11.2× dry, on sanded roads 2.75×. Drivers on salted roads expect grip, which fits the Finnish point that rare conditions are riskier. This explanation is my interpretation.
- **Norway, from Table 4.3 vs dry winter [C]:** wet 1.33; loose snow 2.5; packed snow 2.6; ice 4.4. **Table 4.4 [C]:** μ < 0.15 is 4.0× the 0.35–0.44 band and μ 0.15–0.24 is 2.75×.
- **Sweden, dark and ice combined, from Table 4.1 [C].** Ice/snow vs bare (Oct–Apr) in daylight: north 3.8, central 6.8, south 10.8. Ice/snow plus darkness vs bare daylight: 5.1, 8.5 and 16.2, against a multiplicative prediction of 8.2, 13.3 and 20.0. **Do not multiply the ice and darkness ratios** in any advisory score.
- **Darkness range:** the Johansson 1.3–1.5 estimate controls for time of day, while the Swedish bare-road 1.9–2.2× (Oct–Apr or all year) uses raw exposure and darkness hours include more alcohol and fatigue. [C for ratios] Use Johansson for the effect of darkness itself. That explanation of the difference is my inference.
- **Limits of transfer:** all these figures measure police-reported crashes per unit of exposure, not near-accidents or stopping failures. They already include driver speed adaptation, so they understate the danger at unchanged speed. Finnish and Swedish ice ratios differ by a factor of 5 or more, partly because of definitions and because traffic share on icy conditions is hard to measure. Use them as a qualitative severity ranking and not as inputs to the stopping-distance physics.

### Gaps
- Elvik's *Handbook of Road Safety Measures* risk tables were not reached. Only FHWA CMF Clearinghouse entries for snow and ice control were seen (CMFs 0.71 and 0.96), which measure treatment effectiveness and not surface risk: [CMF Clearinghouse](https://cmfclearinghouse.fhwa.dot.gov/detail.php?facid=182).
- Malin 2019's numeric relative risks are missing: abstract only, and the 2017 Finnish Transport Agency report at [doria.fi](https://www.doria.fi/handle/10024/143844) returned 403.
- Sullivan and Flannagan (daylight-saving analysis), Andersson and Chapman, and Qiu and Nixon were not found.
- Johansson's breakdowns by road user or speed limit were not available from the abstract.
- The attribution of the 1974–77 Finnish study and several others is only through the Malmivuo and Kärki review.

## How drivers actually adjust speed on ice or in darkness

### Takeaway
Observed speed reductions in slippery conditions are small, typically about 4–9 km/h, while keeping the same stopping distance needs tens of km/h. I found no verified evidence that drivers reduce speed in darkness alone.

### Cited Findings
- **Finland, E18 weather-controlled speed limits (Rämä 1999):** adverse weather and road surface alone reduced mean free-flow car speed by an average of 6.3 km/h. Lowering the winter limit from 100 to 80 km/h gave a further 3.4 km/h. Where poor conditions were hard to detect, that limit effect was 5.3 km/h (1.9 km/h more). With slippery-road signs, weather caused 9.3 km/h and the signs and limits a further 1.8 km/h. [A] — [Rämä 1999, *Transportation Research Record* 1689:53–59, doi:10.3141/1689-08](https://cris.vtt.fi/en/publications/effects-of-weather-controlled-variable-speed-limits-and-warning-s/)
- **Sweden, Nilsson (1984):** when the speed limit was lowered from 110 to 90 km/h, predicted speeds fell about 7 km/h on dry roads but about 4 km/h on icy roads. This measures the response to a limit change, not the effect of ice on speed. [A] — [Nilsson 1984, VTI Report 389, TRID record](https://trid.trb.org/View/204558)
- **Sweden, a 1977 study:** speed fell as friction dropped, by about 13 km/h in the slow lane and 18 km/h for fast drivers in the overtaking lane. Keeping the dry-road stopping distance would have needed up to 35 km/h less speed on unstudded tyres and 30 km/h on studded. [U] — [TRID 92005, *Driver speed adaptation to road conditions*](https://trid.trb.org/View/92005)
- **Finland, 1995 conference paper:** average speed on a slippery surface was about 4 km/h lower than in good winter conditions, and calculated stopping distances show this adaptation to be insufficient. [U; record not confirmed] — candidate: [TRID 462981](https://trid.trb.org/View/462981)
- **Darkness and speed:** one study found no differences in speed between daylight, twilight and darkness, with or without road lighting, while rain and snow lowered speed, more so on unlit roads. [U; the summary did not identify the source. I believe it is Jägerbrand and Sjöbergh 2016, SpringerPlus, doi:10.1186/s40064-016-2124-6, but the article page redirected to a login and I could not confirm it.]
- **Perceived vs actual friction:** VTI's conceptual model says perceived friction influences behaviour "but usually far from the necessary extent", so actual friction strongly affects the accident rate. This is a review statement and carries no measured speed. [P] — [VTI 911A, p. 35](https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf)
- **Reflector posts:** on roads with 80 km/h limits and relatively low geometric standards, reflector posts increased driving speeds in darkness. [U, attributed to Leibowitz and Owens] — [Semantic Scholar record](https://www.semanticscholar.org/paper/Nighttime-Driving-and-Visual-Degradation-Leibowitz-Owens/b4c330e01035e34ef021d8ff398f4211e7cd3498)

### Inferences
- **Speed needed to match the dry-road stopping distance at t = 2.5 s, km/h [C]:**

| Dry-road speed | Stopping distance (μ 0.8) | Equivalent at μ 0.25 | Equivalent at μ 0.15 | Equivalent at μ 0.08 |
|---|---|---|---|---|
| 40 | 35.6 m | 30 | 26 | 21 |
| 50 | 47.0 m | 37 | 31 | 25 |
| 60 | 59.4 m | 43 | 36 | 28 |
| 70 | 72.7 m | 49 | 41 | 32 |
| 80 | 87.0 m | 56 | 46 | 36 |

- At 80 km/h on μ 0.15, matching the dry stopping distance needs a reduction of about 34 km/h, close to the 30–35 km/h attributed to the 1977 Swedish study. The observed adjustment of 4–9 km/h is a small fraction of that.
- **Design consequence:** an advisor should present the speed required by the physics and should not assume drivers adapt on their own. Hard-to-detect slippery conditions are where drivers respond to signs and limits the most (Rämä's 5.3 km/h against 3.4 km/h).
- **Age of evidence:** the ice speed data come from 1977 to 1999, before widespread ABS and ESC, so modern adaptation may differ.

### Gaps
- No modern observational study of speed on verified black ice was read.
- No verified quantified darkness-only speed reduction.
- The 1977 Swedish authors were not confirmed, and neither was the 1995 Finnish record.
