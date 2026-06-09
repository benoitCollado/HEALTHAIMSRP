<template>
  <header class="navbar" :class="{ 'menu-open': isMenuOpen }" role="banner" aria-label="En-tete de l'application">
    <div class="navbar-inner">
      <router-link to="/page-accueil" class="navbar-brand" aria-label="Retour a l'accueil HealthAI MSRP" @click="closeMenu">
        <img class="navbar-logo" :src="healthAiIcon" alt="" aria-hidden="true" />
        <span class="brand-copy">
          <span class="brand-name">HealthAI</span>
          <span class="brand-subtitle">MSPR</span>
        </span>
      </router-link>

      <button
        v-if="currentUser"
        type="button"
        class="menu-toggle"
        :aria-expanded="isMenuOpen ? 'true' : 'false'"
        aria-controls="main-navigation"
        aria-label="Ouvrir ou fermer le menu"
        @click="toggleMenu"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </button>

      <nav id="main-navigation" v-if="currentUser" class="navbar-nav" :class="{ open: isMenuOpen }" aria-label="Navigation principale">
        <router-link to="/page-accueil" class="nav-link nav-home" @click="closeMenu">Accueil</router-link>
        <router-link to="/chat" class="nav-link" @click="closeMenu">Chat IA</router-link>
        <button
          v-for="action in pageActions"
          :key="action.id"
          type="button"
          class="nav-link nav-action"
          :class="{ active: activeAction === action.id }"
          @click="selectAction(action.id)"
        >
          <span class="nav-action-label">{{ action.label }}</span>
          <span v-if="action.count !== undefined" class="nav-count">{{ action.count }}</span>
        </button>
        <template v-if="isAdmin">
          <router-link to="/dashboard" class="nav-link" @click="closeMenu">Dashboard</router-link>
          <router-link to="/gestion-des-flux" class="nav-link" @click="closeMenu">Flux</router-link>
          <router-link to="/nettoyage" class="nav-link" @click="closeMenu">Nettoyage</router-link>
          <router-link to="/utilisateurs" class="nav-link" @click="closeMenu">Utilisateurs</router-link>
          <router-link to="/test-backend" class="nav-link" @click="closeMenu">Test API</router-link>
        </template>
        <button type="button" class="nav-link nav-logout" @click="logout">
          Deconnexion
        </button>
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
import { computed, defineComponent, onMounted, PropType, ref } from 'vue'
import { useRouter } from 'vue-router'
import healthAiIcon from '../assets/healthai_icon.svg'
import { auth, type User } from '../services/auth'

export default defineComponent({
  props: {
    title: { type: String, required: true },
    pageActions: {
      type: Array as PropType<Array<{ id: string; label: string; icon?: string; count?: number }>>,
      default: () => []
    },
    activeAction: { type: String, default: '' }
  },
  emits: ['select-action'],
  setup(_props, { emit }) {
    const currentUser = ref<User | null>(null)
    const isMenuOpen = ref(false)
    const router = useRouter()
    const isAdmin = computed(() => auth.isAdmin())
    const userInitial = computed(() => currentUser.value?.username?.charAt(0).toUpperCase() ?? '?')

    onMounted(() => {
      currentUser.value = auth.getCurrentUser()
    })

    function closeMenu() {
      isMenuOpen.value = false
    }

    function toggleMenu() {
      isMenuOpen.value = !isMenuOpen.value
    }

    function selectAction(actionId: string) {
      emit('select-action', actionId)
      closeMenu()
    }

    function logout() {
      closeMenu()
      auth.logout()
      router.push('/connexion')
    }

    return { currentUser, healthAiIcon, isAdmin, isMenuOpen, userInitial, closeMenu, toggleMenu, selectAction, logout }
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
  padding: 12px 24px;
  color: var(--gray-900);
  background: rgba(255, 255, 255, 0.86);
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(16px);
}

.navbar-inner {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 1600px;
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
  gap: 8px;
  min-width: 0;
  overflow-x: auto;
  padding: 2px 0;
  scrollbar-width: thin;
}

.menu-toggle {
  display: none;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 42px;
  padding: 8px 14px;
  color: var(--gray-600);
  font-size: 0.875rem;
  font-weight: 650;
  text-decoration: none;
  white-space: nowrap;
  background: transparent;
  border: 0;
  border-radius: 8px;
  box-shadow: none;
  cursor: pointer;
  transform: none;
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
}

.nav-action {
  flex: 0 0 auto;
  min-width: 112px;
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

.nav-action.active {
  color: var(--primary-dark);
  background: var(--primary-light);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.nav-action:last-of-type {
  min-width: 136px;
}

.nav-action-label {
  overflow: visible;
  text-overflow: clip;
}

.nav-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 800;
  background: var(--primary);
  border-radius: 999px;
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

.nav-logout {
  display: none;
}

@media (max-width: 900px) {
  .navbar-page-title,
  .user-info {
    display: none;
  }

  .navbar {
    padding: 10px 16px;
  }

  .navbar-inner {
    gap: 10px;
  }

  .navbar-brand {
    flex: 1 1 auto;
  }

  .menu-toggle {
    display: inline-flex;
    flex: 0 0 42px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    min-height: 42px;
    padding: 0;
    gap: 4px;
    background: var(--gray-900);
    border: 1px solid var(--gray-900);
    border-radius: 8px;
    box-shadow: none;
    transform: none;
  }

  .menu-toggle:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
    box-shadow: none;
    transform: none;
  }

  .menu-toggle span {
    display: block;
    width: 18px;
    height: 2px;
    background: #fff;
    border-radius: 999px;
    transition: transform 0.18s ease, opacity 0.18s ease;
  }

  .menu-open .menu-toggle span:nth-child(1) {
    transform: translateY(6px) rotate(45deg);
  }

  .menu-open .menu-toggle span:nth-child(2) {
    opacity: 0;
  }

  .menu-open .menu-toggle span:nth-child(3) {
    transform: translateY(-6px) rotate(-45deg);
  }

  .navbar-nav {
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    left: 0;
    display: none;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 8px;
    box-shadow: var(--shadow-lg);
    backdrop-filter: blur(16px);
  }

  .navbar-nav.open {
    display: flex;
  }

  .nav-link,
  .navbar-nav .nav-link {
    justify-content: flex-start;
    width: 100%;
    min-height: 42px;
    padding: 10px 12px;
    background: var(--gray-100);
  }

  .nav-logout {
    display: inline-flex;
    justify-content: center;
    color: #fff;
    background: var(--gray-900);
  }

  .nav-logout:hover {
    color: #fff;
    background: var(--primary-dark);
  }

  .btn-logout {
    display: none;
  }
}

@media (max-width: 720px) {
  .navbar {
    min-height: unset;
    padding: 10px 14px;
  }

  .navbar-inner {
    flex-wrap: nowrap;
    gap: 8px;
  }

  .navbar-user {
    margin-left: 0;
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
