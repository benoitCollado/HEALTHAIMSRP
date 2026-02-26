/**
 * URL de base de l'API backend.
 * Vide = même origine (nginx proxy) - fonctionne avec tunnel/accès distant.
 * Ou VITE_API_URL pour un backend externe (ex: http://localhost:8089)
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''
