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

const subjects = ref([]);
const classrooms = ref([]);
const users = ref([]);
const selectedUserId = ref("");

const subjectToAdd = ref({ classrooms: [] });
const subjectToEdit = ref({ classrooms: [] });

const albumPictureRef = ref();
const albumAddImagesUrls = ref([]);
const albumSubject = ref({});
const albumPictures = ref([]);
const viewPictureUrl = ref('');

const SUBJECT_TYPES = [
  { value: 'classroom', label: 'Классно-урочный' },
  { value: 'extracurricular', label: 'Внеурочный' },
];

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchSubjects() {
  let url = '/api/subjects/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  subjects.value = r.data;
}

async function fetchClassrooms() {
  const r = await axios.get('/api/classrooms/');
  classrooms.value = r.data;
}

watch(selectedUserId, () => {
  fetchSubjects();
});

async function onSubjectAdd() {
  const formData = new FormData();
  formData.set('title', subjectToAdd.value.title);
  formData.set('type', subjectToAdd.value.type || 'classroom');

  const selected = subjectToAdd.value.classrooms || [];
  for (const id of selected) {
    formData.append('classrooms', id);
  }

  await axios.post('/api/subjects/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  subjectToAdd.value = { classrooms: [] };
  await fetchSubjects();
}

function onSubjectEditClick(subject) {
  subjectToEdit.value = { ...subject, classrooms: [...(subject.classrooms || [])] };
}

async function onUpdateSubject() {
  const formData = new FormData();
  formData.set('title', subjectToEdit.value.title);
  formData.set('type', subjectToEdit.value.type);

  const selected = subjectToEdit.value.classrooms || [];
  for (const id of selected) {
    formData.append('classrooms', id);
  }

  await axios.put(`/api/subjects/${subjectToEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  await fetchSubjects();
}

async function onRemoveClick(subject) {
  if (!confirm(`Удалить дисциплину "${subject.title}"?`)) return;
  await axios.delete(`/api/subjects/${subject.id}/`);
  await fetchSubjects();
}

function onAlbumEditClick(subject) {
  albumSubject.value = { ...subject };
  albumPictures.value = subject.pictures ? [...subject.pictures] : [];
  albumAddImagesUrls.value = [];
  if (albumPictureRef.value) albumPictureRef.value.value = '';
}

function albumAddPicturesChange() {
  albumAddImagesUrls.value = [];
  const files = albumPictureRef.value.files;
  for (let i = 0; i < files.length; i++) {
    albumAddImagesUrls.value.push(URL.createObjectURL(files[i]));
  }
}

async function onAlbumUpload() {
  const files = albumPictureRef.value.files;
  for (let i = 0; i < files.length; i++) {
    const formData = new FormData();
    formData.append('image', files[i]);
    formData.set('subject', albumSubject.value.id);

    await axios.post('/api/subject-pictures/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
  albumPictureRef.value.value = '';
  albumAddImagesUrls.value = [];

  await fetchSubjects();
  const updated = subjects.value.find(s => s.id === albumSubject.value.id);
  albumPictures.value = updated && updated.pictures ? [...updated.pictures] : [];
}

async function onAlbumRemovePicture(picture) {
  if (!confirm('Удалить фотографию из альбома?')) return;
  await axios.delete(`/api/subject-pictures/${picture.id}/`);
  await fetchSubjects();
  albumPictures.value = albumPictures.value.filter(p => p.id !== picture.id);
}

function onShowPicture(url) {
  viewPictureUrl.value = url;
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchClassrooms();
  await fetchSubjects();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-book me-2"></i>Дисциплины</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ subjects.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-white border-bottom-0 pt-3">
        <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить дисциплину
      </div>
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
            <th>Название</th>
            <th>Тип</th>
            <th>Автор</th>
            <th>Альбом</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in subjects" :key="item.id">
            <td class="fw-semibold">{{ item.title }}</td>
            <td>
              <span class="badge rounded-pill" :class="item.type === 'classroom' ? 'text-bg-info' : 'text-bg-warning'">
                {{ item.type_display }}
              </span>
            </td>
            <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
            <td>
              <div v-if="item.pictures && item.pictures.length" class="d-flex gap-1 flex-wrap">
                <img v-for="pic in item.pictures" :key="pic.id" :src="pic.image" class="rounded shadow-sm" style="max-height: 40px; cursor: pointer;" alt="" data-bs-toggle="modal" data-bs-target="#viewPictureModal" @click="onShowPicture(pic.image)">
              </div>
              <span v-else class="text-muted small fst-italic">Нет фото</span>
            </td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-secondary me-1" @click="onAlbumEditClick(item)" data-bs-toggle="modal" data-bs-target="#albumModal" title="Альбом">
                <i class="bi bi-images"></i>
              </button>
              <button class="btn btn-sm btn-outline-primary me-1" @click="onSubjectEditClick(item)" data-bs-toggle="modal" data-bs-target="#editSubjectModal" title="Редактировать">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)" title="Удалить">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal fade" id="editSubjectModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
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
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateSubject">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="albumModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light">
            <h5 class="modal-title"><i class="bi bi-images me-2"></i>Альбом — {{ albumSubject.title }}</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="albumPictures.length === 0" class="alert alert-info border-0">В альбоме пока нет фотографий.</div>
            <div v-else class="d-flex gap-3 flex-wrap mb-4">
              <div v-for="pic in albumPictures" :key="pic.id" class="position-relative">
                <img :src="pic.image" class="rounded shadow-sm" style="max-height: 120px; cursor: pointer;" alt="" @click="onShowPicture(pic.image)" data-bs-toggle="modal" data-bs-target="#viewPictureModal">
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 rounded-circle" @click="onAlbumRemovePicture(pic)">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
            <hr>
            <label class="form-label fw-semibold">Добавить фотографии</label>
            <input class="form-control mb-2" type="file" accept="image/*" multiple ref="albumPictureRef" @change="albumAddPicturesChange" />
            <div v-if="albumAddImagesUrls.length" class="d-flex gap-2 flex-wrap mt-3">
              <img v-for="(url, i) in albumAddImagesUrls" :key="i" :src="url" class="rounded shadow-sm" style="max-height: 80px;" alt="">
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button class="btn btn-primary" @click="onAlbumUpload" :disabled="albumAddImagesUrls.length === 0">
              <i class="bi bi-upload me-1"></i>Загрузить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="viewPictureModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header border-0">
            <h5 class="modal-title">Просмотр изображения</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-center pb-4">
            <img :src="viewPictureUrl" class="img-fluid rounded" style="max-height: 75vh;" alt="">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>