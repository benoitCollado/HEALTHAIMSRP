/**
 * URL de base de l'API backend.
 * Vide = même origine (nginx proxy) - fonctionne avec tunnel/accès distant.
 * Ou VITE_API_URL pour un backend externe (ex: http://localhost:8089)
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * URL de l'interface Airflow (pour les liens "Voir dans Airflow").
 * Par défaut : http://localhost:8080
 */
export const AIRFLOW_UI_URL = import.meta.env.VITE_AIRFLOW_UI_URL || 'http://localhost:8080'
