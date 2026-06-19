import { describe, expect, it } from 'vitest'
import { estimateBasalMetabolism, estimateDailyCalories, type CalorieProfile } from './calorieCalculator'

const baseProfile: CalorieProfile = {
  age: 30,
  sexe: 'H',
  taille_cm: 180,
  poids_kg: 75,
  niveau_activite: 3,
  perte_de_poids: false,
  performance: false,
  endurance: false,
  force: false
}

describe('calorieCalculator', () => {
  it('calcule le metabolisme de base Mifflin-St Jeor comme le calculateur du metabolisme', () => {
    expect(estimateBasalMetabolism(baseProfile)).toBe(1730)
    expect(estimateBasalMetabolism({ ...baseProfile, sexe: 'F' })).toBe(1564)
  })

  it('applique le facteur activite et arrondit la recommandation au multiple de 50 kcal', () => {
    expect(estimateDailyCalories(baseProfile)).toEqual({
      calories: 2700,
      detail: "Estimation basee sur le profil, l'activite et maintien du poids."
    })
  })

  it('ajuste les calories selon les objectifs utilisateur', () => {
    expect(estimateDailyCalories({ ...baseProfile, perte_de_poids: true })?.calories).toBe(2300)
    expect(estimateDailyCalories({ ...baseProfile, performance: true })?.calories).toBe(2950)
    expect(estimateDailyCalories({ ...baseProfile, force: true })?.calories).toBe(2950)
    expect(estimateDailyCalories({ ...baseProfile, endurance: true })?.calories).toBe(2850)
  })

  it('retourne null si le profil est incomplet et protege les minima caloriques', () => {
    expect(estimateDailyCalories(null)).toBeNull()
    expect(estimateDailyCalories({ ...baseProfile, poids_kg: 0 })).toBeNull()
    expect(estimateDailyCalories({ ...baseProfile, sexe: 'F', age: 90, taille_cm: 140, poids_kg: 35, perte_de_poids: true })?.calories).toBe(1200)
  })
})
