# Maquette Frontend

Minimal Vue 3 + TypeScript Vite project that reproduces the structure of the maquette found in `Divers/Maquette`.

Run locally:

```bash
cd Frontend
npm install
npm run dev
```

The app uses `src/data/maquette.json` (parsed from the original `Divers/Maquette/index.html`) to render pages and clickable areas. It does not depend on embedding the original images; overlays are positioned from the original coordinates.
