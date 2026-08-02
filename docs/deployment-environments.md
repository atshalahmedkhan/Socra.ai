# Deployment environments

| Environment | Data | Logs | Internal routes | CORS |
|---|---|---|---|---|
| development | fake/dev only | console allowed | opt-in with token | local origin |
| test | synthetic | captured | opt-in | test origin |
| staging | separate project | JSON | disabled | staging frontend |
| production | pilot data | JSON | disabled | exact HTTPS frontend |

Staging/production reject debug mode, wildcard CORS, enabled internal routes, missing database/service-role/JWT verification settings, and production missing model credentials. Research collection defaults off.
