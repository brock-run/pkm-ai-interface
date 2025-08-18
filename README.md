# pkm-ai-interface

This repository provides a minimal proof of concept for interacting with Roam Research via a middle layer.

## CI/CD Strategy

The `ci.yml` workflow under `.github/workflows` runs on every pull request and push to `main`.

1. **Lint & Test** – installs dependencies then runs `ruff check`, `black --check`, and `pytest`.
2. **Security** – executes `bandit` to detect common Python issues.
3. **Build & Deploy** – on pushes to `main` the project builds (`sam build` or `terraform init`) and deploys using either `sam deploy` or `terraform apply` depending on the `DEPLOY_TOOL` variable. AWS credentials are provided through `aws-actions/configure-aws-credentials`; Terraform is installed via `hashicorp/setup-terraform` and SAM via `pip install`.
4. **Notifications** – if `SLACK_WEBHOOK_URL` is set, results are posted to Slack.

### Future Enhancements

- Add CodeQL scanning.
- Create per-PR preview stacks.
- Expand tests for the analytics logging endpoint.

See `TODO.md` for an up-to-date task list.
