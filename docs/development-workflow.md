# Development workflow

## Branch names

<<<<<<< HEAD
Create focused branches using one of these patterns:

- `feat/<ticket-or-scope>-<description>`
- `fix/<ticket-or-scope>-<description>`
- `chore/<description>`
- `docs/<description>`
- `research/<description>`

Examples include `feat/phase1-live-model-integration`,
`fix/message-idempotency`, `chore/phase1-github-workflow`,
`docs/model-deployment-guide`, and `research/gemma-latency-benchmark`.

## Pull-request workflow

1. Branch from the protected integration branch, normally `main`.
2. Never push directly to `main`.
3. Keep every branch and pull request focused on one reviewable scope.
4. Open a pull request and require at least one approval.
5. Require CI to pass and resolve every review conversation.
6. Do not approve or merge your own pull request.
7. Squash merge unless another documented repository policy applies.
8. Delete merged feature branches.

Do not commit secrets, local environment files, access tokens, database URLs,
student data, or private research data. Document environment-variable names and
placeholder values only.

## Issue workflow
=======
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
>>>>>>> origin/main

Use the structured bug or feature form. Link implementation pull requests to an
issue where practical. Sanitize logs and screenshots before attaching them.

<<<<<<< HEAD
## Verification evidence

Pull requests must list exact commands, exit codes, and passed/failed/skipped
counts. Mock-based tests must be identified as mocks. Claims about live model,
database, authentication, or end-to-end behavior require observed live evidence.
=======
1. Never push directly to `main`.
2. Keep every branch and pull request focused.
3. Open a pull request and require at least one approval.
4. Require CI to pass and resolve every review conversation.
5. Do not approve or merge your own pull request.
6. Squash merge unless another documented repository policy exists.
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
>>>>>>> origin/main
