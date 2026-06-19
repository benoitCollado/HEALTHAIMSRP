# Maquette Frontend

Minimal Vue 3 + TypeScript Vite project that reproduces the structure of the maquette found in `Divers/Maquette`.

Run locally:

```bash
cd Frontend
npm install
npm run dev
```

Useful shortcuts:

```bash
npm run build
npm run cap:sync:android
npm run cap:open:android
```

For a full Android refresh after a frontend change, run:

```bash
npm run android:build
```

The app uses `src/data/maquette.json` (parsed from the original `Divers/Maquette/index.html`) to render pages and clickable areas. It does not depend on embedding the original images; overlays are positioned from the original coordinates.

## Daily calorie recommendation

`src/pages/PageAccueil.vue` shows a highlighted daily calorie estimate in `Informations personnelles`.

The estimate uses the user profile:

- age
- sex
- height and weight
- activity level
- selected goals

Formula:

```text
BMR = 10 * poids_kg + 6.25 * taille_cm - 5 * age + sex_adjustment
H = +5, F = -161, other = -78
```

Activity factors:

```text
1 = 1.2
2 = 1.375
3 = 1.55
4 = 1.725
5 = 1.9
```

Goal adjustment:

```text
perte_de_poids = -400 kcal
performance or force = +250 kcal
endurance = +150 kcal
otherwise = 0 kcal
```

The result is rounded to the nearest 50 kcal, with a minimum of `1200 kcal` for `F` and `1500 kcal` otherwise.
It is an indicative estimate, not medical advice.
