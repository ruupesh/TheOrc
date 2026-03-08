# Frontend Setup

This guide covers local setup for the Next.js frontend.

## 1. Prerequisites

Install the following first:

- Node.js 20 or newer
- npm
- The backend API running on `http://localhost:8000`

Backend setup is documented in [BACKEND_SETUP.md](d:/projects/TheOrchestrator/backend_service/ProjectSetup/BACKEND_SETUP.md).

## 2. Install Dependencies

From [frontend](d:/projects/TheOrchestrator/frontend):

```powershell
npm install
```

## 3. Configure Environment Variables

Create or update `.env.local` in [frontend](d:/projects/TheOrchestrator/frontend):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

This is the base URL used by the UI for all backend API calls.

## 4. Start the Development Server

From [frontend](d:/projects/TheOrchestrator/frontend):

```powershell
npm run dev
```

The UI starts on:

```text
http://localhost:3000
```

## 5. Build for Production Validation

To confirm the UI builds successfully:

```powershell
npm run build
```

To run the production server locally after a successful build:

```powershell
npm run start
```

## 6. What to Verify in the UI

After both frontend and backend are running:

1. Open `http://localhost:3000`.
2. Register a new user or log in with an existing user.
3. Open the Agents page and confirm your agents load.
4. Open the MCP Tools page and confirm tools load.
5. Open Marketplace and confirm public listings are visible.
6. Open Chat and send a test request.

## 7. Troubleshooting

### Frontend cannot reach the backend

- Confirm the backend is running on `localhost:8000`.
- Confirm `.env.local` contains the correct `NEXT_PUBLIC_API_URL`.
- Restart `npm run dev` after editing `.env.local`.

### UI loads but chat or marketplace is empty

- Confirm the backend database has been initialized with `python -m scripts.init_db`.
- Confirm marketplace demo scripts were run if you expect sample marketplace data.
- Confirm the remote agents are running if you expect orchestrated chat to use them.

### Port `3000` is already in use

Run on another port:

```powershell
npx next dev --port 3001
```

If you do this, open `http://localhost:3001` in the browser.