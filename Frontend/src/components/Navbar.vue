<template>
  <header class="navbar" role="banner" aria-label="En-tete de l'application">
    <div class="navbar-inner">
      <router-link to="/page-accueil" class="navbar-brand" aria-label="Retour a l'accueil HealthAI MSRP">
        <img class="navbar-logo" :src="healthAiIcon" alt="" aria-hidden="true" />
        <span class="brand-copy">
          <span class="brand-name">HealthAI</span>
          <span class="brand-subtitle">MSPR</span>
        </span>
      </router-link>

      <router-link to="/page-accueil" class="nav-link nav-home">Accueil</router-link>
      <router-link v-if="currentUser" to="/chat" class="nav-link">Chat IA</router-link>

      <nav v-if="isAdmin" class="navbar-nav">
        <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/gestion-des-flux" class="nav-link">Flux</router-link>
        <router-link to="/nettoyage" class="nav-link">Nettoyage</router-link>
        <router-link to="/utilisateurs" class="nav-link">Utilisateurs</router-link>
        <router-link to="/test-backend" class="nav-link">Test API</router-link>
      </nav>

      <span class="navbar-page-title" aria-hidden="true">{{ title }}</span>

      <div class="navbar-user">
        <span v-if="currentUser" class="user-info" :aria-label="`Utilisateur connecte : ${currentUser.username}`">
          <span class="user-avatar">{{ userInitial }}</span>
          {{ currentUser.username }}
          <span class="user-role" :class="{ admin: isAdmin }">
            {{ isAdmin ? 'Admin' : 'Utilisateur' }}
          </span>
        </span>
        <button v-if="currentUser" class="btn-logout" aria-label="Se deconnecter" @click="logout">
          Deconnexion
        </button>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import healthAiIcon from '../assets/healthai_icon.svg'
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

    return { currentUser, healthAiIcon, isAdmin, userInitial, logout }
  }
})
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  min-height: 68px;
  align-items: center;
  padding: 0 24px;
  color: var(--gray-900);
  background: rgba(255, 255, 255, 0.86);
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(16px);
}

.navbar-inner {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  min-width: 0;
}

.navbar-brand {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 10px;
  color: var(--gray-900);
  font-size: 1rem;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  min-width: 0;
}

.navbar-brand:hover {
  opacity: 0.9;
  text-decoration: none;
}

.navbar-logo {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.24);
}

.brand-copy {
  display: grid;
  line-height: 1.05;
}

.brand-name {
  font-size: 1.02rem;
}

.brand-subtitle {
  color: var(--gray-500);
  font-size: 0.7rem;
  font-weight: 800;
}

.navbar-nav {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  color: var(--gray-600);
  font-size: 0.875rem;
  font-weight: 650;
  text-decoration: none;
  white-space: nowrap;
  border-radius: 8px;
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
}

.nav-link:hover {
  color: var(--gray-900);
  text-decoration: none;
  background: var(--gray-100);
}

.nav-link.router-link-active {
  color: var(--primary-dark);
  background: var(--primary-light);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.navbar-page-title {
  flex-shrink: 0;
  color: var(--gray-500);
  font-size: 0.9rem;
  white-space: nowrap;
}

.navbar-user {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--gray-700);
  font-size: 0.875rem;
  font-weight: 600;
}

.user-avatar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), #14b8a6);
  border-radius: 50%;
}

.user-role {
  padding: 2px 8px;
  color: var(--gray-600);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  background: var(--gray-100);
  border-radius: 999px;
}

.user-role.admin {
  color: #0369a1;
  background: #ecfeff;
}

.btn-logout {
  padding: 8px 13px;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  background: var(--gray-900);
  border: 1px solid var(--gray-900);
  border-radius: 8px;
  transition: background 0.15s, border-color 0.15s;
}

.btn-logout:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  box-shadow: none;
  transform: none;
}

@media (max-width: 900px) {
  .navbar-nav,
  .navbar-page-title,
  .user-info {
    display: none;
  }
}

@media (max-width: 720px) {
  .navbar {
    min-height: unset;
    padding: 10px 14px;
  }

  .navbar-inner {
    flex-wrap: wrap;
    gap: 8px;
  }

  .navbar-brand {
    flex: 1 1 auto;
    order: 1;
  }

  .navbar-user {
    order: 2;
    margin-left: 0;
  }

  .nav-home,
  .navbar-brand + .nav-link:not(.nav-home) {
    flex: 1 1 calc(50% - 4px);
    justify-content: center;
    order: 3;
    min-width: 0;
    background: var(--gray-100);
  }

  .btn-logout {
    min-height: 38px;
    padding: 7px 10px;
  }
}

@media (max-width: 540px) {
  .navbar {
    padding: 10px 12px;
  }

  .brand-subtitle {
    display: none;
  }

  .navbar-logo {
    width: 34px;
    height: 34px;
  }

  .brand-name {
    font-size: 0.95rem;
  }

  .nav-link {
    padding: 8px 10px;
    font-size: 0.82rem;
  }
}
</style>
