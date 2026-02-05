<template>
  <header class="navbar">
    <div class="navbar-content">
      <router-link to="/page-accueil" class="navbar-title">← HealthAI MSRP</router-link>
      <span class="navbar-page-title">{{ title }}</span>
      <div class="navbar-user">
        <span v-if="currentUser" style="font-size:13px">{{ currentUser.username }} ({{ currentUser.role }})</span>
        <button v-if="currentUser" @click="logout" style="padding:6px 12px">Déconnexion</button>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth, type User } from '../services/auth'

export default defineComponent({
  props: { title: { type: String, required: true } },
  setup() {
    const currentUser = ref<User | null>(null)
    const router = useRouter()

    onMounted(() => {
      currentUser.value = auth.getCurrentUser()
    })

    function logout() {
      auth.logout()
      router.push('/connexion')
    }

    return { currentUser, logout }
  }
})
</script>

<style scoped>
.navbar {
  background: #444;
  color: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  width: 100%;
}
.navbar-title {
  text-decoration: none;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  transition: opacity 0.2s;
}
.navbar-title:hover {
  opacity: 0.8;
}
.navbar-page-title {
  font-size: 16px;
  opacity: 0.9;
}
.navbar-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
</style>
