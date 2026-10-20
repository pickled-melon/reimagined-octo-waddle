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
const workloads = ref([]);
const classrooms = ref([]);
const bells = ref([]);
const users = ref([]);
const selectedUserId = ref("");
const itemToAdd = ref({});
const itemToEdit = ref({});

const WEEK_DAYS = [
  { value: 1, label: 'Пн' }, { value: 2, label: 'Вт' }, { value: 3, label: 'Ср' },
  { value: 4, label: 'Чт' }, { value: 5, label: 'Пт' }, { value: 6, label: 'Сб' },
];

function workloadLabel(w) {
  return w.study_group_display && w.subject_display
    ? `${w.study_group_display} — ${w.subject_display}`
    : `Нагрузка #${w.id}`;
}

function bellLabel(b) {
  return `${b.lesson_number}-й урок`;
}

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchItems() {
  let url = '/api/lessons/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  items.value = r.data;
}

async function fetchWorkloads() {
  const r = await axios.get('/api/workloads/');
  workloads.value = r.data;
}

async function fetchClassrooms() {
  const r = await axios.get('/api/classrooms/');
  classrooms.value = r.data;
}

async function fetchBells() {
  const r = await axios.get('/api/bell-schedules/');
  bells.value = r.data;
}

watch(selectedUserId, () => {
  fetchItems();
});

async function onAdd() {
  await axios.post('/api/lessons/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchItems();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/lessons/${itemToEdit.value.id}/`, {
    week_day: itemToEdit.value.week_day,
    is_test: itemToEdit.value.is_test,
    workload: itemToEdit.value.workload,
    classroom: itemToEdit.value.classroom,
    bell_schedule: itemToEdit.value.bell_schedule,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить занятие "${item.workload_display}"?`)) return;
  await axios.delete(`/api/lessons/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchWorkloads();
  await fetchClassrooms();
  await fetchBells();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-grid-3x3 me-2"></i>Расписание</h1>
      
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
        <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить занятие
      </div>
      <div class="card-body">
        <form @submit.prevent="onAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-2">
              <label class="form-label">День</label>
              <select class="form-select" v-model="itemToAdd.week_day" required>
                <option v-for="d in WEEK_DAYS" :key="d.value" :value="d.value">{{ d.label }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Нагрузка</label>
              <select class="form-select" v-model="itemToAdd.workload" required>
                <option v-for="w in workloads" :key="w.id" :value="w.id">{{ workloadLabel(w) }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Кабинет</label>
              <select class="form-select" v-model="itemToAdd.classroom" required>
                <option v-for="c in classrooms" :key="c.id" :value="c.id">Каб. {{ c.number }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Слот</label>
              <select class="form-select" v-model="itemToAdd.bell_schedule" required>
                <option v-for="b in bells" :key="b.id" :value="b.id">{{ bellLabel(b) }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <div class="form-check mt-4">
                <input class="form-check-input" type="checkbox" v-model="itemToAdd.is_test" id="isTestAdd" />
                <label class="form-check-label" for="isTestAdd">Контрольная</label>
              </div>
            </div>
            <div class="col-md-1">
              <button class="btn btn-primary w-100"><i class="bi bi-plus-lg"></i></button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm border-0 overflow-hidden">
      <table class="table table-hover align-middle mb-0 bg-white">
        <thead class="table-light">
          <tr>
            <th>День</th>
            <th>Слот</th>
            <th>Нагрузка</th>
            <th>Кабинет</th>
            <th>Контр.</th>
            <th>Автор</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="fw-semibold">{{ item.week_day_display }}</td>
            <td>{{ item.bell_schedule_display }}</td>
            <td>{{ item.workload_display }}</td>
            <td><span class="badge text-bg-light border">Каб. {{ item.classroom_display }}</span></td>
            <td>
              <span v-if="item.is_test" class="badge text-bg-danger rounded-pill">Да</span>
              <span v-else class="text-muted">—</span>
            </td>
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
            <h5 class="modal-title">Редактировать занятие</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">День</label>
              <select class="form-select" v-model="itemToEdit.week_day">
                <option v-for="d in WEEK_DAYS" :key="d.value" :value="d.value">{{ d.label }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Нагрузка</label>
              <select class="form-select" v-model="itemToEdit.workload">
                <option v-for="w in workloads" :key="w.id" :value="w.id">{{ workloadLabel(w) }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Кабинет</label>
              <select class="form-select" v-model="itemToEdit.classroom">
                <option v-for="c in classrooms" :key="c.id" :value="c.id">Каб. {{ c.number }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Слот</label>
              <select class="form-select" v-model="itemToEdit.bell_schedule">
                <option v-for="b in bells" :key="b.id" :value="b.id">{{ bellLabel(b) }}</option>
              </select>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="itemToEdit.is_test" id="isTestEdit" />
              <label class="form-check-label" for="isTestEdit">Контрольная</label>
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