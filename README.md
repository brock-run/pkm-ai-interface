# pkm-ai-interface

This repository provides a minimal proof of concept for interacting with Roam Research via a middle layer.

## CI/CD Strategy

The `ci.yml` workflow under `.github/workflows` runs on every pull request and push to `main`.

1. **Lint & Test** – installs dependencies, runs `ruff`, `black --check`, and `pytest`.
2. **Security** – executes `bandit` to detect common Python issues.
3. **Deploy** – on pushes to `main` the project deploys using either `sam deploy --guided` or `terraform apply` depending on the `DEPLOY_TOOL` variable. AWS credentials are provided through `aws-actions/configure-aws-credentials`.
4. **Notifications** – results are posted to Slack via the `SLACK_WEBHOOK_URL` secret.

### Future Enhancements

- Add CodeQL scanning.
- Create per-PR preview stacks.
- Expand tests for the analytics logging endpoint.
