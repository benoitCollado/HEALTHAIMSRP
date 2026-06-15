<template>
  <main class="register-page">
    <section class="register-shell">
      <div class="register-head">
        <div class="brand-mark">H+</div>
        <div>
          <h1>Créer un compte</h1>
          <p>Créez votre compte, puis activez la 2FA depuis votre espace sécurité.</p>
        </div>
      </div>

      <form class="register-card" @submit.prevent="submit">
        <div class="choice-panel">
          <div>
            <strong>Nouveau compte</strong>
            <span>La 2FA reste désactivée par défaut. Vous pourrez l'activer juste après la première connexion.</span>
          </div>
          <router-link to="/connexion" class="choice-link">Se connecter</router-link>
        </div>

        <div class="form-section">
          <h2>Identifiants</h2>
          <div class="grid two">
            <label for="username">
              Nom d'utilisateur
              <input id="username" v-model.trim="form.username" type="text" autocomplete="username" required />
            </label>

            <label for="email">
              Adresse mail
              <input id="email" v-model.trim="form.email" type="email" autocomplete="email" required />
            </label>

            <label for="password">
              Mot de passe
              <div class="password-row">
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  minlength="4"
                  required
                />
                <button type="button" class="secondary-button" @click="showPassword = !showPassword">
                  {{ showPassword ? 'Masquer' : 'Voir' }}
                </button>
              </div>
            </label>
          </div>
        </div>

        <div class="form-section">
          <h2>Profil santé</h2>
          <div class="grid three">
            <label for="age">
              Age
              <input id="age" v-model.number="form.age" type="number" min="1" max="120" required />
            </label>

            <label for="sexe">
              Sexe
              <select id="sexe" v-model="form.sexe" required>
                <option value="H">Homme</option>
                <option value="F">Femme</option>
              </select>
            </label>

            <label for="niveau">
              Activité
              <select id="niveau" v-model.number="form.niveau_activite" required>
                <option :value="1">Très faible</option>
                <option :value="2">Faible</option>
                <option :value="3">Modérée</option>
                <option :value="4">Élevée</option>
                <option :value="5">Très élevée</option>
              </select>
            </label>

            <label for="taille">
              Taille en cm
              <input id="taille" v-model.number="form.taille_cm" type="number" min="80" max="240" required />
            </label>

            <label for="poids">
              Poids en kg
              <input id="poids" v-model.number="form.poids_kg" type="number" min="20" max="300" required />
            </label>

            <label for="abonnement">
              Abonnement
              <select id="abonnement" v-model.number="form.type_abonnement" required>
                <option :value="1">Standard</option>
                <option :value="2">Premium</option>
              </select>
            </label>
          </div>
        </div>

        <p v-if="error" class="alert error">{{ error }}</p>
        <p v-if="success" class="alert success">{{ success }}</p>

        <div class="actions">
          <label class="twofa-choice">
            <input v-model="goToSecurityAfterRegister" type="checkbox" />
            Me connecter après création pour configurer la 2FA
          </label>
          <button type="submit" class="primary-button" :disabled="isLoading">
            {{ isLoading ? 'Création...' : 'Créer le compte' }}
          </button>
        </div>
      </form>
    </section>
  </main>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config'
import { auth } from '../services/auth'

interface RegisterPayload {
  username: string
  email: string
  password: string
  age: number
  sexe: 'H' | 'F'
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
}

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function initialForm(): RegisterPayload {
  return {
    username: '',
    email: '',
    password: '',
    age: 25,
    sexe: 'H',
    taille_cm: 170,
    poids_kg: 70,
    niveau_activite: 3,
    type_abonnement: 1,
    date_inscription: todayIsoDate()
  }
}

