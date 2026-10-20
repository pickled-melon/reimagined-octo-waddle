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

const items = ref([]);
const studyYears = ref([]);
const users = ref([]);
const selectedUserId = ref("");
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

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchItems() {
  let url = '/api/study-groups/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  items.value = r.data;
}

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/');
  studyYears.value = r.data;
}

watch(selectedUserId, () => {
  fetchItems();
});

async function onAdd() {
  await axios.post('/api/study-groups/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchItems();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/study-groups/${itemToEdit.value.id}/`, {
    students_count: itemToEdit.value.students_count,
    letter: itemToEdit.value.letter,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить "${item.name}"?`)) return;
  await axios.delete(`/api/study-groups/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-people me-2"></i>Учебные группы</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ items.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
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

    <div class="card shadow-sm border-0 overflow-hidden">
      <table class="table table-hover align-middle mb-0 bg-white">
        <thead class="table-light">
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
              <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
  </div>
</template><script setup>
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

const items = ref([]);
const studyYears = ref([]);
const users = ref([]);
const selectedUserId = ref("");
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

async function fetchUsers() {
  if (isSuperuser.value) {
    const r = await axios.get('/api/profile/all/');
    users.value = r.data;
  }
}

async function fetchItems() {
  let url = '/api/study-groups/';
  if (isSuperuser.value && selectedUserId.value) {
    url += `?user=${selectedUserId.value}`;
  }
  const r = await axios.get(url);
  items.value = r.data;
}

async function fetchStudyYears() {
  const r = await axios.get('/api/study-years/');
  studyYears.value = r.data;
}

watch(selectedUserId, () => {
  fetchItems();
});

async function onAdd() {
  await axios.post('/api/study-groups/', { ...itemToAdd.value });
  itemToAdd.value = {};
  await fetchItems();
}

function onEditClick(item) {
  itemToEdit.value = { ...item };
}

async function onUpdate() {
  await axios.put(`/api/study-groups/${itemToEdit.value.id}/`, {
    students_count: itemToEdit.value.students_count,
    letter: itemToEdit.value.letter,
  });
  await fetchItems();
}

async function onRemoveClick(item) {
  if (!confirm(`Удалить "${item.name}"?`)) return;
  await axios.delete(`/api/study-groups/${item.id}/`);
  await fetchItems();
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchStudyYears();
  await fetchItems();
});
</script>

<template>
  <div class="container py-4">
    <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
      <h1 class="h3 mb-0"><i class="bi bi-people me-2"></i>Учебные группы</h1>
      
      <div v-if="isSuperuser" class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
        <select v-model="selectedUserId" class="form-select border-primary" style="width: 200px;">
          <option value="">Все пользователи</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
      </div>

      <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ items.length }}</span>
    </div>

    <div class="card shadow-sm mb-4 border-0">
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

    <div class="card shadow-sm border-0 overflow-hidden">
      <table class="table table-hover align-middle mb-0 bg-white">
        <thead class="table-light">
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
              <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
  </div>
</template>