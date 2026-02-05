<template>
  <div class="canvas" style="padding:24px;display:flex;align-items:center;justify-content:center;min-height:100vh">
    <div style="width:360px;background:#fff;padding:24px;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.2)">
      <h2 style="margin:0 0 12px">Connexion</h2>
      <p style="font-size:12px;color:#666;margin:0 0 16px">Admin: admin / Utilisateur: user</p>
      <form @submit.prevent="submit">
        <div style="margin-bottom:12px">
          <label>Nom d'utilisateur</label>
          <input v-model="username" type="text" required style="width:100%;padding:8px;margin-top:6px;box-sizing:border-box" />
        </div>
        <div style="margin-bottom:12px">
          <label>Mot de passe</label>
          <input v-model="password" type="password" required style="width:100%;padding:8px;margin-top:6px;box-sizing:border-box" />
        </div>
        <div v-if="error" style="margin-bottom:12px;padding:8px;background:#ffebee;color:#c62828;border-radius:4px;font-size:13px">
          {{ error }}
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <button type="submit">Se connecter</button>
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
    const router = useRouter()

    function submit() {
      error.value = ''
      const result = auth.login(username.value, password.value)
      if (result.success) {
        // Redirect to appropriate page based on role
        router.push('/page-accueil')
      } else {
        error.value = result.error || 'Erreur de connexion'
      }
    }

    return { username, password, error, submit }
  }
})
</script>
