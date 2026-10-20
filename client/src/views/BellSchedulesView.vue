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

const bells = ref([]);
const users = ref([]);
const selectedUserId = ref("");
const bellToAdd = ref({});
const bellToEdit = ref({});

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchBells() {
  let url = '/api/bell-schedules/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  bells.value = r.data;
}

watch(selectedUserId, () => {
  fetchBells();
});

async function onBellAdd() {
  await axios.post('/api/bell-schedules/', { ...bellToAdd.value });
  bellToAdd.value = {};
  await fetchBells();
}

function onBellEditClick(item) {
  bellToEdit.value = { ...item };
}

async function onUpdateBell() {
  await axios.put(`/api/bell-schedules/${bellToEdit.value.id}/`, {
    lesson_number: bellToEdit.value.lesson_number,
    start_time: bellToEdit.value.start_time,
    end_time: bellToEdit.value.end_time,
  });
  await fetchBells();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить ${item.lesson_number}-й урок?`)) return;
  await axios.delete(`/api/bell-schedules/${item.id}/`);
  await fetchBells();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchBells();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-clock me-2"></i>Расписание звонков</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ bells.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-white border-bottom-0 pt-3">
        <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить звонок
      </div>
      <div class="card-body">
        <form @submit.prevent="onBellAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <label class="form-label">№ урока</label>
              <input type="number" class="form-control" v-model="bellToAdd.lesson_number" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Начало</label>
              <input type="time" class="form-control" v-model="bellToAdd.start_time" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Конец</label>
              <input type="time" class="form-control" v-model="bellToAdd.end_time" required />
            </div>
            <div class="col-md-3">
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
            <th>№</th>
            <th>Начало</th>
            <th>Конец</th>
            <th>Автор</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bells" :key="item.id">
            <td class="fw-semibold">{{ item.lesson_number }}</td>
            <td>{{ item.start_time }}</td>
            <td>{{ item.end_time }}</td>
            <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary me-1" @click="onBellEditClick(item)" data-bs-toggle="modal" data-bs-target="#editBellModal">
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

    <div class="modal fade" id="editBellModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title">Редактировать</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">№ урока</label>
              <input type="number" class="form-control" v-model="bellToEdit.lesson_number" />
            </div>
            <div class="mb-3">
              <label class="form-label">Начало</label>
              <input type="time" class="form-control" v-model="bellToEdit.start_time" />
            </div>
            <div class="mb-3">
              <label class="form-label">Конец</label>
              <input type="time" class="form-control" v-model="bellToEdit.end_time" />
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateBell">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>