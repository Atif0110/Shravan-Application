# SHRAVAN Web Client

Vue 3 client for the SHRAVAN health platform.

## Setup

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
npm run preview
```

Set `VITE_BACKEND_URL` in `.env` when the API is not running at `http://localhost:5000`.

Authentication uses the backend session cookie. State-changing requests receive a CSRF token through `src/api.js` and send it in `X-CSRF-Token`.
