# Contributing

## Reporting issues

- Include logs
- Remove sensitive data
- Describe setup

## Development

- Use Python 3.14, the version used by the test job in CI
- Install test dependencies: `python -m pip install -r requirements_test.txt`
- To test the minimum supported Core version, use a separate environment
  and install `requirements_test_minimum.txt` instead.
- Run tests with full config-flow coverage: `python -m pytest -q --cov=custom_components.ziggo_modem.config_flow --cov-report=term-missing --cov-fail-under=100`
- Install pre-commit if needed: `python -m pip install pre-commit`
- Run all hooks: `pre-commit run --all-files`
- Check `git status` afterward; formatting hooks may update files
- Follow Home Assistant coding standards and test on real hardware if possible

Pull requests also run tests, pre-commit, Hassfest and HACS validation in CI.
The test matrix checks the minimum supported Core version and the pinned
current release. Update the latter in the workflow and `requirements_test.txt`
together when moving to a newer Core version.

The `Compatibility` check requires the HACS check, the full Core test matrix
and the dashboard card checks to pass. Keep this job name stable for the GitHub
ruleset.

The source and image for the bundled dashboard card live in
`custom_components/ziggo_modem/www/`. Keep them together so the module can load
the image from its own URL. Run the card tests with Node.js 24 using
`node --test tests/card/ziggo-modem-card.test.cjs`.

Modem fixtures in `tests/fixtures` use synthetic values in representative
response structures. Do not commit raw diagnostics, credentials or device
identifiers.

## Pull Requests

- Keep changes focused
- Describe what and why
- No breaking changes without discussion
