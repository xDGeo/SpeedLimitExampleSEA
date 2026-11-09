"""Thresholds, sensor mappings, limits and paths. The single place to change them."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
DOCS_DIR = ROOT / "docs"
PLOTS_DIR = DOCS_DIR / "plots"

SENSOR_TYPES = DATA_DIR / "Case_Study_Speed_Limit_SensorTypes_V100.csv"
SENSORS = DATA_DIR / "Case_Study_Speed_Limit_Sensors_V100.csv"
READINGS_YEAR_N = DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv"
READINGS_YEAR_N1 = DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv"
ACCIDENTS_YEAR_N = DATA_DIR / "Case_Study_Speed_Limit_AccidentsYearN_V100.csv"
ACCIDENTS_YEAR_N1 = DATA_DIR / "AccidentsYearNPlus1_V100.csv"

MODEL_FILE = ARTIFACTS_DIR / "model.pt"
DECISION_LOG = ARTIFACTS_DIR / "decisions.jsonl"
LLM_LOG = ARTIFACTS_DIR / "llm_calls.jsonl"
PARAMETER_BANDS = ARTIFACTS_DIR / "parameter_bands.json"

# SPEC1 and SPEC2
DARK_BELOW_MILLILUX = 500.0
ICE_WATER_ABOVE_UM = 1000.0
ICE_TEMPERATURE_BELOW_C = 0.0

# Speed limits in km/h
DEFAULT_LIMIT = 80
ALLOWED_LIMITS = (40, 50, 60, 70, 80)
CANDIDATE_LIMITS = (40, 50, 60, 70)
ALLOWED_REDUCTIONS = (0, 10, 20, 30, 40)
REQ1_TARGET_PER_HOUR = 1.0
# Used only if the network cannot run: the limit with the most dark or ice evidence.
NN_FAILURE_LIMIT = 60

# Sensors. Sensor 16 is traffic although its type code T is shared with temperature.
SENSOR_KIND = {
    1: "water", 8: "water", 11: "water",
    2: "light", 9: "light", 12: "light",
    3: "noise",
    4: "humidity",
    5: "wind_direction", 13: "wind_direction",
    6: "wind_strength", 14: "wind_strength",
    15: "temperature", 18: "temperature", 19: "temperature",
    16: "traffic",
    -1: "speed_limit",
}
SPEED_LIMIT_SENSOR = -1
SENSOR_GROUPS = {
    "lux": (2, 9, 12),
    "water_um": (1, 8, 11),
    "temperature_c": (15, 18, 19),
    "wind_strength": (6, 14),
    "humidity_pct": (4,),
    "traffic_cars_s": (16,),
}
REDUNDANT_GROUPS = ("lux", "water_um", "temperature_c")
SENSOR_DAYS = 31

# Allowed ranges from SensorTypes.csv, resolved by kind because code T is ambiguous.
RANGES = {
    "water": (0.0, 10000.0),
    "light": (0.0, 1000000.0),
    "noise": (60.0, 120.0),
    "humidity": (0.0, 100.0),
    "wind_direction": (0.0, 360.0),
    "wind_strength": (0.0, 300.0),
    "temperature": (-30.0, 70.0),
    "traffic": (0.0, 50.0),
    "speed_limit": (40.0, 80.0),
}
TABLE_COLUMN_KIND = {
    "lux": "light", "water_um": "water", "temperature_c": "temperature",
    "wind_strength": "wind_strength", "humidity_pct": "humidity",
    "traffic_cars_s": "traffic", "speed_limit": "speed_limit",
}
MAX_GAP_HOURS = 6
LOW_SUPPORT_HOURS = 30

NEAR_ACCIDENT_KINDS = ("SkidAngle", "CloseCarCm", "CloseGuardrailCm")
REAL_ACCIDENT_KINDS = ("Damage", "Injured")

# Air quality, EU Directive 2008/50/EC, in µg/m³
PM10_LIMIT = 50.0
NO2_LIMIT = 200.0
AIR_INPUT_MAX = 2000.0

OPEN_METEO_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
LATITUDE = 48.21   # Vienna
LONGITUDE = 16.37
FORECAST_HOURS = 6
HTTP_TIMEOUT_S = 10.0

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:8b"
OLLAMA_TIMEOUT_S = 90.0
LLM_SAMPLES = 3

# Confidence thresholds
SKILL_HIGH_PCT = 5.0
AGREEMENT_HIGH_WIDTH = 0.25
AGREEMENT_MEDIUM_WIDTH = 0.50
SUPPORT_HIGH_HOURS = 100
SUPPORT_MEDIUM_HOURS = 30

# Retraining
KS_DRIFT_THRESHOLD = 0.1
RETRAIN_GAIN_PCT = 5.0
