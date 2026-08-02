## Summary

Describe what changed and why.

## Linked issue

Closes #

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Infrastructure
- [ ] Database migration
- [ ] Documentation
- [ ] Test
- [ ] Security

## Areas changed

- [ ] Frontend
- [ ] Backend
- [ ] Database
- [ ] Supabase
- [ ] Model infrastructure
- [ ] CI/CD
- [ ] Documentation

## Database impact

- [ ] No database changes
- [ ] Forward migration added
- [ ] RLS or policy changes
- [ ] Data migration required

Explain any migration ordering, rollback, or compatibility considerations:

## Environment-variable impact

List variable names only. Never include values, tokens, keys, or connection strings.

## Security and privacy impact

Describe authentication, authorization, RLS, secrets, student-data, and research-data considerations.

## Testing performed

| Command | Passed | Failed | Skipped | Exit code |
| --- | ---: | ---: | ---: | ---: |
|  |  |  |  |  |

Live verification result:

## Model verification

- Primary model tested:
- Fallback model tested:
- Endpoint type:
- Latency measured:
- Concurrency measured:
- Mocks used: yes / no

## Screenshots or evidence

Screenshots and evidence must not contain secrets, access tokens, database URLs,
student data, or research-participant data.

## Rollback plan

Describe the safe rollback or forward-fix procedure.

## Reviewer checklist

- [ ] No secrets were committed.
- [ ] No real student data was committed.
- [ ] CI passes.
- [ ] Migrations are forward-only.
- [ ] Authentication and RLS were not weakened.
- [ ] Live model claims are backed by real evidence.
- [ ] Fallback behavior was tested.
- [ ] Documentation matches the implementation.
