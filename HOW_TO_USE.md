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

### 3. Press Set limit now

The first answer for new air-quality values takes around 10 seconds, because the local LLM is asked three times. Repeated values are remembered and are faster.

### 4. Read the decision

| You see | Meaning |
|---|---|
| Speed limit, Reduction | The result in km/h. Reduction is measured from 80 km/h |
| Reasons | Why this limit applies |
| REQ1 not met | No limit is predicted to keep near-accidents at or below 1 per hour, so the fixed 60 km/h applies |
| Operator review needed | A person should look at this limit |
| Router | A fixed rule, so it has no uncertainty |
| Neural network level | High, Medium or Low, with one reason per check |
| Candidate table | Predicted near-accidents per hour for each limit, the 90% range of the 10 networks, and the share of networks at or below 1 per hour |
| LLM level | Based on how many of the 3 answers agreed. It shows consistency, not correctness |
| No confidence | The LLM gave no usable answer and a fixed rule decided |

The explanation behind the levels is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### 5. Run on a timer

Turn on **Auto-run on a timer** and set the interval in seconds (3600 = hourly, minimum 5). Cycles use the values currently on the screen. Auto-run stops if you close the page.

### 6. Override

Pick a limit under **Operator override** and press **Apply override**. It is published at once and logged. The next automatic or manual cycle replaces it.

### Try these

| Scenario | Expected result |
|---|---|
| Clear day with good air | 80 km/h |
| Dark night or Icy night | Network path, normally the fixed 60 km/h, REQ1 not met, operator review, Low confidence |
| Black ice in daylight | Network path |
| Clear day, manual PM10 120 and NO₂ 250 µg/m³ | The LLM reduces the limit (50 km/h when tested) |
| Icy night with that poor air | The strictest proposal wins |
| Temperature 500 °C | Input rejected, the limit does not change |

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
