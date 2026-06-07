<template>
  <main class="auth-page">
    <section class="auth-panel">
      <div class="brand-mark">H+</div>
      <h1>HealthAI MSPR</h1>
      <p class="brand-copy">Suivi santé intelligent</p>

      <form class="auth-card" @submit.prevent="submit">
        <div class="card-heading">
          <h2>Connexion</h2>
        </div>

        <div class="choice-panel">
          <div>
            <strong>Déjà inscrit ?</strong>
            <span>Connectez-vous avec votre mot de passe. Si la 2FA est activée, le code sera demandé ensuite.</span>
          </div>
          <router-link to="/inscription" class="choice-link">Créer un compte</router-link>
        </div>

        <label for="username">
          Nom d'utilisateur
          <input
            id="username"
            v-model.trim="username"
            :disabled="isLoading"
            type="text"
            autocomplete="username"
            placeholder="ex. admin"
            required
          />
        </label>

        <label for="password">
          Mot de passe
          <div class="password-row">
            <input
              id="password"
              v-model="password"
              :disabled="isLoading"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Votre mot de passe"
              required
            />
            <button type="button" class="icon-button" :disabled="isLoading" @click="showPassword = !showPassword">
              {{ showPassword ? 'Masquer' : 'Voir' }}
            </button>
          </div>
        </label>

        <label v-if="requiresTwoFactor" for="otp" class="twofa-step">
          Code Google Authenticator
          <input
            id="otp"
            v-model.trim="otp"
            :disabled="isLoading"
            type="text"
            inputmode="numeric"
            autocomplete="one-time-code"
            placeholder="Code à 6 chiffres"
            maxlength="6"
            required
          />
        </label>

        <p v-if="error" class="alert error">{{ error }}</p>
        <p v-else-if="requiresTwoFactor" class="alert info">
          Ouvrez Google Authenticator ou Authy, puis saisissez le code temporaire.
        </p>

        <button type="submit" class="primary-button" :disabled="isLoading">
          {{ submitLabel }}
        </button>

        <p class="auth-note">
          Nouveau sur HealthAI ? Créez un compte, puis activez la 2FA depuis votre espace sécurité.
        </p>
      </form>
    </section>
  </main>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../services/auth'

export default defineComponent({
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const otp = ref('')
    const error = ref('')
    const isLoading = ref(false)
    const showPassword = ref(false)
    const requiresTwoFactor = ref(false)
    const canSubmit = computed(() => username.value.trim().length > 0 && password.value.length > 0)
    const submitLabel = computed(() => {
      if (isLoading.value) return requiresTwoFactor.value ? 'Vérification...' : 'Connexion...'
      return requiresTwoFactor.value ? 'Valider le code 2FA' : 'Se connecter'
    })

    async function submit() {
      if (!canSubmit.value || isLoading.value) return

      error.value = ''
      isLoading.value = true

      try {
        const result = await auth.login(username.value, password.value, requiresTwoFactor.value ? otp.value : '')
        if (result.success) {
          await router.push('/page-accueil')
          return
        }

        if (result.error === 'Code 2FA requis') {
          requiresTwoFactor.value = true
          otp.value = ''
          return
        }

        error.value = result.error || 'Identifiants invalides.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      username,
      password,
      otp,
      error,
      isLoading,
      showPassword,
      requiresTwoFactor,
      submitLabel,
      submit
    }
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 34%),
    linear-gradient(135deg, #0f2044 0%, #1e3a5f 52%, #2563eb 100%);
}

.auth-panel {
  width: min(100%, 430px);
  color: #fff;
}

.brand-mark {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  margin: 0 auto 14px;
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.14);
  font-weight: 800;
  font-size: 1.25rem;
}

h1,
.brand-copy {
  text-align: center;
}

h1 {
  margin: 0;
  color: #fff;
  font-size: 1.8rem;
}

.brand-copy {
  margin: 6px 0 22px;
  color: rgba(255, 255, 255, 0.78);
}

.auth-card {
  display: grid;
  gap: 16px;
  padding: 28px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.28);
  color: #0f172a;
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.card-heading h2 {
  margin: 0;
  font-size: 1.35rem;
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

.choice-panel span,
.auth-note {
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

label {
  display: grid;
  gap: 7px;
  margin: 0;
}

.password-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.icon-button {
  min-width: 76px;
  justify-content: center;
  padding-inline: 12px;
  background: #e2e8f0;
  color: #334155;
  box-shadow: none;
}

.icon-button:hover:not(:disabled) {
  background: #cbd5e1;
  box-shadow: none;
}

.primary-button {
  justify-content: center;
  min-height: 44px;
  margin-top: 4px;
}

.alert {
  margin: 0;
  padding: 11px 13px;
  border-radius: 8px;
  font-size: 0.9rem;
}

.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.info {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.twofa-step input {
  font-weight: 700;
  letter-spacing: 0.16em;
  text-align: center;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 22px;
  }

  .card-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .password-row {
    grid-template-columns: 1fr;
  }

  .choice-panel {
    grid-template-columns: 1fr;
  }
}
</style>
