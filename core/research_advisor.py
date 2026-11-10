"""ResearchAdvisor: what published research suggests, as explicit cited formulas.

This is deliberately not a neural network. Training a network on published figures would hide
outside assumptions inside its weights. Nothing here learns from this road's data, and the result
is advisory only: it never sets the published limit.

Evidence and read-status of every figure: reports/Speed limit advisor evidence.md
"""
import math
from dataclasses import asdict, dataclass

from core import config, router
from core.confidence import Confidence, HIGH, LOW, MEDIUM

NOT_APPLICABLE = "Not applicable"
DRY, WET, BLACK_ICE = "dry", "wet", "black ice"
GRAVITY_MS2 = 9.81


@dataclass(frozen=True)
class Source:
    citation: str
    url: str


@dataclass(frozen=True)
class CandidateEvidence:
    limit_kmh: int
    stopping_m: float
    fits: bool
    mean_speed_change_kmh: float
    injury_pct: float
    injury_low_pct: float
    injury_high_pct: float
    killed_pct: float
    killed_low_pct: float
    killed_high_pct: float


@dataclass(frozen=True)
class ResearchAdvice:
    limit_kmh: int
    reduction_kmh: int
    surface: str
    friction: float
    dark: bool
    available_distance_m: float
    stress_limit_kmh: int
    candidates: list
    stopping_evidence: Confidence
    crash_evidence: Confidence
    air_evidence: Confidence
    headline: str
    reasons: list
    caveats: list
    sources: list

    def summary(self) -> dict:
        return {
            "limit_kmh": self.limit_kmh, "headline": self.headline, "surface": self.surface,
            "friction": self.friction, "dark": self.dark, "available_distance_m": self.available_distance_m,
            "stress_limit_kmh": self.stress_limit_kmh, "stopping_evidence": asdict(self.stopping_evidence),
            "crash_evidence": asdict(self.crash_evidence),
            "air_evidence": asdict(self.air_evidence) if self.air_evidence else None,
        }


WALLMAN = Source("Wallman, C.-G., Åström, H. (2001). Friction measurement methods and the correlation "
                 "between road friction and traffic safety. VTI meddelande 911A.",
                 "https://www.diva-portal.org/smash/get/diva2:673366/FULLTEXT01.pdf")
SVENDENIUS = Source("Svendenius, J. (2007). Validation of the Brush Model towards VTI-measurement data "
                    "recorded in Arjeplog 2006. Lund University, TFRT-7617.",
                    "https://lup.lub.lu.se/search/files/4590032/8627412.pdf")
IOWA = Source("Iowa DOT Design Manual, Section 6D-1 Sight Distance (2015), reproducing AASHTO values.",
              "https://documents.iowa.gov/home/download/9592894")
ELVIK_2004 = Source("Elvik, R., Christensen, P., Amundsen, A. (2004). Speed and road accidents: an "
                    "evaluation of the Power Model. TØI report 740/2004.", "https://www.trg.dk/elvik/740-2004.pdf")
ELVIK_2014 = Source("Elvik, R. (2014). Fart og trafikksikkerhet: nye modeller. TØI report 1296/2014.",
                    "https://www.toi.no/getfile.php/1335297-1394518277/Publikasjoner/T%C3%98I%20rapporter/2014/"
                    "1296-2014/1296-2014-elektronisk.pdf")
AAA = Source("AAA (2015). Test Results: Automotive Headlamp Systems, Fact Sheet.",
             "https://newsroom.aaa.com/wp-content/uploads/2019/06/AET-Headlights-Fact-Sheet.pdf")
RAMA_2003 = Source("Rämä, P., Schirokoff, A., Rajamäki, R. (2003). Finnra Reports 54/2003.",
                   "https://www.tieh.fi/julkaisut/pdf/3200841_vms-turva.pdf")
SALZBURG = Source("Thudium, J., Chélala, C. (2014). T80 Salzburg A1 evaluation.",
                  "http://www.salzburg.gv.at/fileadmin/SP-Dateien/umweltnaturwasser_/Documents/Umwelt/"
                  "be_t80salzburg2014v2.pdf")
BEL_ROSELL = Source("Bel, G., Rosell, J. (2013). Transportation Research Part D 23, 90-97.",
                    "https://hdl.handle.net/2445/44528")
AQEG = Source("AQEG (2019). Non-Exhaust Emissions from Road Traffic. Defra PB14581.",
              "https://uk-air.defra.gov.uk/assets/documents/reports/cat09/"
              "1907101151_20190709_Non_Exhaust_Emissions_typeset_Final.pdf")
