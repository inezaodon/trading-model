# Firebase — Trading Model

| Field | Value |
| --- | --- |
| Display name | `trading-model-oineza` |
| **Firebase Project ID** | `trading-model-oineza-8280d` |
| Related GCP project | `trading-model-oineza` |
| Account | `oineza@nd.edu` |
| Web App | Trading Model Web |
| Web App ID | `1:245835915410:web:23054acf0a1a051b96c64b` |

## Live URLs

- **Hosting:** https://trading-model-oineza-8280d.web.app  
- **Console:** https://console.firebase.google.com/project/trading-model-oineza-8280d/overview  
- Auth domain: `trading-model-oineza-8280d.firebaseapp.com`

## Services enabled

| Service | Status |
| --- | --- |
| Hosting | Deployed (`apps/web`) |
| Cloud Firestore | Created `(default)` + rules deployed |
| Web App + SDK config | `apps/web/firebase-config.json` |

## Client config

See `apps/web/firebase-config.json` (also exposed via API `GET /api/v1/runs` → `firebase_web_config` when present).

## Redeploy

```bash
cd /agent/trading-model-merge   # or repo root
npx firebase-tools deploy --only hosting,firestore --project trading-model-oineza-8280d
```
