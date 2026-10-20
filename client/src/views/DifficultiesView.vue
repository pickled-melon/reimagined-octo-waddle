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
const studyYears = ref([]);
const users = ref([]);
const selectedUserId = ref("");
const itemToAdd = ref({});
const itemToEdit = ref({});

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchItems() {
  let url = '/api/difficulties/';
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

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/');
  studyYears.value = r.data;
}

watch(selectedUserId, () => {
  fetchItems();
});

async function onAdd() {
  await axios.post('/api/difficulties/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchItems();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/difficulties/${itemToEdit.value.id}/`, {
    study_year: itemToEdit.value.study_year,
    subject: itemToEdit.value.subject,
    points: itemToEdit.value.points,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить "${item.subject_display} — ${item.study_year_display} класс"?`)) return;
  await axios.delete(`/api/difficulties/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
  await fetchSubjects();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-bar-chart me-2"></i>Трудности</h1>
      
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
            <div class="col-md-4">
              <label class="form-label">Год обучения</label>
              <select class="form-select" v-model="itemToAdd.study_year" required>
                <option v-for="y in studyYears" :key="y.id" :value="y.id">{{ y.year }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Дисциплина</label>
              <select class="form-select" v-model="itemToAdd.subject" required>
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Баллы</label>
              <input type="number" class="form-control" v-model="itemToAdd.points" min="1" required />
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
            <th>Год</th>
            <th>Дисциплина</th>
            <th>Баллы</th>
            <th>Автор</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="fw-semibold">{{ item.study_year_display }} класс</td>
            <td>{{ item.subject_display }}</td>
            <td>{{ item.points }}</td>
            <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
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
              <label class="form-label">Год обучения</label>
              <select class="form-select" v-model="itemToEdit.study_year">
                <option v-for="y in studyYears" :key="y.id" :value="y.id">{{ y.year }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Дисциплина</label>
              <select class="form-select" v-model="itemToEdit.subject">
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Баллы</label>
              <input type="number" class="form-control" v-model="itemToEdit.points" />
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