# 🧪 Darkelf Pytests

**Official centralized pytest suite for the Darkelf Labs ecosystem.**

Darkelf Pytests provides automated testing for Darkelf Labs projects including:

- 🌑 Darkelf Shadow
- 🍫 Darkelf Cocoa
- 🛡️ Darkelf SecureAudit
- 🔒 Darkelf Dependency Guardian
- 🔍 Future Darkelf projects

---

# Features

- ✅ Unit tests
- ✅ Integration tests
- ✅ Regression tests
- ✅ Security validation
- ✅ CLI testing
- ✅ Sample project testing
- ✅ GitHub Actions support
- ✅ Coverage reporting

---

# Repository Layout

```text
Darkelf-Pytests/
│
├── tests/
│   ├── test_secureaudit.py
│   ├── test_dependency_guardian.py
│   ├── test_shadow.py
│   ├── test_cocoa.py
│   └── data/
│
├── pytest.ini
├── pyproject.toml
├── README.md
├── requirements.txt
└── .github/
```

---

# Installation

```bash
git clone https://github.com/Darkelf-Labs/Darkelf-Pytests.git

cd Darkelf-Pytests

python -m pip install -e .
```

---

# Run All Tests

```bash
pytest
```

---

# Run Individual Test Suites

Darkelf Cocoa

```bash
pytest -m cocoa
```

Darkelf Shadow

```bash
pytest -m shadow
```

Darkelf SecureAudit

```bash
pytest -m secureaudit
```

Dependency Guardian

```bash
pytest -m dependencyguardian
```

---

# Coverage

```bash
pytest --cov
```

---

# GitHub Actions

This repository is designed to work with GitHub Actions.

Every push or pull request can automatically:

- execute pytest
- collect coverage
- verify CLI behavior
- validate expected outputs
- detect regressions

---

# License

LGPL-3.0-or-later

---

# Darkelf Labs

Privacy-first software engineered for security research, defensive development, and modern browser technologies.
