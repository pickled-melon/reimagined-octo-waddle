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

const subjectPictureRef = ref();
const subjectAddImageUrl = ref();

const subjectEditPictureRef = ref();
const subjectEditImageUrl = ref();

const subjectModalPictureUrl = ref('');

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

function subjectAddPictureChange() {
  subjectAddImageUrl.value = URL.createObjectURL(subjectPictureRef.value.files[0]);
}

function subjectEditPictureChange() {
  if (subjectEditPictureRef.value.files.length === 0) {
    subjectEditImageUrl.value = '';
    return;
  }
  subjectEditImageUrl.value = URL.createObjectURL(subjectEditPictureRef.value.files[0]);
}

async function onSubjectAdd() {
  const formData = new FormData();

  if (subjectPictureRef.value && subjectPictureRef.value.files.length > 0) {
    formData.append('picture', subjectPictureRef.value.files[0]);
  }
  formData.set('title', subjectToAdd.value.title);
  formData.set('type', subjectToAdd.value.type || 'classroom');

  const selected = subjectToAdd.value.classrooms || [];
  for (const id of selected) {
    formData.append('classrooms', id);
  }

  await axios.post('/api/subjects/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  subjectToAdd.value = { classrooms: [] };
  subjectAddImageUrl.value = '';
  if (subjectPictureRef.value) subjectPictureRef.value.value = '';
  await fetchSubjects();
}

function onSubjectEditClick(subject) {
  subjectToEdit.value = {
    ...subject,
    classrooms: [...(subject.classrooms || [])]
  };
  subjectEditImageUrl.value = '';
  if (subjectEditPictureRef.value) subjectEditPictureRef.value.value = '';
}

async function onUpdateSubject() {
  const formData = new FormData();
  formData.set('title', subjectToEdit.value.title);
  formData.set('type', subjectToEdit.value.type);

  const selected = subjectToEdit.value.classrooms || [];
  for (const id of selected) {
    formData.append('classrooms', id);
  }

  if (subjectEditPictureRef.value && subjectEditPictureRef.value.files.length > 0) {
    formData.append('picture', subjectEditPictureRef.value.files[0]);
  }

  await axios.put(`/api/subjects/${subjectToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  await fetchSubjects();
}

async function onRemoveClick(subject) {
  if (!confirm(`Удалить дисциплину "${subject.title}"?`)) return;
  await axios.delete(`/api/subjects/${subject.id}/`);
  await fetchSubjects();
}

function onShowPicture(url) {
  subjectModalPictureUrl.value = url;
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
            <div class="col-md-3">
              <label class="form-label">Название</label>
              <input class="form-control" v-model="subjectToAdd.title" required />
            </div>
            <div class="col-md-2">
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
              <label class="form-label">Картинка</label>
              <input
                class="form-control"
                type="file"
                ref="subjectPictureRef"
                @change="subjectAddPictureChange"
              />
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100">Добавить</button>
            </div>
            <div v-if="subjectAddImageUrl" class="col-md-2">
              <img :src="subjectAddImageUrl" style="max-height: 60px;" alt="">
            </div>
          </div>
        </form>
      </div>
    </div>

    <table class="table table-striped bg-white">
      <thead>
        <tr>
          <th>Название</th>
          <th>Тип</th>
          <th>Картинка</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in subjects" :key="item.id">
          <td>{{ item.title }}</td>
          <td>{{ item.type_display }}</td>
          <td>
            <img
              v-if="item.picture"
              :src="item.picture"
              style="max-height: 60px; cursor: pointer;"
              alt=""
              data-bs-toggle="modal"
              data-bs-target="#subjectPictureModal"
              @click="onShowPicture(item.picture)"
            >
          </td>
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
            <div class="mb-3">
              <label class="form-label">Картинка</label>
              <input
                class="form-control"
                type="file"
                ref="subjectEditPictureRef"
                @change="subjectEditPictureChange"
              />
            </div>
            <div v-if="subjectEditImageUrl" class="mb-3">
              <img :src="subjectEditImageUrl" style="max-height: 60px;" alt="">
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateSubject">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="subjectPictureModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Изображение</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="subjectModalPictureUrl" style="max-width: 100%;" alt="">
          </div>
        </div>
      </div>
    </div>

  </div>
</template>