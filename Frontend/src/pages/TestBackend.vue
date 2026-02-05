<template>
  <div class="test-backend">
    <Navbar title="Test Backend API" />
    <h1>Test Backend API</h1>
    <div class="test-section">
      <h2>Test /aliments/</h2>
      <button @click="testGetAliments">GET /aliments/</button>
      <pre v-if="alimentsResponse">{{ alimentsResponse }}</pre>
    </div>
    <div class="test-section">
      <h2>Test /utilisateurs/</h2>
      <button @click="testGetUtilisateurs">GET /utilisateurs/</button>
      <pre v-if="utilisateursResponse">{{ utilisateursResponse }}</pre>
    </div>
    <div class="test-section">
      <h2>Test /login</h2>
      <form @submit.prevent="testLogin">
        <input v-model="loginData.username" placeholder="Username" required />
        <input v-model="loginData.password" type="password" placeholder="Password" required />
        <button type="submit">POST /login</button>
      </form>
      <pre v-if="loginResponse">{{ loginResponse }}</pre>
    </div>
    <div v-if="loading" style="color:#888">Chargement...</div>
    <div v-if="error" style="color:#a00;margin-bottom:12px">Erreur : {{ error }}</div>
  </div>
</template>

<script lang="ts">

import { defineComponent, ref } from 'vue';
import Navbar from '../components/Navbar.vue';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default defineComponent({
  components: { Navbar },
  setup() {
    const alimentsResponse = ref('');
    const utilisateursResponse = ref('');
    const loginResponse = ref('');
    const loginData = ref({ username: '', password: '' });
    const error = ref('');
    const loading = ref(false);

    async function testGetAliments() {
      alimentsResponse.value = '';
      error.value = '';
      loading.value = true;
      try {
        const res = await fetch(`${API_URL}/aliments/`);
        const data = await res.json();
        alimentsResponse.value = JSON.stringify(data, null, 2);
      } catch (e:any) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    }

    async function testGetUtilisateurs() {
      utilisateursResponse.value = '';
      error.value = '';
      loading.value = true;
      try {
        const res = await fetch(`${API_URL}/utilisateurs/`);
        const data = await res.json();
        utilisateursResponse.value = JSON.stringify(data, null, 2);
      } catch (e:any) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    }

    async function testLogin() {
      loginResponse.value = '';
      error.value = '';
      loading.value = true;
      try {
        const res = await fetch(`${API_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(loginData.value)
        });
        const data = await res.json();
        loginResponse.value = JSON.stringify(data, null, 2);
      } catch (e:any) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    }


    return {
      alimentsResponse,
      utilisateursResponse,
      loginResponse,
      loginData,
      error,
      loading,
      testGetAliments,
      testGetUtilisateurs,
      testLogin,
    };
  }
});
</script>


<style scoped>
.test-backend {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.test-section {
  margin-bottom: 2rem;
}
button {
  margin-bottom: 1rem;
}
pre {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}
form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
