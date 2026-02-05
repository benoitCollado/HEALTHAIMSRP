<template>
  <div class="canvas" style="padding:24px;">
    <div style="width:360px;background:#fff;padding:24px;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.2)">
      <h2 style="margin:0 0 12px">Connexion</h2>
      <form @submit.prevent="submit">
        <div style="margin-bottom:12px">
          <label>Email</label>
          <input v-model="email" type="email" required style="width:100%;padding:8px;margin-top:6px" />
        </div>
        <div style="margin-bottom:12px">
          <label>Mot de passe</label>
          <input v-model="password" type="password" required style="width:100%;padding:8px;margin-top:6px" />
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <button type="submit">Se connecter</button>
          <router-link to="/dashboard">Tester sans compte</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {
    const email = ref('')
    const password = ref('')
    const router = useRouter()

    function submit() {
      // no backend: simulate successful login
      router.push({ path: '/page-accueil' })
    }

    return { email, password, submit }
  }
})
</script>
