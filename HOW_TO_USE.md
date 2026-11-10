# How to use SpeedLimit

SpeedLimit sets a highway speed limit from light, weather and air quality. It runs on your own computer. This is an MVP for a case study and must not be used on real roads.

## What you need

- macOS or Linux with [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) with the `qwen3:8b` model (`ollama pull qwen3:8b`)
- Internet access for the air-quality forecast (optional, you can enter values by hand)
- PlantUML, only if you want to redraw the diagrams

## First-time setup

```bash
git clone git@github.com:xDGeo/SpeedLimitExampleSEA.git speedlimit
```

```bash
cd speedlimit
```

```bash
uv venv --python 3.12 .venv
```

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

The repository already contains a trained model, so you can go straight to the app.

## Start the app

On this Mac, double-click `Start SpeedLimit.command` in the folder above `speedlimit/`. It starts Ollama if needed, starts the app and opens the page. `Stop SpeedLimit.command` shuts both down.

To start it by hand, make sure Ollama is running, then:

```bash
.venv/bin/python -m streamlit run app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
```

Open http://localhost:8501.

## Using the screen

### 1. Enter the conditions

Type the values on the left, or press a scenario button to fill them in.

| Field | Unit | Allowed range |
|---|---|---|
| Illuminance | lux | 0 to 1,000,000 |
| Water on road | µm | 0 to 10,000 |
| Temperature | °C | -30 to 70 |
| Wind strength | km/h | 0 to 300 |
| Humidity | % | 0 to 100 |
| Traffic | cars/s | 0 to 50 |
| PM10 (manual air quality) | µg/m³ | 0 to 2,000 |
| NO₂ (manual air quality) | µg/m³ | 0 to 2,000 |

Each field shows a badge. **Normal** and **Abnormal** are defined in [docs/PARAMETER_RANGES.md](docs/PARAMETER_RANGES.md), and the same table is at the bottom of the screen. Rules change the limit. Data bands only describe what was typical in January.

### 2. Choose the air-quality source

By default the app uses the Open-Meteo forecast for Vienna and takes the worst PM10 and NO₂ of the next 6 hours. Turn on **Enter air quality manually** to try other values.

### 3. Press Calculate

**Calculate** is at the top right. The first answer for new air-quality values takes about 10 seconds, because the local LLM is asked three times. Repeated values are remembered and are faster.

If you change any condition after calculating, a yellow note says **Conditions have changed**. Press Calculate again to update.

### 4. Read the recommendation

From top to bottom:

| You see | Meaning |
|---|---|
| **Published limit** (green or blue bar) | The limit in force now, and who set it: the system (green) or an operator override (blue). A newly opened page shows the last published limit |
| **Recommended limit** | What the system recommends, in km/h: the lower of the neural network and the LLM, or 80 km/h if neither gives a reason to reduce |
| REQ1 not met / Operator review needed | A person should look at this limit |
| **Three cards** | Each shows its own speed in km/h, a confidence or evidence level, and one line saying why |
| Details (fold-out) | The reasons behind each confidence level, the network's prediction for each limit, the LLM's three sampled speeds, the research tables and sources |

The three cards:

| Card | Speed it shows | Used for the recommendation? |
|---|---|---|
| **Neural network (dark or black ice)** | Its limit in darkness or black ice, or "Not used" otherwise. When no limit reaches at most 1 near-accident per hour, the fixed 60 km/h applies | Yes |
| **LLM (air quality)** | The local LLM's limit for the current PM10 and NO₂ | Yes |
| **Research (expert evidence)** | The fastest limit that can still stop within the distance a driver can see, from published studies | No, comparison only |

Confidence levels: **High**, **Medium** or **Low**; **No confidence** means the LLM gave no usable answer and a fixed rule decided. LLM agreement shows consistency, not correctness. The neural network is always Low, because in testing it does not meaningfully beat guessing the average.

The research figures are calculations from published studies, not measurements on this road, and they say nothing about near-accidents. The evidence is in [the research report](reports/Speed%20limit%20advisor%20evidence.md), and the reasoning behind all levels is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### 5. Publish a different limit (override)

Use this when you disagree with the recommendation, for example after an accident or during road works. Choose a limit under **Publish a different limit** and press **Publish this limit**. The list starts at the limit currently published.

The bar at the top then says the limit was set by an operator override, and still shows what the system recommends. The override stays published until the next Calculate or timer cycle. Every override is logged.

### 6. Run on a timer

Open **Run automatically on a timer** at the bottom left, turn on **Auto-run**, and set the interval in seconds (3600 = hourly, minimum 5). Each cycle uses the values on the screen and publishes its recommendation. Auto-run stops if you close the page.

### Try these

| Scenario, then Calculate | Neural network | LLM | Research | Recommended |
|---|---|---|---|---|
| Clear day | Not used | 80 km/h | 80 km/h | 80 km/h |
| Dark night | 60 km/h, REQ1 not met | 80 km/h | 80 km/h | 60 km/h |
| Black ice in daylight | 60 km/h, REQ1 not met | 80 km/h | 50 km/h | 60 km/h |
| Icy night | 60 km/h, REQ1 not met | 80 km/h | 40 km/h | 60 km/h |
| Clear day, manual PM10 120 and NO₂ 250 µg/m³ | Not used | lower, 50 km/h when tested | 80 km/h | the LLM's value |
| Temperature 500 °C | | | | Input rejected, the published limit does not change |

LLM values assume good air from the forecast.

## Run the stages yourself

| Command | What it does | Output |
|---|---|---|
| `.venv/bin/python analyze_data.py` | Cleans and validates the data, draws the plots | `docs/plots/`, `docs/DATA_QUALITY.md`, `docs/PARAMETER_RANGES.md` |
| `.venv/bin/python train.py` | Validates, then trains and evaluates. Stops if validation fails | `artifacts/model.pt`, `artifacts/training_report.json` |
| `.venv/bin/python check_retraining.py` | Analyses Year N+1 | `artifacts/retraining_report.json` |
| `.venv/bin/python synthetic_experiment.py` | Tests whether generated data helps, without changing the model | `docs/SYNTHETIC_DATA.md`, `docs/plots/09_*.png`, `docs/plots/10_*.png`, `artifacts/synthetic_report.json` |
| `.venv/bin/python -m pytest -q` | Runs all tests. Live LLM tests skip if Ollama is down | |
| `.venv/bin/python -m pytest -q -m "not live"` | Runs the tests without Ollama | |
| `plantuml -tpng docs/uml/*.puml` | Redraws the diagrams | `docs/uml/*.png` |

Each decision is appended to `artifacts/decisions.jsonl`, and each LLM call to `artifacts/llm_calls.jsonl`.

## Troubleshooting

| Problem | Fix |
|---|---|
| "No trained model found" | Run `train.py`. Until then, dark or icy conditions use a fixed 60 km/h with a review flag |
| "No confidence" for the LLM | Start Ollama with `ollama serve` and check `ollama list` shows `qwen3:8b` |
| "Air quality unavailable" | The forecast could not be reached. Enter air quality manually or check your connection |
| Port 8501 is in use | Use `--server.port` with another number |
| Python 3.15 errors when installing PyTorch | Create the environment with `--python 3.12` as shown above |
