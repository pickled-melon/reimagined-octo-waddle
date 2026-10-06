<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const subjects = ref([]);
const classrooms = ref([]);
const subjectToAdd = ref({ classrooms: [] });
const subjectToEdit = ref({ classrooms: [] });

const SUBJECT_TYPES = [
  { value: 'classroom', label: 'Классно-урочный' },
  { value: 'extracurricular', label: 'Внеурочный' },
];

async function fetchSubjects() {
  const r = await axios.get('/api/subjects/');
  subjects.value = r.data;
}

async function fetchClassrooms() {
  const r = await axios.get('/api/classrooms/');
  classrooms.value = r.data;
}

async function onSubjectAdd() {
  await axios.post('/api/subjects/', { ...subjectToAdd.value });
  subjectToAdd.value = { classrooms: [] };
  await fetchSubjects();
}

function onSubjectEditClick(subject) {
  subjectToEdit.value = { ...subject, classrooms: [...subject.classrooms] };
}

async function onUpdateSubject() {
  await axios.put(`/api/subjects/${subjectToEdit.value.id}/`, {
    ...subjectToEdit.value,
  });
  await fetchSubjects();
}

async function onRemoveClick(subject) {
  if (!confirm(`Удалить дисциплину "${subject.title}"?`)) return;
  await axios.delete(`/api/subjects/${subject.id}/`);
  await fetchSubjects();
}

onBeforeMount(async () => {
  await fetchClassrooms();
  await fetchSubjects();
});
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0"><i class="bi bi-book me-2"></i>Дисциплины</h1>
      <span class="badge text-bg-secondary">Всего: {{ subjects.length }}</span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">Добавить дисциплину</div>
      <div class="card-body">
        <form @submit.prevent="onSubjectAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">Название</label>
              <input class="form-control" v-model="subjectToAdd.title" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Тип</label>
              <select class="form-select" v-model="subjectToAdd.type">
                <option v-for="t in SUBJECT_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Требуемые кабинеты</label>
              <select class="form-select" multiple v-model="subjectToAdd.classrooms">
                <option v-for="c in classrooms" :key="c.id" :value="c.id">{{ c.number }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100">Добавить</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead><tr><th>Название</th><th>Тип</th><th></th></tr></thead>
      <tbody>
        <tr v-for="item in subjects" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ item.type }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary me-1"
                    @click="onSubjectEditClick(item)"
                    data-bs-toggle="modal" data-bs-target="#editSubjectModal">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="modal fade" id="editSubjectModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать дисциплину</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название</label>
              <input class="form-control" v-model="subjectToEdit.title" />
            </div>
            <div class="mb-3">
              <label class="form-label">Тип</label>
              <select class="form-select" v-model="subjectToEdit.type">
                <option v-for="t in SUBJECT_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Требуемые кабинеты</label>
              <select class="form-select" multiple v-model="subjectToEdit.classrooms">
                <option v-for="c in classrooms" :key="c.id" :value="c.id">{{ c.number }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateSubject">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>