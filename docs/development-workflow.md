# Development workflow

## Branch names

The repository currently has one long-lived branch: protected `main`. Create
short-lived branches from the latest `main` using these patterns:

```text
feat/<ticket-or-scope>-<description>
fix/<ticket-or-scope>-<description>
chore/<description>
docs/<description>
research/<description>
```

Examples: `feat/phase1-live-model-integration`, `fix/message-idempotency`,
`chore/phase1-github-workflow`, `docs/model-deployment-guide`, and
`research/gemma-latency-benchmark`.

Do not document or branch from `development` unless that integration branch is
created intentionally and protected.

## Pull-request workflow

1. Never push directly to `main`.
2. Keep every branch and pull request focused on one reviewable scope.
3. Open a pull request and require at least one approval.
4. Require CI to pass and resolve every review conversation.
5. Do not approve or merge your own pull request.
6. Squash merge unless another documented repository policy applies.
7. Delete merged feature branches.

Never commit secrets, local environment files, access tokens, database URLs,
model weights, student data, or private research data.

## Issues and evidence

Use the structured bug or feature form and link implementation PRs to issues
where practical. Sanitize logs and screenshots. Pull requests must list exact
commands, exit codes, and passed/failed/skipped counts. Mock-based tests must be
identified as mocks; live model claims require real observed evidence.

## Local checks

```bash
cd apps/web
npm ci
npm run lint
npm run typecheck
npm run test
npm run build

cd ../../services/api
python -m pip install -r requirements-dev.txt
ruff check .
pytest
```
