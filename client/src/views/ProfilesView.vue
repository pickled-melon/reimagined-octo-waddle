<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const profiles = ref([]);
const profileToEdit = ref({});

const ROLES = [
  { value: 0, label: 'Не определена' },
  { value: 1, label: 'Методист' },
  { value: 2, label: 'Завуч' },
  { value: 3, label: 'Учитель' },
];

async function fetchProfiles() {
  const r = await axios.get('/api/profile/'); // ИСПРАВЛЕНО
  profiles.value = r.data;
}

function onProfileEditClick(item) {
  profileToEdit.value = { ...item };
}

async function onUpdateProfile() {
  await axios.put(`/api/profile/${profileToEdit.value.id}/`, { // ИСПРАВЛЕНО
    last_name: profileToEdit.value.last_name || '',
    first_name: profileToEdit.value.first_name || '',
    patronymic_name: profileToEdit.value.patronymic_name || '',
    role: profileToEdit.value.role,
  });
  await fetchProfiles();
}

onBeforeMount(fetchProfiles);
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-person-circle me-2"></i>Профили</h1>
      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ profiles.length }}</span>
    </div>

    <div class="card shadow-sm border-0 overflow-hidden">
      <table class="table table-hover align-middle mb-0 bg-white">
        <thead class="table-light">
          <tr>
            <th>Логин</th>
            <th>ФИО</th>
            <th>Роль</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in profiles" :key="item.id">
            <td class="fw-semibold text-primary">{{ item.username }}</td>
            <td>{{ item.user_display }}</td>
            <td>
              <span class="badge rounded-pill" :class="item.role === 1 ? 'text-bg-success' : item.role === 2 ? 'text-bg-warning' : item.role === 3 ? 'text-bg-info' : 'text-bg-secondary'">
                {{ item.role_display }}
              </span>
            </td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary" @click="onProfileEditClick(item)" data-bs-toggle="modal" data-bs-target="#editProfileModal">
                <i class="bi bi-pencil"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" id="editProfileModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Редактировать профиль</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Логин</label>
              <input class="form-control" :value="profileToEdit.username" disabled />
            </div>
            <div class="mb-3">
              <label class="form-label">Фамилия</label>
              <input class="form-control" v-model="profileToEdit.last_name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Имя</label>
              <input class="form-control" v-model="profileToEdit.first_name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Отчество</label>
              <input class="form-control" v-model="profileToEdit.patronymic_name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Роль</label>
              <select class="form-select" v-model="profileToEdit.role">
                <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateProfile">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>