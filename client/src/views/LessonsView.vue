<script setup>
import { ref, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useCrud } from '@/composables/useCrud';
import CrudPage from '@/components/CrudPage.vue';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const {
  items, totalCount, currentPage, pageSize, stats,
  users, selectedUserId, isSuperuser, fetchUsers, fetchData, fetchStats, onRemove
} = useCrud('/api/lessons/');

const workloads = ref([]);
const classrooms = ref([]);
const bells = ref([]);
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

async function fetchWorkloads() {
  const r = await axios.get('/api/workloads/?page_size=1000');
  workloads.value = r.data.results;
}

async function fetchClassrooms() {
  const r = await axios.get('/api/classrooms/?page_size=1000');
  classrooms.value = r.data.results;
}

async function fetchBells() {
  const r = await axios.get('/api/bell-schedules/?page_size=1000');
  bells.value = r.data.results;
}

async function onAdd() {
  await axios.post('/api/lessons/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchData(1);
  await fetchStats();
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
  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteLesson(item) {
  await onRemove(item.id, `Удалить занятие "${item.workload_display}"?`);
  await fetchStats();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchWorkloads();
  await fetchClassrooms();
  await fetchBells();
  await fetchData(1);
  await fetchStats();
});
</script>

<template>
  <CrudPage
    title="Расписание"
    icon="bi-grid-3x3"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    :stats="stats"
    @update:selected-user-id="selectedUserId = $event"
    @update:current-page="currentPage = $event"
  >
    <template #form>
      <div class="card shadow-sm mb-3 border-0">
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
    </template>

    <template #content>
      <div class="card shadow-sm border-0 overflow-hidden">
        <table class="table table-hover align-middle mb-0 bg-white">
          <thead class="table-light sticky-top">
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
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteLesson(item)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template #modals>
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
    </template>
  </CrudPage>
</template>

<style scoped>
.sticky-top {
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>