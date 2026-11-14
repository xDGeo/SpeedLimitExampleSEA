- [ ]

# SpeedLimit MVP

Sets a highway speed limit from light, weather and air quality. Case study for Software Engineering for AI. Not for use on real roads.

**Main result:** the data is clean, the system works end to end, and the neural network does not meaningfully beat guessing the average (cross-validated skill +0.4%). Near-accidents in this data behave like random noise, so every network-based limit is shown with Low confidence.

## How it decides

| Situation                | Who decides                                                     |
| ------------------------ | --------------------------------------------------------------- |
| Dark or black-ice danger | A PyTorch ensemble of 10 small networks                         |
| Air quality              | A local LLM (Ollama, `qwen3:8b`), using the Open-Meteo forecast |
| No reason to reduce      | Fixed rule: 80 km/h                                             |
| Several reasons          | The strictest limit wins                                        |

Every network and LLM result shows a confidence level and the reasons for it. An operator can override any limit.

## Documents

| Document                                                                                 | Contents                                                       |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| [HOW_TO_USE.md](HOW_TO_USE.md)                                                           | Setup, running the app, reading the screen, troubleshooting    |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)                                             | Architecture, UML diagrams, choices and their reasons, results |
| [docs/DATA_QUALITY.md](docs/DATA_QUALITY.md)                                             | What was found, fixed and validated, with plots                |
| [docs/PARAMETER_RANGES.md](docs/PARAMETER_RANGES.md)                                     | Normal and abnormal values with units                          |
| [docs/SYNTHETIC_DATA.md](docs/SYNTHETIC_DATA.md)                                         | Why generating more data does not help                         |
| [reports/Speed limit advisor evidence.md](reports/Speed%20limit%20advisor%20evidence.md) | Cited evidence behind the "Research suggests" panel            |
| [CLAUDE.md](CLAUDE.md)                                                                   | Guidance for working on this repository with Claude Code       |

## Quick start

```bash
uv venv --python 3.12 .venv
```

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

```bash
.venv/bin/python -m streamlit run app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
```

Ollama must be running for the LLM path. See [HOW_TO_USE.md](HOW_TO_USE.md).
