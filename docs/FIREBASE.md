# Firebase

Account: `oineza@nd.edu`

## Status (2026-09-15)

| Step | Result |
| --- | --- |
| Google login | OK |
| GCP project `trading-model-oineza` | **Created** (under ND org `163520073994`) |
| `projects:addfirebase` via API/CLI | **403 PERMISSION_DENIED** (org policy / role) |
| `fir-demo-project` list access | Visible, but **no deploy rights** |
| Local config (`firebase.json`, rules) | Ready |

## What you must do in the browser

1. Open https://console.firebase.google.com/ as `oineza@nd.edu`
2. **Add project** → use existing GCP project **`trading-model-oineza`** (preferred)
3. Reply with the Firebase **Project ID**

Then we will: set active project → create Web app → deploy Hosting + Firestore → write `apps/web/firebase-config.json`.

## Local files

- `firebase.json` — Hosting (`apps/web`) + Firestore
- `firestore.rules` — `runs` collection demo rules
- `.firebaserc` — aliases `default` / `dedicated`
