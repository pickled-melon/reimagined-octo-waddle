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
} = useCrud('/api/bell-schedules/');

const bellToAdd = ref({});
const bellToEdit = ref({});

async function onBellAdd() {
  await axios.post('/api/bell-schedules/', { ...bellToAdd.value });
  bellToAdd.value = {};
  await fetchData(1);
  await fetchStats();
}

function onBellEditClick(item) {
  bellToEdit.value = { ...item };
}

async function onUpdateBell() {
  await axios.put(`/api/bell-schedules/${bellToEdit.value.id}/`, {
    lesson_number: bellToEdit.value.lesson_number,
    start_time: bellToEdit.value.start_time,
    end_time: bellToEdit.value.end_time,
  });
  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteBell(item) {
  await onRemove(item.id, `Удалить ${item.lesson_number}-й урок?`);
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
    title="Расписание звонков"
    icon="bi-clock"
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
          <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить звонок
        </div>
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
              <th>№</th>
              <th>Начало</th>
              <th>Конец</th>
              <th>Автор</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold">{{ item.lesson_number }}</td>
              <td>{{ item.start_time }}</td>
              <td>{{ item.end_time }}</td>
              <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" @click="onBellEditClick(item)" data-bs-toggle="modal" data-bs-target="#editBellModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteBell(item)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template #modals>
      <div class="modal fade" id="editBellModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-light">
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
            <div class="modal-footer bg-light">
              <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
              <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateBell">Сохранить</button>
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