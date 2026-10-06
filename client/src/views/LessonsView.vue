<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const items = ref([]);
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

async function fetchItems() {
  const r = await axios.get('/api/lessons/');
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
    ...itemToEdit.value,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить занятие "${item.workload_display}"?`)) return;
  await axios.delete(`/api/lessons/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchWorkloads();
  await fetchClassrooms();
  await fetchBells();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-grid-3x3 me-2"></i>Расписание</h1>
      <span class="badge text-bg-secondary">Всего: {{ items.length }}</span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">Добавить занятие</div>
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
              <div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="itemToAdd.is_test" id="isTestAdd" />
                <label class="form-check-label" for="isTestAdd">Контрольная</label>
              </div>
            </div>
            <div class="col-md-1">
              <button class="btn btn-primary w-100">+</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead>
        <tr>
          <th>День</th>
          <th>Слот</th>
          <th>Нагрузка</th>
          <th>Кабинет</th>
          <th>Контр.</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.week_day_display }}</td>
          <td>{{ item.bell_schedule_display }}</td>
          <td>{{ item.workload_display }}</td>
          <td>Каб. {{ item.classroom_display }}</td>
          <td>
            <span v-if="item.is_test" class="badge text-bg-danger">Да</span>
            <span v-else class="text-muted">—</span>
          </td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary me-1"
                    @click="onEditClick(item)"
                    data-bs-toggle="modal" data-bs-target="#editItemModal">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="modal fade" id="editItemModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
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
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdate">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>