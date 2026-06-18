# Tech Stack

## Language

- Python (targets 3.9–3.13, CI runs on 3.13)

## Key Dependencies

| Library | Purpose |
|---------|---------|
| PySide6 (>=6.5.1.1) | Qt bindings for GUI widgets |
| opencv-contrib-python-headless (>=4.10) | Computer vision, video capture |
| numpy (>=2.0.0) | Array/matrix operations |
| scikit-surgerycore | Core utilities (transforms, config) |
| scikit-surgeryimage | Image acquisition, processing |
| scikit-surgeryvtk | VTK overlay rendering |
| scikit-surgeryarucotracker | ArUco/ChArUco marker tracking |
| scikit-surgerycalibration | Camera calibration |

## Build & Packaging

- setuptools with `setup.py` / `setup.cfg`
- Versioning via **versioneer** (PEP 440 style from git tags prefixed `v`)
- No pyproject.toml yet — uses traditional setup.py

## Dev Dependencies

- pytest, pytest-qt — testing
- coverage, coveralls — coverage reporting
- pylint — linting (config in `tests/pylintrc`)
- tox — test environment orchestration
- pyfakefs, mock, parameterized — test helpers
- sphinx — documentation

## Common Commands

All Python commands should be run using the tox-managed virtualenv at `.tox/test/bin/python`. Tox installs all requirements from the top-level requirements files.

```bash
# Run tests with coverage (creates/uses .tox/test venv)
tox -e test

# Run linter
tox -e lint

# Build docs
tox -e docs

# Run a Python command using the tox venv directly
.tox/test/bin/python -m pytest -v -s

# Run a script with the tox venv
.tox/test/bin/python sksurgerystereorenderer.py --help
```

## CI/CD

- GitHub Actions (`.github/workflows/ci.yml`)
- Coverage reported to Coveralls
- Docs hosted on Read the Docs
