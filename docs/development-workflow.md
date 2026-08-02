# Development workflow

## Branch names

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

Use the structured bug or feature form. Link implementation pull requests to an
issue where practical. Sanitize logs and screenshots before attaching them.

## Verification evidence

Pull requests must list exact commands, exit codes, and passed/failed/skipped
counts. Mock-based tests must be identified as mocks. Claims about live model,
database, authentication, or end-to-end behavior require observed live evidence.
