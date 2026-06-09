<template>
  <main class="auth-page">
    <section class="auth-shell" aria-labelledby="login-title">
      <div class="brand-strip">
        <img class="brand-icon" :src="healthAiIcon" alt="" aria-hidden="true" />
        <div>
          <p class="brand-kicker">HealthAI MSPR</p>
          <h1>Suivi sante intelligent</h1>
        </div>
      </div>

      <form class="auth-card" @submit.prevent="submit">
        <div class="card-heading">
          <div>
            <p class="eyebrow">Espace securise</p>
            <h2 id="login-title">Connexion</h2>
          </div>
        </div>

        <div class="helper-panel">
          <strong>Deja inscrit ?</strong>
          <span>Connectez-vous avec votre mot de passe. Si la 2FA est activee, le code sera demande ensuite.</span>
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
            <button type="button" class="secondary-button" :disabled="isLoading" @click="showPassword = !showPassword">
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
            placeholder="Code a 6 chiffres"
            maxlength="6"
            required
          />
        </label>

        <p v-if="error" class="auth-alert error">{{ error }}</p>
        <p v-else-if="requiresTwoFactor" class="auth-alert info">
          Ouvrez Google Authenticator ou Authy, puis saisissez le code temporaire.
        </p>

        <button type="submit" class="primary-button" :disabled="isLoading">
          {{ submitLabel }}
        </button>

        <div class="create-account-panel">
          <span>Nouveau sur HealthAI ?</span>
          <router-link to="/inscription" class="choice-link">Creer un compte</router-link>
        </div>
      </form>
    </section>
  </main>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import healthAiIcon from '../assets/healthai_icon.svg'
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
      if (isLoading.value) return requiresTwoFactor.value ? 'Verification...' : 'Connexion...'
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
      healthAiIcon,
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
  display: grid;
  min-height: 100vh;
  min-height: 100dvh;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 18% 0%, rgba(20, 184, 166, 0.16), transparent 34%),
    radial-gradient(circle at 86% 10%, rgba(37, 99, 235, 0.18), transparent 32%),
    linear-gradient(135deg, #071226 0%, #24364f 54%, #2563eb 100%);
}

.auth-shell {
  width: min(100%, 460px);
  min-width: 0;
}

.brand-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-bottom: 18px;
  color: #fff;
}

.brand-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.32);
}

.brand-strip h1,
.brand-strip p {
  margin: 0;
}

.brand-strip h1 {
  color: #fff;
  font-size: 1.28rem;
}

.brand-kicker {
  color: rgba(255, 255, 255, 0.70);
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

.auth-card {
  display: grid;
  gap: 18px;
  width: 100%;
  min-width: 0;
  padding: 28px;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(226, 232, 240, 0.88);
  border-radius: 8px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.28);
}

.card-heading {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 14px;
}

.card-heading h2,
.eyebrow {
  margin: 0;
}

.card-heading h2 {
  color: #0f172a;
  font-size: 1.55rem;
}

.eyebrow {
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}

.auth-badge {
  flex: 0 0 auto;
  padding: 5px 9px;
  color: #0369a1;
  font-size: 0.72rem;
  font-weight: 800;
  background: #ecfeff;
  border-radius: 999px;
}

.helper-panel,
.create-account-panel {
  padding: 14px;
  background: #f8fbff;
  border: 1px solid #dbeafe;
  border-radius: 8px;
}

.helper-panel {
  display: grid;
  gap: 5px;
}

.helper-panel strong {
  color: #1e3a8a;
}

.helper-panel span,
.create-account-panel span {
  color: #64748b;
  font-size: 0.9rem;
}

label {
  display: grid;
  gap: 7px;
  margin: 0;
  color: #334155;
  font-weight: 700;
  min-width: 0;
}

.password-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 96px;
  gap: 10px;
  min-width: 0;
}

.password-row input {
  min-width: 0;
}

.secondary-button {
  justify-content: center;
  min-height: 48px;
  padding-inline: 12px;
  color: #334155;
  background: #e2e8f0;
  box-shadow: none;
}

.secondary-button:hover:not(:disabled) {
  background: #cbd5e1;
  box-shadow: none;
}

.primary-button {
  justify-content: center;
  min-height: 52px;
  font-size: 1rem;
  width: 100%;
  white-space: normal;
}

.create-account-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.choice-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 9px 14px;
  color: #fff;
  font-weight: 800;
  text-align: center;
  white-space: nowrap;
  background: #2563eb;
  border-radius: 8px;
}

.choice-link:hover {
  background: #1d4ed8;
  text-decoration: none;
}

.auth-alert {
  margin: 0;
  padding: 11px 13px;
  font-size: 0.9rem;
  border-radius: 8px;
}

.error {
  color: #991b1b;
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.info {
  color: #1e40af;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.twofa-step input {
  font-weight: 800;
  text-align: center;
  letter-spacing: 0.16em;
}

@media (max-width: 640px) {
  .auth-page {
    align-items: start;
    padding: 16px;
  }

  .auth-shell {
    width: 100%;
  }

  .brand-strip {
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 14px;
  }

  .brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
  }

  .brand-strip h1 {
    font-size: 1.05rem;
  }

  .auth-card {
    gap: 14px;
    padding: 18px;
  }

  .card-heading,
  .create-account-panel {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .card-heading h2 {
    font-size: 1.35rem;
  }

  .helper-panel,
  .create-account-panel {
    padding: 12px;
  }

  .password-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .choice-link,
  .secondary-button {
    width: 100%;
  }

  .secondary-button,
  .primary-button,
  .choice-link {
    min-height: 46px;
  }
}

@media (max-width: 360px) {
  .auth-page {
    padding: 10px;
  }

  .auth-card {
    padding: 14px;
  }

  .brand-strip {
    gap: 10px;
  }

  .helper-panel span,
  .create-account-panel span {
    font-size: 0.84rem;
  }
}
</style>
