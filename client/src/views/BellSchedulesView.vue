<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const bells = ref([]);
const bellToAdd = ref({});
const bellToEdit = ref({});

async function fetchBells() {
  const r = await axios.get('/api/bell-schedules/');
  bells.value = r.data;
}

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
    ...bellToEdit.value,
  });
  await fetchBells();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить ${item.lesson_number}-й урок?`)) return;
  await axios.delete(`/api/bell-schedules/${item.id}/`);
  await fetchBells();
}

onBeforeMount(fetchBells);
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-clock me-2"></i>Расписание звонков</h1>
      <span class="badge text-bg-secondary">Всего: {{ bells.length }}</span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">Добавить звонок</div>
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
              <button class="btn btn-primary w-100">Добавить</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead><tr><th>№</th><th>Начало</th><th>Конец</th><th></th></tr></thead>
      <tbody>
        <tr v-for="item in bells" :key="item.id">
          <td>{{ item.lesson_number }}</td>
          <td>{{ item.start_time }}</td>
          <td>{{ item.end_time }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary me-1"
                    @click="onBellEditClick(item)"
                    data-bs-toggle="modal" data-bs-target="#editBellModal">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="modal fade" id="editBellModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
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
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateBell">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>