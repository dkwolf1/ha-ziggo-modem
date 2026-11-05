# Contributing

## Reporting issues

- Include logs
- Remove sensitive data
- Describe setup

## Development

- Use Python 3.14, the version used by the test job in CI
- Install test dependencies: `python -m pip install -r requirements_test.txt`
- Run tests with full config-flow coverage: `python -m pytest -q --cov=custom_components.ziggo_modem.config_flow --cov-report=term-missing --cov-fail-under=100`
- Install pre-commit if needed: `python -m pip install pre-commit`
- Run all hooks: `pre-commit run --all-files`
- Check `git status` afterward; formatting hooks may update files
- Follow Home Assistant coding standards and test on real hardware if possible

Pull requests also run tests, pre-commit, Hassfest and HACS validation in CI.

## Pull Requests

- Keep changes focused
- Describe what and why
- No breaking changes without discussion
