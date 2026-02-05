<template>
  <div class="canvas nav-page">
    <Navbar title="Accueil" />
    <div class="page-content">
      <!-- Admin view: Navigation -->
      <div v-if="isAdmin">
        <h2>Page d'accueil</h2>
        <p>Bienvenue dans le système de gestion des flux</p>
        <div class="nav-grid">
          <router-link to="/dashboard" class="nav-card">
            <div class="nav-icon">📊</div>
            <div>Dashboard</div>
          </router-link>
          <router-link to="/gestion-des-flux" class="nav-card">
            <div class="nav-icon">📋</div>
            <div>Gestion des flux</div>
          </router-link>
          <router-link to="/nettoyage" class="nav-card">
            <div class="nav-icon">🧹</div>
            <div>Nettoyage</div>
          </router-link>
        </div>
      </div>

      <!-- User view: Profile -->
      <div v-else style="max-width:600px;margin:0 auto">
        <h2>Votre profil</h2>
        <div style="background:#fff;padding:24px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
          <!-- Profile section -->
          <div style="margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #eee">
            <h3>Informations personnelles</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px">
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Nom</div>
                <div style="font-weight:600;margin-top:4px">[ Placeholder ]</div>
              </div>
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Email</div>
                <div style="font-weight:600;margin-top:4px">[ Placeholder ]</div>
              </div>
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Taille</div>
                <div style="font-weight:600;margin-top:4px">[ -- cm ]</div>
              </div>
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Poids</div>
                <div style="font-weight:600;margin-top:4px">[ -- kg ]</div>
              </div>
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Âge</div>
                <div style="font-weight:600;margin-top:4px">[ -- ans ]</div>
              </div>
              <div style="padding:12px;background:#f6f6f6;border-radius:6px">
                <div style="font-size:12px;color:#666">Date d'enregistrement</div>
                <div style="font-weight:600;margin-top:4px">[ -- ]</div>
              </div>
            </div>
          </div>

          <!-- Alimentation section -->
          <div style="margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #eee">
            <h3>Alimentation</h3>
            <div style="background:#f9f9f9;padding:16px;border-radius:6px;margin-top:12px">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div>
                  <div style="font-size:12px;color:#666">Calories quotidiennes (cible)</div>
                  <div style="font-weight:600;margin-top:4px">[ -- kcal ]</div>
                </div>
                <div>
                  <div style="font-size:12px;color:#666">Protéines (cible)</div>
                  <div style="font-weight:600;margin-top:4px">[ -- g ]</div>
                </div>
                <div>
                  <div style="font-size:12px;color:#666">Glucides (cible)</div>
                  <div style="font-weight:600;margin-top:4px">[ -- g ]</div>
                </div>
                <div>
                  <div style="font-size:12px;color:#666">Lipides (cible)</div>
                  <div style="font-weight:600;margin-top:4px">[ -- g ]</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Notice section -->
          <div style="background:#e3f2fd;padding:16px;border-radius:6px;border-left:4px solid #2196f3">
            <div style="font-size:14px;color:#1565c0">
              <strong>ℹ️ Note:</strong> Cette partie de l'application ne sera pas développée côté client. Les données de profil et d'alimentation seront gérées ultérieurement via le backend.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { auth } from '../services/auth'

export default defineComponent({
  components: { Navbar },
  setup() {
    const isAdmin = computed(() => auth.isAdmin())
    return { isAdmin }
  }
})
</script>

<style scoped>
.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 32px;
  max-width: 900px;
}
.nav-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  font-size: 18px;
  font-weight: 500;
}
.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
.nav-icon {
  font-size: 48px;
}
</style>
