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
} = useCrud('/api/study-groups/');

const studyYears = ref([]);
const itemToAdd = ref({});
const itemToEdit = ref({});

const GROUP_TYPES = [
  { value: 'group', label: 'Группа' },
  { value: 'subgroup', label: 'Подгруппа' },
];
const SUBGROUP_NUMBERS = [
  { value: 'first', label: '1' },
  { value: 'second', label: '2' },
];

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/?page_size=1000');
  studyYears.value = r.data.results;
}

async function onAdd() {
  await axios.post('/api/study-groups/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchData(1);
  await fetchStats();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/study-groups/${itemToEdit.value.id}/`, {
    students_count: itemToEdit.value.students_count,
    letter: itemToEdit.value.letter,
  });
  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteGroup(item) {
  await onRemove(item.id, `Удалить "${item.name}"?`);
  await fetchStats();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
  await fetchData(1);
  await fetchStats();
});
</script>

<template>
  <CrudPage
    title="Учебные группы"
    icon="bi-people"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    :stats="stats"
    :stats-labels="{ avg: 'Ср. учеников', max: 'Макс. учеников', min: 'Мин. учеников' }"
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
              <div class="col-md-2">
                <label class="form-label">Кол-во человек</label>
                <input type="number" class="form-control" v-model="itemToAdd.students_count" required />
              </div>
              <div class="col-md-1">
                <label class="form-label">Литера</label>
                <input class="form-control" maxlength="1" v-model="itemToAdd.letter" />
              </div>
              <div class="col-md-2">
                <label class="form-label">Тип</label>
                <select class="form-select" v-model="itemToAdd.type">
                  <option v-for="t in GROUP_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">№ подгруппы</label>
                <select class="form-select" v-model="itemToAdd.subgroup_number">
                  <option value="">—</option>
                  <option v-for="n in SUBGROUP_NUMBERS" :key="n.value" :value="n.value">{{ n.label }}</option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">Год</label>
                <select class="form-select" v-model="itemToAdd.study_year" required>
                  <option v-for="y in studyYears" :key="y.id" :value="y.id">{{ y.year }}</option>
                </select>
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
              <th>Название</th>
              <th>Человек</th>
              <th>Тип</th>
              <th>Год</th>
              <th>Автор</th>
              <th class="text-end">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="fw-semibold">{{ item.name }}</td>
              <td>{{ item.students_count }}</td>
              <td>
                <span class="badge rounded-pill" :class="item.type === 'group' ? 'text-bg-primary' : 'text-bg-secondary'">
                  {{ item.type_display }}
                </span>
              </td>
              <td>{{ item.study_year }}</td>
              <td class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ item.user_display }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" @click="onEditClick(item)" data-bs-toggle="modal" data-bs-target="#editItemModal">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onDeleteGroup(item)">
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
                <label class="form-label">Кол-во человек</label>
                <input type="number" class="form-control" v-model="itemToEdit.students_count" />
              </div>
              <div class="mb-3">
                <label class="form-label">Литера</label>
                <input class="form-control" maxlength="1" v-model="itemToEdit.letter" />
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