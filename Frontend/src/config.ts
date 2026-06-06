/**
 * URL de base de l'API backend.
 * /api = proxy nginx de meme origine, recommande en deploiement.
 * VITE_API_URL peut cibler un backend externe si necessaire.
 */
const rawApiUrl = import.meta.env.VITE_API_URL || '/api'
export const API_BASE_URL = rawApiUrl.replace(/\/$/, '') || '/api'

/**
 * URL de l'interface Airflow (pour les liens "Voir dans Airflow").
 * Par defaut : http://localhost:8080
 */
export const AIRFLOW_UI_URL = import.meta.env.VITE_AIRFLOW_UI_URL || 'http://localhost:8080'
