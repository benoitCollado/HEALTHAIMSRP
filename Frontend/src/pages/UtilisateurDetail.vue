<template>
  <div class="canvas" role="main" aria-label="Détail des données utilisateur">
    <Navbar :title="`Utilisateur : ${data?.utilisateur?.username ?? '...'}`" />
    <div id="main-content" class="detail-container">
      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement des données...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>

      <template v-if="data && !loading">
        <section class="card" aria-labelledby="profil-title">
          <div class="header-row">
            <h2 id="profil-title">Profil : {{ data.utilisateur.username }}</h2>
            <router-link to="/utilisateurs" class="btn btn-back" aria-label="Retour à la liste des utilisateurs">
              ← Retour
            </router-link>
          </div>
          <div class="profil-grid">
            <div class="profil-item"><span class="label">ID</span><span class="value">{{ data.utilisateur.id_utilisateur }}</span></div>
            <div class="profil-item"><span class="label">Âge</span><span class="value">{{ data.utilisateur.age }} ans</span></div>
            <div class="profil-item"><span class="label">Sexe</span><span class="value">{{ data.utilisateur.sexe }}</span></div>
            <div class="profil-item"><span class="label">Taille</span><span class="value">{{ data.utilisateur.taille_cm }} cm</span></div>
            <div class="profil-item"><span class="label">Poids</span><span class="value">{{ data.utilisateur.poids_kg }} kg</span></div>
            <div class="profil-item"><span class="label">Inscription</span><span class="value">{{ data.utilisateur.date_inscription }}</span></div>
          </div>
        </section>

        <section class="card" aria-labelledby="cons-title">
          <h2 id="cons-title">Consommations ({{ data.consommations.length }})</h2>
          <div v-if="data.consommations.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Quantité (g)</th>
                  <th scope="col">Calories</th>
                  <th scope="col">ID aliment</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in data.consommations" :key="c.id_consommation">
                  <td>{{ c.date_consommation }}</td>
                  <td>{{ c.quantite_g }}</td>
                  <td>{{ c.calories_calculees }}</td>
                  <td>{{ c.id_aliment }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune consommation</p>
        </section>

        <section class="card" aria-labelledby="act-title">
          <h2 id="act-title">Activités ({{ data.activites.length }})</h2>
          <div v-if="data.activites.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Durée (min)</th>
                  <th scope="col">Calories dépensées</th>
                  <th scope="col">ID exercice</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in data.activites" :key="a.id_activite">
                  <td>{{ a.date_activite }}</td>
                  <td>{{ a.duree_minutes }}</td>
                  <td>{{ a.calories_depensees }}</td>
                  <td>{{ a.id_exercice }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune activité</p>
        </section>

        <section class="card" aria-labelledby="met-title">
          <h2 id="met-title">Métriques santé ({{ data.metriques.length }})</h2>
          <div v-if="data.metriques.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Poids (kg)</th>
                  <th scope="col">FC</th>
                  <th scope="col">Sommeil (h)</th>
                  <th scope="col">Pas</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in data.metriques" :key="m.id_metrique">
                  <td>{{ m.date_mesure }}</td>
                  <td>{{ m.poids_kg ?? '-' }}</td>
                  <td>{{ m.frequence_cardiaque ?? '-' }}</td>
                  <td>{{ m.duree_sommeil_h ?? '-' }}</td>
                  <td>{{ m.pas ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune métrique</p>
        </section>

        <section class="card" aria-labelledby="obj-title">
          <h2 id="obj-title">Objectifs ({{ data.objectifs.length }})</h2>
          <div v-if="data.objectifs.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Type</th>
                  <th scope="col">Description</th>
                  <th scope="col">Début</th>
                  <th scope="col">Fin</th>
                  <th scope="col">Statut</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in data.objectifs" :key="o.id_objectif">
                  <td>{{ o.type_objectif }}</td>
                  <td>{{ o.description }}</td>
                  <td>{{ o.date_debut }}</td>
                  <td>{{ o.date_fin }}</td>
                  <td>{{ o.statut }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucun objectif</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { useRoute } from 'vue-router'
import { getUtilisateurDonnees, type UtilisateurDonnees } from '../services/adminApi'

async function loadUser(id: number, data: { value: UtilisateurDonnees | null }, loading: { value: boolean }, error: { value: string }) {
  if (!Number.isFinite(id)) {
    error.value = 'ID utilisateur invalide'
    loading.value = false
    return
  }
  try {
    loading.value = true
    error.value = ''
    data.value = await getUtilisateurDonnees(id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Erreur lors du chargement.'
    data.value = null
  } finally {
    loading.value = false
  }
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const route = useRoute()
    const id = computed(() => {
      const p = route.params.id
      return Number(Array.isArray(p) ? p[0] : p)
    })
    const data = ref<UtilisateurDonnees | null>(null)
    const loading = ref(true)
    const error = ref('')

    const fetchData = () => loadUser(id.value, data, loading, error)

    onMounted(fetchData)
    watch(id, fetchData)

    return { data, loading, error }
  }
})
</script>

<style scoped>
.detail-container {
  padding: 24px;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card h2 {
  font-size: 1rem;
  margin: 0;
  color: #2f4b66;
}

.profil-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.profil-item {
  padding: 8px 12px;
  background: #f7f9fc;
  border-radius: 6px;
}

.profil-item .label {
  display: block;
  font-size: 0.8rem;
  color: #5a6c7d;
}

.profil-item .value {
  font-weight: 600;
  color: #2f4b66;
}

.btn-back {
  padding: 8px 16px;
  border-radius: 6px;
  background: #5a6c7d;
  color: #fff;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn-back:hover {
  background: #4a5c6d;
}

.table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.table th {
  font-weight: 600;
  background: #f7f9fc;
  color: #2f4b66;
}

.empty-msg {
  margin: 0;
  color: #666;
  font-style: italic;
}

.loading, .error {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.loading {
  background: #f5f7fa;
  color: #2f4b66;
}

.error {
  background: #ffebee;
  color: #c62828;
}
</style>
