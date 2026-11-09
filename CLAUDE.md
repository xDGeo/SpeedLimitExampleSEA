# SpeedLimit MVP

Case study for Software Engineering for AI. The system sets a highway speed limit from light, weather and air quality. A PyTorch ensemble handles dark and black-ice conditions, a local LLM handles air quality, and plain rules handle everything else.

## Commands

Use the project environment. System Python is 3.15 and has no PyTorch.

```bash
.venv/bin/python -m pytest -q                 # all tests, live ones skip if Ollama is down
.venv/bin/python -m pytest -q -m "not live"   # no real Ollama
.venv/bin/python analyze_data.py              # clean, validate, plots, parameter ranges
.venv/bin/python train.py                     # stops if validation fails
.venv/bin/python check_retraining.py          # Year N+1 analysis
.venv/bin/python -m streamlit run app.py      # GUI, add --server.address localhost
plantuml -tpng docs/uml/*.puml                # render diagrams
```

Setup: `uv venv --python 3.12 .venv`, then `uv pip install --python .venv/bin/python -r requirements.txt`.

## Working rules

- **Tests first.** Write or change the test, watch it fail for the right reason, then change the code. Each component has at least five test cases.
- **Allowed-to-use is enforced.** `docs/uml/01_architecture_*.puml` and `tests/test_architecture.py` define which module may import which. If a change needs a new dependency, update both on purpose.
- Only `core/llm_manager.py` talks to the LLM, and every call goes through its guardrails and log.
- Only `core/features.py` defines model features, so training and live inputs cannot drift apart.
- Thresholds, sensor mappings and allowed limits live in `core/config.py`.
- The LLM is the user's local Ollama (`qwen3:8b`). Do not add a cloud LLM backend.
- Show units on every displayed value. Every NN or LLM result carries a confidence level and its reasons.
- Report results honestly. Never claim the network has skill unless the report shows it.

## Data facts (already verified, do not re-derive)

- Near-accidents per hour behave like pure Poisson noise (variance/mean = 1.00), and the same hours in Year N and N+1 do not correlate. Expect the network to show no skill.
- Dark or black-ice hours average above 1 near-accident per hour at every limit, so REQ1 is mostly unreachable. Lower limits look riskier in the data; that is noise or confounding.
- 80 km/h never occurs in dark or black-ice hours, so the network is only asked about 40 to 70 km/h.
- Year N+1 sensor readings are identical to Year N, and that file has no header. Near-accidents still differ (964 vs 822).
- Accident hours run 1 to 24, sensor hours 0 to 23. The code subtracts 1.
- Illuminance sensors report lux, while SPEC1 is in millilux. Conversion happens only in `core/router.py`.
- Sensor code `T` means temperature and traffic. Sensor 16 is traffic. Sensor 19 is undocumented and treated as temperature.
- Licence plates are dropped at load and must never reach features or logs.

## Agreed behaviour that looks odd

When no limit meets REQ1, the policy uses a fixed 60 km/h and requests operator review, even if another limit has a lower prediction. On the current data this applies to every dark or black-ice hour, so the network does not change the outcome. Do not go back to "lowest prediction": it chose 70 km/h for every such hour. See `docs/ARCHITECTURE.md`.

## Do not commit

Lecture PDFs or the slide deck. Run logs in `artifacts/` are ignored by `.gitignore`.
