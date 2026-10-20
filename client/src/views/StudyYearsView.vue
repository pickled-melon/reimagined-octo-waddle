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

const studyYears = ref([]);
const users = ref([]);
const selectedUserId = ref("");
const studyYearToAdd = ref({});
const studyYearToEdit = ref({});

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchStudyYears() {
  let url = '/api/study-years/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  studyYears.value = r.data;
}

watch(selectedUserId, () => {
  fetchStudyYears();
});

async function onStudyYearAdd() {
  await axios.post('/api/study-years/', { ...studyYearToAdd.value });
  studyYearToAdd.value = {};
  await fetchStudyYears();
}

function onStudyYearEditClick(item) {
  studyYearToEdit.value = { ...item };
}

async function onUpdateStudyYear() {
  await axios.put(`/api/study-years/${studyYearToEdit.value.id}/`, {
    year: studyYearToEdit.value.year,
    max_weekly_hours: studyYearToEdit.value.max_weekly_hours,
    max_daily_hours: studyYearToEdit.value.max_daily_hours,
  });
  await fetchStudyYears();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить ${item.year} класс?`)) return;
  await axios.delete(`/api/study-years/${item.id}/`);
  await fetchStudyYears();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-calendar me-2"></i>Годы обучения</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ studyYears.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-white border-bottom-0 pt-3">
        <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить год
      </div>
      <div class="card-body">
        <form @submit.prevent="onStudyYearAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <label class="form-label">Год</label>
              <input type="number" class="form-control" v-model="studyYearToAdd.year" min="1" max="11" required />
            </div>
            <div class="col-md-4">
              <label class="form-label">Недельная нагрузка</label>
              <input type="number" class="form-control" v-model="studyYearToAdd.max_weekly_hours" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Дневная нагрузка</label>
              <input type="number" class="form-control" v-model="studyYearToAdd.max_daily_hours" required />
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
            <th>В неделю</th>
            <th>В день</th>
            <th>Автор</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in studyYears" :key="item.id">
            <td class="fw-semibold">{{ item.year }} класс</td>
            <td>{{ item.max_weekly_hours }}</td>
            <td>{{ item.max_daily_hours }}</td>
            <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary me-1" @click="onStudyYearEditClick(item)" data-bs-toggle="modal" data-bs-target="#editStudyYearModal">
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

    <div class="modal fade" id="editStudyYearModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Редактировать</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Год</label>
              <input type="number" class="form-control" v-model="studyYearToEdit.year" />
            </div>
            <div class="mb-3">
              <label class="form-label">Недельная</label>
              <input type="number" class="form-control" v-model="studyYearToEdit.max_weekly_hours" />
            </div>
            <div class="mb-3">
              <label class="form-label">Дневная</label>
              <input type="number" class="form-control" v-model="studyYearToEdit.max_daily_hours" />
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateStudyYear">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>