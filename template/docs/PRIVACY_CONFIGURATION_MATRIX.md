# Reponomics Privacy Configuration Matrix

> [!WARNING]
> Pre-release placeholder matrix; details may change before `v1`.

Repository visibility and Reponomics privacy mode are separate. Repository visibility controls repository access. `privacy-mode` controls storage and publication handling.

| Mode | Repository visibility | Retained artifact | Hosted Pages dashboard | Downloadable dashboard artifact | Secret policy |
| --- | --- | --- | --- | --- | --- |
| `strong` | public or private | encrypted `dashboard-data.enc` | optional encrypted deployment | encrypted artifact when hosted publication is disabled | high-entropy `DASHBOARD_SECRET_DO_NOT_REPLACE` |
| `casual` | public or private | encrypted `dashboard-data.enc` | optional encrypted deployment | encrypted artifact when hosted publication is disabled | any non-empty `DASHBOARD_SECRET_DO_NOT_REPLACE` |
| `plain` | private only | plaintext retained CSV files | disabled | plaintext artifact | no dashboard secret |

`plain` mode is rejected in public repositories.
