<script setup>
import axios from 'axios';
import { onBeforeMount, ref, watch } from 'vue';
import Cookies from 'js-cookie';
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const profileStore = useProfileStore();
const { isSuperuser } = storeToRefs(profileStore);

const items = ref([]);
const subjects = ref([]);
const profiles = ref([]);
const users = ref([]);
const selectedUserId = ref("");
const itemToAdd = ref({});
const itemToEdit = ref({});

function teacherLabel(profile) {
  return profile.user_display || profile.user;
}

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchItems() {
  let url = '/api/user-subjects/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  items.value = r.data;
}

async function fetchSubjects() {
  const r = await axios.get('/api/subjects/');
  subjects.value = r.data;
}

async function fetchProfiles() {
  const r = await axios.get('/api/profile/'); // ИСПРАВЛЕНО
  profiles.value = r.data;
}

watch(selectedUserId, () => {
  fetchItems();
});

async function onAdd() {
  await axios.post('/api/user-subjects/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchItems();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/user-subjects/${itemToEdit.value.id}/`, {
    user: itemToEdit.value.user,
    subject: itemToEdit.value.subject,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить "${item.user_display} — ${item.subject_display}"?`)) return;
  await axios.delete(`/api/user-subjects/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchProfiles();
  await fetchSubjects();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-person-badge me-2"></i>Дисциплины учителей</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ items.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-white border-bottom-0 pt-3">
        <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить
      </div>
      <div class="card-body">
        <form @submit.prevent="onAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label">Учитель</label>
              <select class="form-select" v-model="itemToAdd.user" required>
                <option v-for="p in profiles" :key="p.id" :value="p.user">{{ teacherLabel(p) }}</option>
              </select>
            </div>
            <div class="col-md-5">
              <label class="form-label">Дисциплина</label>
              <select class="form-select" v-model="itemToAdd.subject" required>
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100"><i class="bi bi-plus-lg me-1"></i>Добавить</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm border-0 overflow-hidden">
      <table class="table table-hover align-middle mb-0 bg-white">
        <thead class="table-light">
          <tr>
            <th>Учитель</th>
            <th>Дисциплина</th>
            <th>Автор записи</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="fw-semibold">{{ item.user_display }}</td>
            <td>{{ item.subject_display }}</td>
            <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.creator_display }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary me-1" @click="onEditClick(item)" data-bs-toggle="modal" data-bs-target="#editItemModal">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" id="editItemModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Редактировать</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Учитель</label>
              <select class="form-select" v-model="itemToEdit.user">
                <option v-for="p in profiles" :key="p.id" :value="p.user">{{ teacherLabel(p) }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Дисциплина</label>
              <select class="form-select" v-model="itemToEdit.subject">
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdate">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>