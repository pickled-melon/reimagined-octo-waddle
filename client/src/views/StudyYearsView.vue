<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const studyYears = ref([]);
const studyYearToAdd = ref({});
const studyYearToEdit = ref({});

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/');
  studyYears.value = r.data;
}

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
    ...studyYearToEdit.value,
  });
  await fetchStudyYears();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить ${item.year} класс?`)) return;
  await axios.delete(`/api/study-years/${item.id}/`);
  await fetchStudyYears();
}

onBeforeMount(fetchStudyYears);
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-calendar me-2"></i>Годы обучения</h1>
      <span class="badge text-bg-secondary">Всего: {{ studyYears.length }}</span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">Добавить год</div>
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
              <button class="btn btn-primary w-100">Добавить</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead><tr><th>Год</th><th>В неделю</th><th>В день</th><th></th></tr></thead>
      <tbody>
        <tr v-for="item in studyYears" :key="item.id">
          <td>{{ item.year }}</td>
          <td>{{ item.max_weekly_hours }}</td>
          <td>{{ item.max_daily_hours }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary me-1"
                    @click="onStudyYearEditClick(item)"
                    data-bs-toggle="modal" data-bs-target="#editStudyYearModal">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="modal fade" id="editStudyYearModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
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
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateStudyYear">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>