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
  items, totalCount, currentPage, pageSize,
  users, selectedUserId, isSuperuser, fetchUsers, fetchData, onRemove
} = useCrud('/api/subjects/');

const classrooms = ref([]);
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

async function fetchClassrooms() {
  const r = await axios.get('/api/classrooms/?page_size=1000');
  classrooms.value = r.data.results;
}

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
  await fetchData(1);
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
  await fetchData(currentPage.value);
}

function onDeleteSubject(item) {
  onRemove(item.id, `Удалить дисциплину "${item.title}"?`);
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
  await fetchData(currentPage.value);
  const updated = items.value.find(s => s.id === albumSubject.value.id);
  albumPictures.value = updated && updated.pictures ? [...updated.pictures] : [];
}

async function onAlbumRemovePicture(picture) {
  if (!confirm('Удалить фотографию из альбома?')) return;
  await axios.delete(`/api/subject-pictures/${picture.id}/`);
  await fetchData(currentPage.value);
  albumPictures.value = albumPictures.value.filter(p => p.id !== picture.id);
}

function onShowPicture(url) {
  viewPictureUrl.value = url;
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchClassrooms();
  await fetchData(1);
});
</script>

<template>
  <CrudPage
    title="Дисциплины"
    icon="bi-book"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    @update:selected-user-id="selectedUserId = $event"
    @update:current-page="currentPage = $event"
  >
    <template #form>
      <div class="card shadow-sm mb-3 border-0">
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
    </template>

    <template #content>
      <div class="card shadow-sm border-0 overflow-hidden">
        <table class="table table-hover align-middle mb-0 bg-white">
          <thead class="table-light sticky-top">
            <tr>
              <th>Название</th>
              <th>Тип</th>
              <th>Автор</th>
              <th>Альбом</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
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
                <button class="btn btn-sm btn-outline-primary me-1" @click="onSubjectEditClick(item)" data-bs-toggle="modal" data-bs-target="#editSubjectModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteSubject(item)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template #modals>
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
              <h5 class="modal-title">Просмотр</h5>
              <button class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center pb-4">
              <img :src="viewPictureUrl" class="img-fluid rounded" style="max-height: 75vh;" alt="">
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