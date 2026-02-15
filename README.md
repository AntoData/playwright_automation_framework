# Playwright Test Automation Framework

## Summary

This project provides a framework to develop automated test cases using **Playwright**.

We use the public website below to illustrate how to use this framework:

https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login

The framework demonstrates:

- Browser automation using Playwright
- Test execution with Pytest

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright
```bash
playwright install
```

### 3. Install Project (from project root)
```bash
pip install -e .
```

### 4. Execute Tests (from project root)
```bash
pytest ./tests
```