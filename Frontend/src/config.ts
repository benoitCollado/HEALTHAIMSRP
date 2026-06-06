/**
 * URL complète de l'API (VITE_API_URL dans .env / .env.example à la racine du repo).
 * Ex. https://healthai.mondomaine.com/api
 */
const rawApiUrl = import.meta.env.VITE_API_URL ?? '/api'
export const API_BASE_URL = rawApiUrl.replace(/\/$/, '')

/**
 * URL de l'interface Airflow (pour les liens "Voir dans Airflow").
 * Par défaut : http://localhost:8080
 */
export const AIRFLOW_UI_URL = import.meta.env.VITE_AIRFLOW_UI_URL || 'http://localhost:8080'
