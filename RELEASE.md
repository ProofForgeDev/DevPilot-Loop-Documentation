# Release Process

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer).

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions
- **PATCH** version for backward-compatible bug fixes

## Release Checklist

### Pre-Release
- [ ] All tests passing (`pytest -v`)
- [ ] Code coverage ≥ 90% (`pytest --cov=skills --cov-report=term-missing`)
- [ ] Security scan clean (`bandit -r skills/`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml`

### Release
1. Create release branch: `git checkout -b release/vX.Y.Z`
2. Update version numbers
3. Update CHANGELOG.md
4. Run full test suite
5. Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. Push tag: `git push origin vX.Y.Z`
7. Create GitHub Release with release notes

### Post-Release
- [ ] Merge release branch to main
- [ ] Delete release branch
- [ ] Announce on community channels

## Branch Strategy

- **main**: Stable, production-ready code
- **develop**: Integration branch for next release
- **feature/***: New features
- **fix/***: Bug fixes
- **release/***: Release preparation

## Contributors

To add a new code owner, update `CODEOWNERS` file and get approval from maintainers.
