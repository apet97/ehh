# Pull Request

## Description

<!-- Briefly describe your changes -->

## Type of Change

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📚 Documentation
- [ ] 🔧 Configuration
- [ ] ♻️  Refactoring
- [ ] 🧪 Tests
- [ ] 🚀 Performance
- [ ] 🔒 Security

## Checklist

### Code Quality
- [ ] Code follows project style (ruff, black)
- [ ] All tests pass (`pytest -v`)
- [ ] No new linting errors (`ruff check app/ tests/`)
- [ ] Type hints added where appropriate

### Testing
- [ ] Smoke tests pass (`./scripts/smoke.sh`)
- [ ] `/healthz` endpoint works
- [ ] `/readyz` endpoint works
- [ ] Added tests for new functionality
- [ ] Existing tests still pass

### Security
- [ ] No secrets committed (checked with gitleaks)
- [ ] Environment variables documented in `.env.example`
- [ ] API keys/tokens read from env only
- [ ] No hardcoded credentials

### Documentation
- [ ] README updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] API documentation updated (if endpoints changed)
- [ ] Comments added to complex code

### Deployment
- [ ] Docker build succeeds (`docker build .`)
- [ ] Docker compose up works (`docker compose up`)
- [ ] No breaking changes to existing endpoints
- [ ] Backward compatibility maintained

## Testing Instructions

<!-- How should reviewers test this? -->

1.
2.
3.

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

## Related Issues

<!-- Link related issues: Fixes #123, Closes #456 -->

## Additional Notes

<!-- Any additional context, concerns, or questions -->