EU_2024 = Source("Directive (EU) 2024/2881 on ambient air quality.",
                 "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202402881")


def stopping_distance_m(speed_kmh: float, friction: float, reaction_s: float = config.RESEARCH_REACTION_S) -> float:
    """Reaction distance plus braking distance on a level road."""
    speed_ms = speed_kmh / 3.6
    return speed_ms * reaction_s + speed_ms ** 2 / (2.0 * GRAVITY_MS2 * friction)


def mean_speed_change_kmh(limit_kmh: float, compliance: float = config.RESEARCH_COMPLIANCE) -> float:
    """A posted cut only partly reaches actual mean speed."""
    return compliance * (limit_kmh - config.DEFAULT_LIMIT)


def crash_change_pct(limit_kmh: float, beta: float, compliance: float = config.RESEARCH_COMPLIANCE) -> float:
    """Exponential Model applied to the expected mean-speed change, in percent."""
    return (math.exp(beta * mean_speed_change_kmh(limit_kmh, compliance)) - 1.0) * 100.0


def _surface(water_um: float, temperature_c: float) -> str:
    if router.is_black_ice(water_um, temperature_c):
        return BLACK_ICE
    return WET if water_um > 0 else DRY


def _highest_fitting(friction: float, available_m: float):
    fitting = [limit for limit in config.ALLOWED_LIMITS if stopping_distance_m(limit, friction) <= available_m]
    return max(fitting) if fitting else None


def _candidate(limit: int, friction: float, available_m: float) -> CandidateEvidence:
    low, high = config.RESEARCH_COMPLIANCE_LOW, config.RESEARCH_COMPLIANCE_HIGH
    stopping = stopping_distance_m(limit, friction)
    return CandidateEvidence(
        limit, stopping, stopping <= available_m, mean_speed_change_kmh(limit),
        crash_change_pct(limit, config.RESEARCH_BETA_INJURY),
        crash_change_pct(limit, config.RESEARCH_BETA_INJURY, low),
        crash_change_pct(limit, config.RESEARCH_BETA_INJURY_STRESS, high),
        crash_change_pct(limit, config.RESEARCH_BETA_KILLED),
        crash_change_pct(limit, config.RESEARCH_BETA_KILLED, low),
        crash_change_pct(limit, config.RESEARCH_BETA_KILLED_STRESS, high),
    )


def _stopping_evidence(surface: str, dark: bool) -> Confidence:
    if surface == BLACK_ICE:
        return Confidence(MEDIUM, [
            "Black ice is the strongest case for a lower limit, and it rests on stopping physics",
            "Friction on ice is uncertain: published values run from 0.05 to 0.30, and 0.15 is used here",
            "No study has measured the crash effect of a limit cut specifically under black ice",
        ])
    if dark and surface == WET:
        return Confidence(MEDIUM, [
            "Darkness is better supported as a modifier of poor road conditions than on its own",
            "The 91 m detection distance is an upper bound, and dark obstacles are seen later",
        ])
    if dark:
        return Confidence(LOW, [
            "Darkness alone has the weakest case: two Finnish systems tried a darkness rule and dropped it",
            "The 91 m detection distance is an upper bound, and dark obstacles are seen later",
        ])
    return Confidence(HIGH, ["Stopping on a dry or wet road in daylight is well established"])


def _crash_evidence(limit: int) -> Confidence:
    if limit == config.DEFAULT_LIMIT:
        return Confidence(NOT_APPLICABLE, ["No limit reduction is suggested, so there is no effect to estimate"])
    transfer = "No study tests this limit on an 80 km/h road, so the estimate is transferred from other roads"
    calculated = "Calculated from published coefficients, and the injury coefficient is disputed (0.034 or 0.06)"
    compliance = "Assumes one quarter of the posted cut reaches mean speed, with no value published for advisory signs"
    if limit >= 70:
        return Confidence(MEDIUM, [transfer, calculated, compliance])
    return Confidence(LOW, [transfer, calculated, compliance,
                            f"{limit} km/h lies outside the range of most deployments and studies"])


