<template>
  <div class="login-page">
    <div class="login-bg"></div>

    <div class="login-container">
      <!-- Brand -->
      <div class="login-brand">
        <div class="login-logo">❤️</div>
        <h1 class="login-title">HealthAI MSPR</h1>
        <p class="login-subtitle">Suivi santé intelligent</p>
      </div>

      <!-- Card -->
      <div class="login-card">
        <h2 class="login-heading">Connexion</h2>
        <p class="login-hint">Entrez vos identifiants pour accéder à votre espace</p>

        <form @submit.prevent="submit" class="login-form">
          <div class="form-group">
            <label for="username">Nom d'utilisateur</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input
                id="username"
                v-model="username"
                :disabled="isLoading"
                type="text"
                placeholder="Votre identifiant"
                autocomplete="username"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">Mot de passe</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                id="password"
                v-model="password"
                :disabled="isLoading"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Votre mot de passe"
                autocomplete="current-password"
                required
              />
              <button type="button" class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <div v-if="error" class="login-error">
            <span>⚠️</span> {{ error }}
          </div>

          <button type="submit" :disabled="isLoading" class="login-btn">
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Connexion en cours...' : 'Se connecter' }}
          </button>
        </form>
      </div>

      <p class="login-footer-note">© {{ year }} EPSI · HealthAI MSPR v1.0</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../services/auth'

export default defineComponent({
  setup() {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const isLoading = ref(false)
    const showPassword = ref(false)
    const router = useRouter()
    const year = computed(() => new Date().getFullYear())

    async function submit() {
      error.value = ''
      isLoading.value = true
      const result = await auth.login(username.value, password.value)

      if (result.success) {
        router.push('/page-accueil')
      } else {
        error.value = result.error || 'Erreur de connexion'
      }

      isLoading.value = false
    }

    return { username, password, error, isLoading, showPassword, year, submit }
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 24px;
  overflow: hidden;
}

.login-bg {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0f2044 0%, #1e3a5f 40%, #2563eb 100%);
  z-index: 0;
}

.login-bg::before,
.login-bg::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
}
.login-bg::before {
  width: 600px; height: 600px;
  top: -200px; right: -150px;
}
.login-bg::after {
  width: 400px; height: 400px;
  bottom: -100px; left: -100px;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.login-brand { text-align: center; color: #fff; }
.login-logo  { font-size: 2.5rem; margin-bottom: 8px; }
.login-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 4px;
  letter-spacing: -0.5px;
}
.login-subtitle { font-size: 0.9rem; color: rgba(255,255,255,0.6); margin: 0; }

.login-card {
  width: 100%;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.30), 0 4px 12px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
}

.login-heading {
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
}
.login-hint { font-size: 0.85rem; color: #64748b; margin: 0 0 24px; }

.login-form { display: flex; flex-direction: column; }

.form-group { margin-bottom: 18px; }
.form-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
  display: block;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 0.9rem;
  pointer-events: none;
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 11px 44px 11px 38px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #0f172a;
  background: #f8fafc;
  transition: border-color 0.18s, box-shadow 0.18s, background 0.18s;
  outline: none;
}
.input-wrapper input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
  background: #fff;
}
.input-wrapper input:disabled { opacity: 0.6; cursor: not-allowed; }

.toggle-pw {
  position: absolute;
  right: 10px;
  background: none !important;
  border: none !important;
  padding: 4px 6px !important;
  cursor: pointer;
  font-size: 0.85rem;
  box-shadow: none !important;
  transform: none !important;
  color: #94a3b8;
}
.toggle-pw:hover { background: none !important; transform: none !important; }

.login-error {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 14px;
  background: #fef2f2;
  color: #991b1b;
  border-radius: 8px;
  border-left: 3px solid #dc2626;
  font-size: 0.87rem;
  margin-bottom: 16px;
}

.login-btn {
  width: 100%;
  justify-content: center;
  padding: 13px;
  font-size: 0.98rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.18s;
  letter-spacing: 0.2px;
  box-shadow: 0 4px 14px rgba(37,99,235,0.30);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37,99,235,0.40);
}
.login-btn:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.login-footer-note {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.4);
  text-align: center;
  margin: 0;
}
</style>
