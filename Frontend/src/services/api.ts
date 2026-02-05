import {
  mockDashboardStats,
  mockActivityData,
  mockValidationRateData,
  mockFluxData,
  mockNettoyageData
} from '../data/mockApiData'

// API base URL - change this when connecting to real backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// ============ Dashboard ============

export async function getDashboardStats() {
  // TODO: Replace with real API call:
  // const response = await fetch(`${API_BASE_URL}/dashboard/stats`)
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve(mockDashboardStats), 100)
  })
}

export async function getActivityData() {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/dashboard/activity`)
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve(mockActivityData), 100)
  })
}

export async function getValidationRateData() {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/dashboard/validation-rate`)
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve(mockValidationRateData), 100)
  })
}

// ============ Flux ============

export async function getFluxData() {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/flux/all`)
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve(mockFluxData), 100)
  })
}

export async function validerFlux(fluxId: string) {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/flux/${fluxId}/valider`, { method: 'POST' })
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve({ success: true, fluxId }), 100)
  })
}

export async function refuserFlux(fluxId: string) {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/flux/${fluxId}/refuser`, { method: 'POST' })
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve({ success: true, fluxId }), 100)
  })
}

// ============ Nettoyage ============

export async function getNettoyageData() {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/nettoyage/all`)
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve(mockNettoyageData), 100)
  })
}

export async function cleanItem(itemId: string) {
  // TODO: Replace with:
  // const response = await fetch(`${API_BASE_URL}/nettoyage/${itemId}/clean`, { method: 'POST' })
  // return response.json()
  
  return new Promise(resolve => {
    setTimeout(() => resolve({ success: true, itemId }), 100)
  })
}
