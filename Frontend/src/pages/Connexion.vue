<template>
  <div class="canvas" style="padding:24px;display:flex;align-items:center;justify-content:center;min-height:100vh">
    <div style="width:360px;background:#fff;padding:24px;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.2)">
      <h2 style="margin:0 0 12px">Connexion</h2>
      <p style="font-size:12px;color:#666;margin:0 0 16px">Connecte-toi avec un compte existant de la base de données</p>
      <form @submit.prevent="submit">
        <div style="margin-bottom:12px">
          <label>Nom d'utilisateur</label>
          <input v-model="username" :disabled="isLoading" type="text" required style="width:100%;padding:8px;margin-top:6px;box-sizing:border-box" />
        </div>
        <div style="margin-bottom:12px">
          <label>Mot de passe</label>
          <input v-model="password" :disabled="isLoading" type="password" required style="width:100%;padding:8px;margin-top:6px;box-sizing:border-box" />
        </div>
        <div v-if="error" style="margin-bottom:12px;padding:8px;background:#ffebee;color:#c62828;border-radius:4px;font-size:13px">
          {{ error }}
        </div>
        <div v-if="debugReq || debugRes" style="margin-top:24px;background:#f4f4f4;padding:12px;border-radius:6px;font-size:13px">
          <h3 style="font-size:15px;margin-bottom:8px">Debug API</h3>
          <div v-if="debugReq">
            <strong>Requête envoyée :</strong>
            <pre style="background:#e3f2fd;padding:8px;border-radius:4px">POST /login\n{{ debugReq }}</pre>
          </div>
          <div v-if="debugRes">
            <strong>Réponse :</strong>
            <pre style="background:#e8f5e9;padding:8px;border-radius:4px">{{ debugRes }}</pre>
          </div>
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <button type="submit" :disabled="isLoading">{{ isLoading ? 'Connexion...' : 'Se connecter' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../services/auth'

export default defineComponent({
  setup() {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const isLoading = ref(false)
    const debugReq = ref('')
    const debugRes = ref('')
    const router = useRouter()

    async function submit() {
      error.value = ''
      isLoading.value = true
      debugReq.value = JSON.stringify({ username: username.value, password: password.value }, null, 2)
      const result = await auth.login(username.value, password.value)
      debugRes.value = JSON.stringify(result, null, 2)

      if (result.success) {
        router.push('/page-accueil')
      } else {
        error.value = result.error || 'Erreur de connexion'
      }

      isLoading.value = false
    }

    return { username, password, error, isLoading, submit, debugReq, debugRes }
  }
})
</script>
