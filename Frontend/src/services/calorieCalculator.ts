export interface CalorieProfile {
  age: number
  sexe: string
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  perte_de_poids: boolean
  performance: boolean
  endurance: boolean
  force: boolean
}

export interface EstimatedCalories {
  calories: number
  detail: string
}

const ACTIVITY_FACTORS: Record<number, number> = {
  1: 1.2,
  2: 1.375,
  3: 1.55,
  4: 1.725,
  5: 1.9
}

export function estimateBasalMetabolism(profile: Pick<CalorieProfile, 'age' | 'sexe' | 'taille_cm' | 'poids_kg'>): number {
  const sexAdjustment = profile.sexe === 'F' ? -161 : profile.sexe === 'H' ? 5 : -78
  return (10 * profile.poids_kg) + (6.25 * profile.taille_cm) - (5 * profile.age) + sexAdjustment
}

export function estimateDailyCalories(profile: CalorieProfile | null): EstimatedCalories | null {
  if (!profile?.age || !profile.taille_cm || !profile.poids_kg) {
    return null
  }

  const basalMetabolism = estimateBasalMetabolism(profile)
  const maintenanceCalories = basalMetabolism * (ACTIVITY_FACTORS[profile.niveau_activite] ?? ACTIVITY_FACTORS[1])
  let goalAdjustment = 0
  let goalDetail = 'maintien du poids'

  if (profile.perte_de_poids) {
    goalAdjustment = -400
    goalDetail = 'objectif perte de poids'
  } else if (profile.performance || profile.force) {
    goalAdjustment = 250
    goalDetail = 'objectif performance ou force'
  } else if (profile.endurance) {
    goalAdjustment = 150
    goalDetail = 'objectif endurance'
  }

  const minimumCalories = profile.sexe === 'F' ? 1200 : 1500
  const calories = Math.max(minimumCalories, Math.round((maintenanceCalories + goalAdjustment) / 50) * 50)

  return {
    calories,
    detail: `Estimation basee sur le profil, l'activite et ${goalDetail}.`
  }
}
