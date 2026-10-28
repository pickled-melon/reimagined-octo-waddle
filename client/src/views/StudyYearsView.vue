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
} = useCrud('/api/study-years/');

const studyYearToAdd = ref({});
const studyYearToEdit = ref({});

async function onStudyYearAdd() {
  await axios.post('/api/study-years/', { ...studyYearToAdd.value });
  studyYearToAdd.value = {};
  await fetchData(1);
  await fetchStats();
}

function onStudyYearEditClick(item) {
  studyYearToEdit.value = { ...item };
}

async function onUpdateStudyYear() {
  await axios.put(`/api/study-years/${studyYearToEdit.value.id}/`, {
    year: studyYearToEdit.value.year,
    max_weekly_hours: studyYearToEdit.value.max_weekly_hours,
    max_daily_hours: studyYearToEdit.value.max_daily_hours,
  });
  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteYear(item) {
  await onRemove(item.id, `Удалить ${item.year} класс?`);
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
    title="Годы обучения"
    icon="bi-calendar"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    :stats="stats"
    :stats-labels="{ avg: 'Ср. часов/нед', max: 'Макс. часов/нед', min: 'Мин. часов/нед' }"
    @update:selected-user-id="selectedUserId = $event"
    @update:current-page="currentPage = $event"
  >
    <template #form>
      <div class="card shadow-sm mb-3 border-0">
        <div class="card-header bg-white border-bottom-0 pt-3">
          <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить год
        </div>
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
              <th>В неделю</th>
              <th>В день</th>
              <th>Автор</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold">{{ item.year }} класс</td>
              <td>{{ item.max_weekly_hours }}</td>
              <td>{{ item.max_daily_hours }}</td>
              <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" @click="onStudyYearEditClick(item)" data-bs-toggle="modal" data-bs-target="#editStudyYearModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteYear(item)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template #modals>
      <div class="modal fade" id="editStudyYearModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-light">
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
            <div class="modal-footer bg-light">
              <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
              <button class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateStudyYear">Сохранить</button>
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