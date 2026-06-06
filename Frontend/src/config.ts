/**
 * URL de base de l'API backend.
 * /api = proxy nginx de même origine, recommandé en déploiement.
 * VITE_API_URL peut cibler un backend externe si nécessaire.
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

/**
 * URL de l'interface Airflow (pour les liens "Voir dans Airflow").
 * Par défaut : http://localhost:8080
 */
export const AIRFLOW_UI_URL = import.meta.env.VITE_AIRFLOW_UI_URL || 'http://localhost:8080'
