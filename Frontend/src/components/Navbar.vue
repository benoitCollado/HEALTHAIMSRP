<template>
  <header class="navbar">
    <div class="navbar-inner">
      <!-- Logo / accueil -->
      <router-link to="/page-accueil" class="navbar-brand">
        <span class="navbar-logo">❤️</span>
        HealthAI MSRP
      </router-link>

      <!-- Navigation admin -->
      <nav v-if="isAdmin" class="navbar-nav">
        <router-link to="/dashboard"        class="nav-link">📊 Dashboard</router-link>
        <router-link to="/gestion-des-flux" class="nav-link">📋 Flux</router-link>
        <router-link to="/nettoyage"        class="nav-link">🧹 Nettoyage</router-link>
        <router-link to="/test-backend"     class="nav-link">🧪 Test API</router-link>
      </nav>

      <!-- Titre de la page courante -->
      <span class="navbar-page-title">{{ title }}</span>

      <!-- Utilisateur + déconnexion -->
      <div class="navbar-user">
        <span v-if="currentUser" class="user-info">
          <span class="user-avatar">{{ userInitial }}</span>
          {{ currentUser.username }}
          <span class="user-role" :class="{ admin: isAdmin }">
            {{ isAdmin ? 'Admin' : 'Utilisateur' }}
          </span>
        </span>
        <button v-if="currentUser" @click="logout" class="btn-logout">
          Déconnexion
        </button>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth, type User } from '../services/auth'

export default defineComponent({
  props: { title: { type: String, required: true } },
  setup() {
    const currentUser = ref<User | null>(null)
    const router = useRouter()
    const isAdmin = computed(() => auth.isAdmin())
    const userInitial = computed(() => currentUser.value?.username?.charAt(0).toUpperCase() ?? '?')

    onMounted(() => {
      currentUser.value = auth.getCurrentUser()
    })

    function logout() {
      auth.logout()
      router.push('/connexion')
    }

    return { currentUser, isAdmin, userInitial, logout }
  }
})
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
  color: #fff;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.20);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

/* Brand */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.3px;
}
.navbar-brand:hover { opacity: 0.85; text-decoration: none; }
.navbar-logo { font-size: 1.2rem; }

/* Nav links */
.navbar-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 6px;
  color: rgba(255,255,255,0.85);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-link:hover { background: rgba(255,255,255,0.15); color: #fff; text-decoration: none; }
.nav-link.router-link-active {
  background: rgba(255,255,255,0.2);
  color: #fff;
  font-weight: 600;
}

/* Page title */
.navbar-page-title {
  font-size: 0.9rem;
  opacity: 0.75;
  white-space: nowrap;
  flex-shrink: 0;
}

/* User info */
.navbar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: rgba(255,255,255,0.9);
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.user-role {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(255,255,255,0.18);
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.user-role.admin { background: rgba(251,191,36,0.3); color: #fde68a; }

.btn-logout {
  padding: 6px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-logout:hover { background: rgba(255,255,255,0.25); transform: none; box-shadow: none; }

/* Responsive */
@media (max-width: 900px) {
  .navbar-nav { display: none; }
  .navbar-page-title { display: none; }
  .user-info { display: none; }
}
</style>
