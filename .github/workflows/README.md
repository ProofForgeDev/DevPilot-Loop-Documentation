# CI/CD Pipeline

This directory contains GitHub Actions workflows for automated testing and deployment.

## Workflows

### ci.yml - Continuous Integration
- Runs on every push to main and pull requests
- Executes: lint, test, security scan, build

### deploy.yml - Deployment (Semi-final/Final)
- Triggers on tagged releases
- Deploys to staging/production environments

## Local Development

```bash
# Run all checks locally
make ci

# Run tests with coverage
make test

# Run security scan
make security-scan
```
