<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const items = ref([]);
const subjects = ref([]);
const studyYears = ref([]);
const itemToAdd = ref({});
const itemToEdit = ref({});

async function fetchItems() {
  const r = await axios.get('/api/difficulties/');
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
    ...itemToEdit.value,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm('Удалить запись?')) return;
  await axios.delete(`/api/difficulties/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchStudyYears();
  await fetchSubjects();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-bar-chart me-2"></i>Трудности</h1>
      <span class="badge text-bg-secondary">Всего: {{ items.length }}</span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">Добавить</div>
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
              <button class="btn btn-primary w-100">Добавить</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead><tr><th>Год</th><th>Дисциплина</th><th>Баллы</th><th></th></tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.study_year }}</td>
          <td>{{ item.subject }}</td>
          <td>{{ item.points }}</td>
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
            <h5 class="modal-title">Редактировать</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <label class="form-label">Баллы</label>
            <input type="number" class="form-control" v-model="itemToEdit.points" />
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