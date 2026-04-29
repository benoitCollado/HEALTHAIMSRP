/**
 * Service API pour l'interface d'administration.
 * Utilise les endpoints /admin/* du backend.
 */
import { API_BASE_URL } from '../config'
import { auth } from './auth'

function getHeaders(): HeadersInit {
  const token = auth.getToken()
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

export interface DashboardData {
  qualite_donnees: {
    score_pct: number
    total_anomalies: number
    objectifs_refuses: number
    consommations_invalides: number
    metriques_aberrantes: number
  }
  progression_utilisateurs: {
    total: number
    nouveaux_7j: number
    nouveaux_30j: number
  }
  tendances_nutrition: {
    total_consommations: number
    consommations_7j: number
    calories_moyennes: number
  }
  tendances_activite: {
    total_activites: number
    activites_7j: number
    duree_totale_minutes: number
  }
  objectifs: {
    valides: number
    encours: number
    refuses: number
    taux_validation_pct: number
  }
  kpis_business: {
    utilisateurs_actifs_30j: number
    donnees_sante_total: number
  }
}

export async function getDashboard(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE_URL}/admin/dashboard`, {
    method: 'GET',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/dashboard`)
  return res.json()
}

export interface FluxItem {
  id: string
  type: string
  nom: string
  description: string
  statut?: string
  dag_id?: string
  run_id?: string
  id_entite?: number
  stats?: { rows?: number; lastRun: string }
  errors?: string[]
  comment?: string
}

export interface FluxData {
  valides: FluxItem[]
  encours: FluxItem[]
  refuses: FluxItem[]
  flux_metadonnees: {
    consommations: { total: number; dernier_run: string | null }
    activites: { total: number; dernier_run: string | null }
    metriques: { total: number; dernier_run: string | null }
  }
  airflow_disponible?: boolean
}

export async function getFlux(): Promise<FluxData> {
  const res = await fetch(`${API_BASE_URL}/admin/flux`, {
    method: 'GET',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/flux`)
  return res.json()
}

// ============ CSV intermédiaires (visualisation, modification, validation) ============

export interface CsvIntermediaireMeta {
  filename: string
  type: string
  dag_id: string
  run_id?: string
  created_at: string
  status: 'pending' | 'validated' | 'rejected' | 'incorporated'
  rows: number
  target_date?: string
  csv_type: 'import' | 'export'
}

export interface FluxCsvListResponse {
  import: CsvIntermediaireMeta[]
  export: CsvIntermediaireMeta[]
}

export async function getFluxCsvList(type?: string, status?: string): Promise<FluxCsvListResponse> {
  const params = new URLSearchParams()
  if (type) params.set('type_csv', type)
  if (status) params.set('status', status)
  const url = `${API_BASE_URL}/admin/flux/csv${params.toString() ? '?' + params : ''}`
  const res = await fetch(url, { method: 'GET', headers: getHeaders() })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/flux/csv`)
  return res.json()
}

export interface FluxCsvContentResponse {
  content: string
  metadata: CsvIntermediaireMeta
}

export async function getFluxCsvContent(filename: string): Promise<FluxCsvContentResponse> {
  const res = await fetch(`${API_BASE_URL}/admin/flux/csv/${encodeURIComponent(filename)}`, {
    method: 'GET',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/flux/csv/${filename}`)
  return res.json()
}

export async function updateFluxCsv(filename: string, content: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/admin/flux/csv/${encodeURIComponent(filename)}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ content })
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur mise à jour CSV`)
  return res.json()
}

export async function validateFluxCsv(filename: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/admin/flux/csv/${encodeURIComponent(filename)}/validate`, {
    method: 'POST',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur validation CSV`)
  return res.json()
}

export async function rejectFluxCsv(filename: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/admin/flux/csv/${encodeURIComponent(filename)}/reject`, {
    method: 'POST',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur refus CSV`)
  return res.json()
}

export interface Anomalie {
  id: string
  type: string
  type_affichage: string
  id_entite: number
  entite_type: string
  description: string
  detail: string
}

export interface AnomaliesResponse {
  anomalies: Anomalie[]
  total: number
}