def _air_finding(air):
    if air is None or (air.pm10 <= config.PM10_LIMIT and air.no2 <= config.NO2_LIMIT):
        return None, None
    reasons = ["No published evaluation covers cutting a limit below 80 km/h on a free-flowing road",
               "Measured benefits stop at cuts down to 80 km/h, and station data can show no gain at all"]
    if air.pm10 > config.PM10_LIMIT:
        reasons.append("PM10 is a poor trigger: most road PM10 comes from tyres and brakes, not exhaust")
    note = ("Air quality is above the EU limit, but research does not support a reduction below 80 km/h "
            "for air quality alone")
    return Confidence(LOW, reasons), note


SURFACE_NAMES = {DRY: "Dry road", WET: "Wet road", BLACK_ICE: "Black ice"}


def _headline(surface, dark, available, limit, air_note) -> str:
    """One short justification for the panel."""
    conditions = f"{SURFACE_NAMES[surface]} in {'darkness' if dark else 'daylight'}"
    if limit == config.DEFAULT_LIMIT:
        text = f"{conditions}: 80 km/h can stop within the {available:g} m available."
    else:
        text = f"{conditions}: {limit} km/h is the fastest limit that can stop within {available:g} m."
    if air_note:
        text += " Air quality alone does not justify going below 80 km/h."
    return text


def _reasons(surface, friction, dark, available, limit, stress_limit, candidates, air_note) -> list:
    sight = "low-beam detection distance" if dark else "design stopping distance for 80 km/h"
    chosen = next(c for c in candidates if c.limit_kmh == limit)
    reasons = [f"Surface: {surface}, friction {friction:g}. Available distance: {available:g} m ({sight})."]
    if limit == config.DEFAULT_LIMIT:
        reasons.append(f"80 km/h stops in {chosen.stopping_m:.1f} m, within the {available:g} m available, "
                       "so stopping distance gives no reason to reduce.")
    else:
        faster = next(c for c in candidates if c.limit_kmh == limit + 10)
        reasons.append(f"{limit} km/h is the highest limit that stops within {available:g} m "
                       f"({chosen.stopping_m:.1f} m). {faster.limit_kmh} km/h would need {faster.stopping_m:.1f} m.")
    if surface == BLACK_ICE:
        stress = (f"{stress_limit} km/h" if stress_limit
                  else f"even 40 km/h cannot stop within {available:g} m")
        reasons.append(f"On very slippery ice (friction {config.RESEARCH_ICE_STRESS_FRICTION:g}): {stress}.")
        reasons.append("In practice, operators post 60 to 80 km/h for ice on 100 km/h roads, "
                       "and no system on an 80 km/h road has reported crash results.")
    if air_note:
        reasons.append(air_note + ".")
    return reasons


def _sources(surface, dark, air_finding) -> list:
    sources = [WALLMAN, IOWA, ELVIK_2004, ELVIK_2014]
    if surface == BLACK_ICE:
        sources += [SVENDENIUS, RAMA_2003]
    if dark:
        sources.append(AAA)
        if surface != BLACK_ICE:
            sources.append(RAMA_2003)
    if air_finding:
        sources += [SALZBURG, BEL_ROSELL, AQEG, EU_2024]
    return sources


CAVEATS = [
    "Advisory only: this research estimate is not used to set the published limit.",
    "It does not predict near-accidents. No published model links speed to near-accidents.",
    "It has not been validated on this road. Crash figures are calculations from published coefficients, "
    "and they apply to free-flowing traffic.",
]


def advise(readings: dict, air=None) -> ResearchAdvice:
    dark = router.is_dark(router.lux_to_millilux(readings["illuminance_lux"]))
    surface = _surface(readings["water_um"], readings["temperature_c"])
    friction = config.RESEARCH_FRICTION[surface]
    available = config.RESEARCH_DARK_DISTANCE_M if dark else config.RESEARCH_DAY_DISTANCE_M
    candidates = [_candidate(limit, friction, available) for limit in config.ALLOWED_LIMITS]
    limit = _highest_fitting(friction, available) or min(config.ALLOWED_LIMITS)
    stress_limit = _highest_fitting(config.RESEARCH_ICE_STRESS_FRICTION, available) if surface == BLACK_ICE else None
    air_evidence, air_note = _air_finding(air)
    return ResearchAdvice(
        limit, config.DEFAULT_LIMIT - limit, surface, friction, dark, available, stress_limit, candidates,
        _stopping_evidence(surface, dark), _crash_evidence(limit), air_evidence,
        _headline(surface, dark, available, limit, air_note),
        _reasons(surface, friction, dark, available, limit, stress_limit, candidates, air_note),
        list(CAVEATS), _sources(surface, dark, air_evidence),
    )
