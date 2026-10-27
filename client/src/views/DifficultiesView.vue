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
} = useCrud('/api/difficulties/');

const subjects = ref([]);
const studyYears = ref([]);
const itemToAdd = ref({});
const itemToEdit = ref({});

async function fetchSubjects() {
  const r = await axios.get('/api/subjects/?page_size=1000');
  subjects.value = r.data.results;
}

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/?page_size=1000');
  studyYears.value = r.data.results;
}

async function onAdd() {
  await axios.post('/api/difficulties/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchData(1);
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/difficulties/${itemToEdit.value.id}/`, {
    study_year: itemToEdit.value.study_year,
    subject: itemToEdit.value.subject,
    points: itemToEdit.value.points,
  });
  await fetchData(currentPage.value);
}

function onDeleteDifficulty(item) {
  onRemove(item.id, `Удалить "${item.subject_display} — ${item.study_year_display} класс"?`);
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
  await fetchSubjects();
  await fetchData(1);
});
</script>

<template>
  <CrudPage
    title="Трудности"
    icon="bi-bar-chart"
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
          <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить
        </div>
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
              <th>Год</th>
              <th>Дисциплина</th>
              <th>Баллы</th>
              <th>Автор</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold">{{ item.study_year_display }} класс</td>
              <td>{{ item.subject_display }}</td>
              <td>{{ item.points }}</td>
              <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" @click="onEditClick(item)" data-bs-toggle="modal" data-bs-target="#editItemModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteDifficulty(item)">
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
              <h5 class="modal-title">Редактировать</h5>
              <button class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Год обучения</label>
                <select class="form-select" v-model="itemToEdit.study_year">
                  <option v-for="y in studyYears" :key="y.id" :value="y.id">{{ y.year }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Дисциплина</label>
                <select class="form-select" v-model="itemToEdit.subject">
                  <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Баллы</label>
                <input type="number" class="form-control" v-model="itemToEdit.points" />
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