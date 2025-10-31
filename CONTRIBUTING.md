# Contributing to NEXA

Thanks for contributing! This document describes the recommended workflow, branch and PR rules, code style, and testing expectations for the NEXA project.

Branching strategy
• `main` — protected, always green; releases and deployable artifacts only.
• `develop` (optional) — long-lived integration branch for the next release (if used).
• `feature/*` — new features and work-in-progress. Named like `feature/JIRA-123-connector`.
• `bugfix/*` — bug fixes. Named like `bugfix/fix-auth`.
• `hotfix/*` — critical fixes to `main`.

PR rules
1. Open a pull request from a topic branch into `develop` (or `main` if the repo uses trunk-based flow).
2. Link related Jira ticket(s) in the PR description and include a short summary of the change, rationale, and testing steps.
3. Use meaningful PR titles. Include the Jira ticket ID when applicable.
4. Add at least two reviewers for significant changes. One reviewer should be from the ML/backend side for infra/ML changes, and one from frontend for UI changes.
5. Ensure CI passes (unit tests, linters, type checks) before requesting final review.
6. Use squash-and-merge for feature PRs unless history must be preserved.

PR Checklist (add to each PR description)
• [ ] Jira ticket referenced
• [ ] Description & rationale provided
• [ ] Unit tests added or updated
• [ ] Linter and formatter run locally
• [ ] Security/secret checks performed (no secrets in PR)
• [ ] CI green

Commit messages
• Use Conventional Commits style (recommended):
  - feat(scope): short description
  - fix(scope): short description
  - docs: documentation only changes
  - chore: build/tooling changes
• Include the Jira ticket ID in commit messages when applicable.

Code style & linters
Backend (Python / FastAPI)
• Black for formatting: black .
• ruff for linting: ruff check .
• isort for imports: isort .
• Type checks (optional): mypy for typed modules.

Frontend (React + TypeScript)
• Prettier for formatting: npx prettier --write .
• ESLint for linting: npm run lint (configure rules in `.eslintrc`)

Testing
• Write unit tests for new features (pytest for backend, Jest/React Testing Library for frontend).
• Add simple integration tests for connector code (mock APIs).

Adding dependencies
• Backend: add dependency to `requirements.txt` or `pyproject.toml` and document why it's needed in the PR.
• Frontend: update `package.json` and lockfile. Keep versions pinned for reproducible builds.

Security & secrets
• Never commit secrets, credentials, or tokens. Use `.env` files ignored by git and document required env vars in `.env.example`.
• For production, use a secret manager (Azure Key Vault / Kubernetes secrets).

CI & observability
• All PRs must pass CI checks (tests, linters, type checks) before merge.
• Add monitoring & alerts for any new long-running services.

Getting help
• Open an issue for bugs or feature requests.
• Tag maintainers in PRs for urgent reviews.

Thank you for contributing — every contribution helps move the project forward!
