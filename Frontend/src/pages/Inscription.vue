<template>
  <div class="register-page">
    <div class="register-bg"></div>

    <div class="register-container">
      <div class="register-brand">
        <div class="register-logo">❤️</div>
        <h1 class="register-title">HealthAI MSPR</h1>
        <p class="register-subtitle">Creer un compte utilisateur</p>
      </div>

      <div class="register-card">
        <h2 class="register-heading">Inscription</h2>
        <p class="register-hint">Remplissez vos informations pour creer un compte.</p>

        <form @submit.prevent="submit" class="register-form">
          <div class="field-grid">
            <label>
              <span>Nom d'utilisateur</span>
              <input v-model="form.username" type="text" required />
            </label>

            <label>
              <span>Mot de passe</span>
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" minlength="4" required />
            </label>

            <label>
              <span>Age</span>
              <input v-model.number="form.age" type="number" min="1" required />
            </label>

            <label>
              <span>Sexe</span>
              <select v-model="form.sexe" required>
                <option value="H">H</option>
                <option value="F">F</option>
              </select>
            </label>

            <label>
              <span>Taille (cm)</span>
              <input v-model.number="form.taille_cm" type="number" min="1" required />
            </label>

            <label>
              <span>Poids (kg)</span>
              <input v-model.number="form.poids_kg" type="number" min="1" required />
            </label>

            <label>
              <span>Niveau d'activite (1-5)</span>
              <input v-model.number="form.niveau_activite" type="number" min="1" max="5" required />
            </label>

            <label>
              <span>Type d'abonnement</span>
              <input v-model.number="form.type_abonnement" type="number" min="1" required />
            </label>

            <label class="full-width">
              <span>Date d'inscription</span>
              <input v-model="form.date_inscription" type="date" required />
            </label>
          </div>

          <div class="actions-row">
            <label class="checkbox-inline">
              <input v-model="showPassword" type="checkbox" />
              Afficher le mot de passe
            </label>
          </div>

          <div v-if="error" class="register-error">{{ error }}</div>
          <div v-if="success" class="register-success">{{ success }}</div>

          <button type="submit" class="register-btn" :disabled="isLoading">
            {{ isLoading ? 'Creation en cours...' : 'Creer mon compte' }}
          </button>

          <router-link to="/connexion" class="back-link">J'ai deja un compte</router-link>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'

interface RegisterPayload {
  username: string
  password: string
  age: number
  sexe: 'H' | 'F'
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
}

function initialForm(): RegisterPayload {
  return {
    username: '',
    password: '',
    age: 25,
    sexe: 'H',
    taille_cm: 170,
    poids_kg: 70,
    niveau_activite: 2,
    type_abonnement: 1,
    date_inscription: new Date().toISOString().slice(0, 10)
  }
}

export default defineComponent({
  setup() {
    const router = useRouter()
    const form = ref<RegisterPayload>(initialForm())
    const isLoading = ref(false)
    const error = ref('')
    const success = ref('')
    const showPassword = ref(false)

    async function submit() {
      error.value = ''
      success.value = ''
      isLoading.value = true

      try {
        const response = await fetch(`${API_BASE_URL}/utilisateurs/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form.value)
        })

        if (!response.ok) {
          let message = "Erreur lors de l'inscription"
          try {
            const err = await response.json()
            message = err?.detail || message
          } catch {
            // no-op
          }
          throw new Error(message)
        }

        success.value = 'Compte cree avec succes. Redirection vers la connexion...'
        form.value = initialForm()

        setTimeout(() => {
          router.push('/connexion')
        }, 1200)
      } catch (e) {
        error.value = e instanceof Error ? e.message : "Erreur lors de l'inscription"
      } finally {
        isLoading.value = false
      }
    }

    return { form, isLoading, error, success, showPassword, submit }
  }
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 24px;
}

.register-bg {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0f2044 0%, #1e3a5f 40%, #2563eb 100%);
  z-index: 0;
}

.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 740px;
}

.register-brand {
  text-align: center;
  color: #fff;
  margin-bottom: 16px;
}

.register-logo {
  font-size: 2.2rem;
}

.register-title {
  margin: 4px 0;
}

.register-subtitle {
  margin: 0;
  color: rgba(255,255,255,0.75);
}

.register-card {
  background: rgba(255,255,255,0.97);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 18px 48px rgba(0,0,0,0.25);
}

.register-heading {
  margin: 0;
  color: #0f172a;
}

.register-hint {
  margin: 8px 0 18px;
  color: #64748b;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.88rem;
  color: #334155;
}

.field-grid input,
.field-grid select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  background: #fff;
  color: #0f172a;
}

.full-width {
  grid-column: 1 / -1;
}

.actions-row {
  margin-top: 12px;
}

.checkbox-inline {
  font-size: 0.9rem;
  color: #334155;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.register-error {
  margin-top: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  padding: 10px 12px;
}

.register-success {
  margin-top: 12px;
  background: #dcfce7;
  color: #166534;
  border-radius: 8px;
  padding: 10px 12px;
}

.register-btn {
  width: 100%;
  margin-top: 14px;
  border: 0;
  border-radius: 10px;
  padding: 12px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  font-weight: 700;
  cursor: pointer;
}

.register-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.back-link {
  display: block;
  margin-top: 12px;
  text-align: center;
  color: #1d4ed8;
  text-decoration: none;
}

@media (max-width: 740px) {
  .field-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }
}
</style>