export default defineComponent({
  setup() {
    const router = useRouter()
    const form = ref<RegisterPayload>(initialForm())
    const isLoading = ref(false)
    const showPassword = ref(false)
    const goToSecurityAfterRegister = ref(true)
    const error = ref('')
    const success = ref('')

    async function submit() {
      if (isLoading.value) return

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
          let message = "Impossible de créer le compte."
          try {
            const data = await response.json()
            message = data?.detail || message
          } catch {
            // keep fallback message
          }
          throw new Error(message)
        }

        success.value = goToSecurityAfterRegister.value
          ? 'Compte créé. Connexion automatique...'
          : 'Compte créé. Redirection vers la connexion...'

        const credentials = {
          username: form.value.username,
          password: form.value.password
        }
        form.value = initialForm()

        if (goToSecurityAfterRegister.value) {
          const login = await auth.login(credentials.username, credentials.password)
          if (login.success) {
            window.setTimeout(() => router.push('/page-accueil'), 500)
          } else {
            success.value = 'Compte créé. Connectez-vous pour configurer la 2FA.'
            window.setTimeout(() => router.push('/connexion'), 900)
          }
        } else {
          window.setTimeout(() => router.push('/connexion'), 900)
        }
      } catch (err) {
        error.value = err instanceof Error ? err.message : "Impossible de créer le compte."
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      isLoading,
      showPassword,
      goToSecurityAfterRegister,
      error,
      success,
      submit
    }
  }
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 18% 0%, rgba(22, 163, 74, 0.14), transparent 32%),
    linear-gradient(135deg, #0f2044 0%, #1e3a5f 54%, #2563eb 100%);
}

.register-shell {
  width: min(100%, 820px);
  min-width: 0;
}

.register-head {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  color: #fff;
}

.brand-mark {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.36);
  background: rgba(255, 255, 255, 0.14);
  font-weight: 800;
  font-size: 1.25rem;
  flex: 0 0 auto;
}

h1,
h2,
p {
  margin: 0;
}

.register-head h1 {
  color: #fff;
  font-size: 1.7rem;
}

.register-head p {
  color: rgba(255, 255, 255, 0.78);
  margin-top: 4px;
}

.register-card {
  display: grid;
  gap: 22px;
  width: 100%;
  min-width: 0;
  padding: 28px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.28);
}

.choice-panel {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  background: #eff6ff;
}

.choice-panel div {
  display: grid;
  gap: 2px;
}

.choice-panel strong {
  color: #1e3a8a;
  font-size: 0.92rem;
}

.choice-panel span {
  color: #64748b;
  font-size: 0.84rem;
}

.choice-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 7px 12px;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 700;
  white-space: nowrap;
}

.choice-link:hover {
  background: #1d4ed8;
  text-decoration: none;
}

.form-section {
  display: grid;
  gap: 14px;
}

.form-section h2 {
  font-size: 1.05rem;
  color: #0f172a;
}

.grid {
  display: grid;
  gap: 14px;
}

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

label {
  display: grid;
  gap: 7px;
  margin: 0;
}

.password-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  min-width: 0;
}

.secondary-button {
  min-width: 76px;
  justify-content: center;
  padding-inline: 12px;
  background: #e2e8f0;
  color: #334155;
  box-shadow: none;
}

.secondary-button:hover:not(:disabled) {
  background: #cbd5e1;
  box-shadow: none;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.twofa-choice {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #334155;
  font-size: 0.9rem;
}

.twofa-choice input {
  width: auto;
}

.primary-button {
  min-width: 180px;
  justify-content: center;
}

.alert {
  padding: 11px 13px;
  border-radius: 8px;
  font-size: 0.9rem;
}

.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

@media (max-width: 760px) {
  .register-page {
    align-items: start;
    padding: 16px;
  }

  .register-head {
    align-items: flex-start;
  }

  .grid.two,
  .grid.three {
    grid-template-columns: 1fr;
  }

  .actions {
    align-items: stretch;
    flex-direction: column-reverse;
  }

  .choice-panel {
    grid-template-columns: 1fr;
  }

  .choice-link,
  .secondary-button {
    width: 100%;
    justify-content: center;
  }

  .primary-button {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 460px) {
  .register-card {
    padding: 22px;
  }

  .password-row {
    grid-template-columns: 1fr;
  }
}
</style>
