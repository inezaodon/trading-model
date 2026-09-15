# Firebase

Project ID (target): `trading-model-oineza`  
Account: `oineza@nd.edu`

## Services

| Service | Purpose |
| --- | --- |
| **Hosting** | Serve `apps/web` (Trading Model umbrella site) |
| **Cloud Firestore** | Persist simulation run history (`runs` collection) |
| **Web App** | Client SDK config for optional browser reads |

## Local files

- `firebase.json` — Hosting + Firestore
- `firestore.rules` — demo-open create/read on `runs`
- `firestore.indexes.json`
- `.firebaserc` — default project alias

## Blocker

Project creation failed until Google Cloud **Terms of Service** are accepted for this account:

1. Open https://console.cloud.google.com/  
2. Accept the Cloud Terms of Service if prompted  
3. Optionally also open https://console.firebase.google.com/ and accept Firebase terms  
4. Reply **Done** in chat so the agent can create the project, run `firebase_init`, create the web app, and deploy

## After init

```bash
# from repo root
npx firebase-tools deploy --only hosting,firestore
```

Hosting URL (after deploy): `https://trading-model-oineza.web.app`
