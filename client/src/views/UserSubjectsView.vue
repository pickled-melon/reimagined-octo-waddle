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
} = useCrud('/api/user-subjects/');

const subjects = ref([]);
const profiles = ref([]);
const itemToAdd = ref({});
const itemToEdit = ref({});

function teacherLabel(profile) {
  return profile.user_display || profile.user;
}

async function fetchSubjects() {
  const r = await axios.get('/api/subjects/?page_size=1000');
  subjects.value = r.data.results;
}

async function fetchProfiles() {
  const r = await axios.get('/api/profile/?page_size=1000');
  profiles.value = r.data.results;
}

async function onAdd() {
  await axios.post('/api/user-subjects/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchData(1);
  await fetchStats();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/user-subjects/${itemToEdit.value.id}/`, {
    user: itemToEdit.value.user,
    subject: itemToEdit.value.subject,
  });
  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteUserSubject(item) {
  await onRemove(item.id, `Удалить "${item.user_display} — ${item.subject_display}"?`);
  await fetchStats();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchProfiles();
  await fetchSubjects();
  await fetchData(1);
  await fetchStats();
});
</script>

<template>
  <CrudPage
    title="Дисциплины учителей"
    icon="bi-person-badge"
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
          <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить
        </div>
        <div class="card-body">
          <form @submit.prevent="onAdd">
            <div class="row g-3 align-items-end">
              <div class="col-md-5">
                <label class="form-label">Учитель</label>
                <select class="form-select" v-model="itemToAdd.user" required>
                  <option v-for="p in profiles" :key="p.id" :value="p.user">{{ teacherLabel(p) }}</option>
                </select>
              </div>
              <div class="col-md-5">
                <label class="form-label">Дисциплина</label>
                <select class="form-select" v-model="itemToAdd.subject" required>
                  <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
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
              <th>Учитель</th>
              <th>Дисциплина</th>
              <th>Автор записи</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold">{{ item.user_display }}</td>
              <td>{{ item.subject_display }}</td>
              <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.creator_display }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" @click="onEditClick(item)" data-bs-toggle="modal" data-bs-target="#editItemModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteUserSubject(item)">
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
                <label class="form-label">Учитель</label>
                <select class="form-select" v-model="itemToEdit.user">
                  <option v-for="p in profiles" :key="p.id" :value="p.user">{{ teacherLabel(p) }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Дисциплина</label>
                <select class="form-select" v-model="itemToEdit.subject">
                  <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.title }}</option>
                </select>
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