export async function getAnomalies(type?: string): Promise<AnomaliesResponse> {
  const url = type
    ? `${API_BASE_URL}/admin/anomalies?type_anomalie=${encodeURIComponent(type)}`
    : `${API_BASE_URL}/admin/anomalies`
  const res = await fetch(url, { method: 'GET', headers: getHeaders() })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/anomalies`)
  return res.json()
}

export async function validerAnomalie(anomalieId: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/admin/anomalies/${encodeURIComponent(anomalieId)}/valider`, {
    method: 'POST',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur valider anomalie`)
  return res.json()
}

export interface CorrectionBody {
  statut?: string
  quantite_g?: number
  calories_calculees?: number
  poids_kg?: number
  frequence_cardiaque?: number
  duree_sommeil_h?: number
}

export async function corrigerAnomalie(
  anomalieId: string,
  correction?: CorrectionBody
): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/admin/anomalies/${encodeURIComponent(anomalieId)}/corriger`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(correction || {})
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur corriger anomalie`)
  return res.json()
}

export async function exportDonneesNettoyees(typeDonnees: string = 'all'): Promise<Blob> {
  const url = `${API_BASE_URL}/admin/export?format_type=csv&type_donnees=${encodeURIComponent(typeDonnees)}`
  const res = await fetch(url, { method: 'GET', headers: getHeaders() })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur export`)
  return res.blob()
}

// ============ Utilisateurs ============

export interface UtilisateurAdmin {
  id_utilisateur: number
  username: string
  age: number
  sexe: string
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
  is_admin: boolean
  stats: {
    nb_consommations: number
    nb_activites: number
    nb_metriques: number
    nb_objectifs: number
  }
}

export interface UtilisateursResponse {
  utilisateurs: UtilisateurAdmin[]
  total: number
}

export interface UtilisateurCreatePayload {
  username: string
  password: string
  age: number
  sexe: string
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
}

export interface UtilisateurUpdatePayload {
  age?: number
  sexe?: string
  taille_cm?: number
  poids_kg?: number
  niveau_activite?: number
  type_abonnement?: number
  date_inscription?: string
}

export async function searchUtilisateurs(q?: string): Promise<UtilisateursResponse> {
  const url = q
    ? `${API_BASE_URL}/admin/utilisateurs?q=${encodeURIComponent(q)}`
    : `${API_BASE_URL}/admin/utilisateurs`
  const res = await fetch(url, { method: 'GET', headers: getHeaders() })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/utilisateurs`)
  return res.json()
}

export async function createUtilisateur(payload: UtilisateurCreatePayload): Promise<UtilisateurAdmin> {
  const res = await fetch(`${API_BASE_URL}/utilisateurs/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  })

  if (!res.ok) throw new Error(`Erreur ${res.status} sur création utilisateur`)
  return res.json()
}

export async function updateUtilisateur(id: number, payload: UtilisateurUpdatePayload): Promise<UtilisateurAdmin> {
  const res = await fetch(`${API_BASE_URL}/utilisateurs/${id}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  })

  if (!res.ok) throw new Error(`Erreur ${res.status} sur modification utilisateur`)
  return res.json()
}

export async function deleteUtilisateur(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/utilisateurs/${id}`, {
    method: 'DELETE',
    headers: getHeaders()
  })

  if (!res.ok) throw new Error(`Erreur ${res.status} sur suppression utilisateur`)
}

export interface UtilisateurDonnees {
  utilisateur: UtilisateurAdmin
  consommations: Array<{
    id_consommation: number
    date_consommation: string
    quantite_g: number
    calories_calculees: number
    id_aliment: number
  }>
  activites: Array<{
    id_activite: number
    date_activite: string
    duree_minutes: number
    calories_depensees: number
    id_exercice: number
  }>
  metriques: Array<{
    id_metrique: number
    date_mesure: string
    poids_kg: number | null
    frequence_cardiaque: number | null
    duree_sommeil_h: number | null
    calories_brulees: number | null
    pas: number | null
  }>
  objectifs: Array<{
    id_objectif: number
    type_objectif: string
    description: string
    date_debut: string
    date_fin: string
    statut: string
  }>
}

export async function getUtilisateurDonnees(id: number): Promise<UtilisateurDonnees> {
  const res = await fetch(`${API_BASE_URL}/admin/utilisateurs/${id}`, {
    method: 'GET',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error(`Erreur ${res.status} sur /admin/utilisateurs/${id}`)
  return res.json()
}
