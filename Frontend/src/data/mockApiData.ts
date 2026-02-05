// Mock API data that will be replaced by FastAPI calls
export const mockDashboardStats = {
  valides: 124,
  enCours: 32,
  refuses: 8
}

export const mockActivityData = [12, 20, 8, 16, 24, 18, 22]

export const mockValidationRateData = [40, 50, 55, 60, 58, 64, 70]

export const mockFluxData = {
  valides: [
    { id: 'F-101', nom: 'Flux A' },
    { id: 'F-102', nom: 'Flux B' }
  ],
  encours: [
    { id: 'F-201', nom: 'Flux C' },
    { id: 'F-202', nom: 'Flux D' }
  ],
  refuses: [
    { id: 'F-301', nom: 'Flux X' }
  ]
}

export const mockNettoyageData = [
  { id: 'N-1', type: 'Incohérence date' },
  { id: 'N-2', type: 'Doublon' },
  { id: 'N-3', type: 'Manque info' }
]
