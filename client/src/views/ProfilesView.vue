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
  users, selectedUserId, isSuperuser, fetchUsers, fetchData, fetchStats
} = useCrud('/api/profile/');

const profileToEdit = ref({});

const ROLES = [
  { value: 0, label: 'Не определена' },
  { value: 1, label: 'Методист' },
  { value: 2, label: 'Завуч' },
  { value: 3, label: 'Учитель' },
];

function onProfileEditClick(item) {
  profileToEdit.value = { ...item };
}

async function onUpdateProfile() {
  await axios.put(`/api/profile/${profileToEdit.value.id}/`, {
    last_name: profileToEdit.value.last_name || '',
    first_name: profileToEdit.value.first_name || '',
    patronymic_name: profileToEdit.value.patronymic_name || '',
    role: profileToEdit.value.role,
  });
  await fetchData(currentPage.value);
  await fetchStats();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchData(1);
  await fetchStats();
});
</script>

<template>
  <CrudPage
    title="Профили"
    icon="bi-person-circle"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    :stats="stats"
    :show-filter="false"
    @update:selected-user-id="selectedUserId = $event"
    @update:current-page="currentPage = $event"
  >
    <template #form></template>

    <template #content>
      <div class="card shadow-sm border-0 overflow-hidden">
        <table class="table table-hover align-middle mb-0 bg-white">
          <thead class="table-light sticky-top">
            <tr>
              <th>Логин</th>
              <th>ФИО</th>
              <th>Роль</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold text-primary">{{ item.username }}</td>
              <td>{{ item.user_display }}</td>
              <td>
                <span class="badge rounded-pill" :class="item.role === 1 ? 'text-bg-success' : item.role === 2 ? 'text-bg-warning' : item.role === 3 ? 'text-bg-info' : 'text-bg-secondary'">
                  {{ item.role_display }}
                </span>
              </td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary" @click="onProfileEditClick(item)" data-bs-toggle="modal" data-bs-target="#editProfileModal">
                  <i class="bi bi-pencil"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template #modals>
      <div class="modal fade" id="editProfileModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-light">
              <h5 class="modal-title">Редактировать профиль</h5>
              <button class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Логин</label>
                <input class="form-control" :value="profileToEdit.username" disabled />
              </div>
              <div class="mb-3">
                <label class="form-label">Фамилия</label>
                <input class="form-control" v-model="profileToEdit.last_name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Имя</label>
                <input class="form-control" v-model="profileToEdit.first_name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Отчество</label>
                <input class="form-control" v-model="profileToEdit.patronymic_name" />
              </div>
              <div class="mb-3">
                <label class="form-label">Роль</label>
                <select class="form-select" v-model="profileToEdit.role">
                  <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
                </select>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
              <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateProfile">Сохранить</button>
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