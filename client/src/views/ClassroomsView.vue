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
  items, totalCount, currentPage, pageSize, loading, stats,
  users, selectedUserId, isSuperuser, fetchUsers, fetchData, fetchStats, onRemove
} = useCrud('/api/classrooms/');

const WEEK_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

const classroomToEdit = ref({});
const classroomToAdd = ref({});

const classroomPictureRef = ref();
const classroomAddImageUrl = ref();
const classroomEditPictureRef = ref();
const classroomEditImageUrl = ref();
const classroomModalPictureUrl = ref('');

function classroomAddPictureChange() {
  classroomAddImageUrl.value = URL.createObjectURL(classroomPictureRef.value.files[0]);
}

function classroomEditPictureChange() {
  if (classroomEditPictureRef.value.files.length === 0) {
    classroomEditImageUrl.value = '';
    return;
  }
  classroomEditImageUrl.value = URL.createObjectURL(classroomEditPictureRef.value.files[0]);
}

async function onClassroomAdd() {
  const formData = new FormData();
  if (classroomPictureRef.value && classroomPictureRef.value.files.length > 0) {
    formData.append('picture', classroomPictureRef.value.files[0]);
  }
  formData.set('number', classroomToAdd.value.number);
  formData.set('capacity', classroomToAdd.value.capacity);

  await axios.post("/api/classrooms/", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  classroomToAdd.value = {};
  classroomAddImageUrl.value = '';
  if (classroomPictureRef.value) classroomPictureRef.value.value = '';
  await fetchData(1);
  await fetchStats();
}

function onClassroomEditClick(classroom) {
  classroomToEdit.value = { ...classroom };
  classroomEditImageUrl.value = '';
  if (classroomEditPictureRef.value) classroomEditPictureRef.value.value = '';
}

async function onUpdateClassroom() {
  const formData = new FormData();
  formData.set('number', classroomToEdit.value.number);
  formData.set('capacity', classroomToEdit.value.capacity);

  if (classroomEditPictureRef.value && classroomEditPictureRef.value.files.length > 0) {
    formData.append('picture', classroomEditPictureRef.value.files[0]);
  }

  await axios.put(`/api/classrooms/${classroomToEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  await fetchData(currentPage.value);
  await fetchStats();
}

async function onDeleteClassroom(item) {
  await onRemove(item.id, `Удалить кабинет ${item.number}?`);
  await fetchStats();
}

function onShowPicture(url) {
  classroomModalPictureUrl.value = url;
}

function dailyValue(item, day) {
  if (!item.daily_load) return 0;
  return item.daily_load[String(day)] || 0;
}

function weekMax(item) {
  let m = 0;
  for (let d = 1; d <= 6; d++) {
    const v = dailyValue(item, d);
    if (v > m) m = v;
  }
  return m || 1;
}

function dayBarHeight(item, day) {
  const v = dailyValue(item, day);
  if (v === 0) return 3;
  return Math.max(3, Math.round((v / weekMax(item)) * 28));
}

function dayBarClass(item, day) {
  const v = dailyValue(item, day);
  if (v === 0) return 'bg-secondary-subtle';
  const max = weekMax(item);
  if (v >= max) return 'bg-danger';
  if (v >= max / 2) return 'bg-warning';
  return 'bg-primary';
}

function dayTitle(item, day) {
  return `${WEEK_LABELS[day - 1]}: ${dailyValue(item, day)} ур.`;
}

function utilizationBarClass(percent) {
  const num = Number(percent);
  if (isNaN(num)) return 'bg-secondary';
  if (num >= 85) return 'bg-danger';
  if (num >= 60) return 'bg-warning';
  if (num > 0) return 'bg-success';
  return 'bg-secondary';
}

function utilizationWidth(percent) {
  const num = Number(percent);
  if (isNaN(num)) return '0%';
  return Math.min(num, 100) + '%';
}

onBeforeMount(async () => {
  await fetchUsers();
  await fetchData(1);
  await fetchStats();
});
</script>

<template>
  <CrudPage
    title="Кабинеты"
    icon="bi-door-open"
    :total-count="totalCount"
    :current-page="currentPage"
    :page-size="pageSize"
    :users="users"
    :selected-user-id="selectedUserId"
    :is-superuser="isSuperuser"
    :stats="stats"
    :stats-labels="{ avg: 'Ср. вместимость', max: 'Макс. вместимость', min: 'Мин. вместимость' }"
    @update:selected-user-id="selectedUserId = $event"
    @update:current-page="currentPage = $event"
  >
    <template #form>
      <div class="card shadow-sm mb-3 border-0">
        <div class="card-header bg-white border-bottom-0 pt-3">
          <i class="bi bi-plus-circle me-2 text-primary"></i>Добавить кабинет
        </div>
        <div class="card-body">
          <form @submit.prevent.stop="onClassroomAdd">
            <div class="row g-3 align-items-end">
              <div class="col-md-4">
                <label class="form-label">Номер</label>
                <input type="text" class="form-control" v-model="classroomToAdd.number" required />
              </div>
              <div class="col-md-4">
                <label class="form-label">Вместимость</label>
                <input type="number" class="form-control" v-model="classroomToAdd.capacity" min="1" required />
              </div>
              <div class="col-md-2">
                <label class="form-label">Картинка</label>
                <input class="form-control" type="file" ref="classroomPictureRef" @change="classroomAddPictureChange" />
              </div>
              <div class="col-md-2">
                <button class="btn btn-primary w-100"><i class="bi bi-plus-lg me-1"></i>Добавить</button>
              </div>
              <div v-if="classroomAddImageUrl" class="col-md-2">
                <img :src="classroomAddImageUrl" class="rounded shadow-sm" style="max-height: 60px;" alt="">
              </div>
            </div>
          </form>
        </div>
      </div>
    </template>

    <template #content>
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      <div v-else-if="items.length === 0" class="alert alert-info shadow-sm border-0">
        Кабинетов не найдено.
      </div>
      <div v-else class="row g-3 pb-3">
        <div v-for="item in items" :key="item.id" class="col-sm-6 col-md-4 col-xl-3">
          <div class="card h-100 classroom-card border-0">
            <div class="card-body d-flex flex-column">
              <div class="d-flex align-items-start justify-content-between mb-2">
                <div>
                  <div class="fs-5 fw-semibold">
                    <i class="bi bi-door-closed me-2 text-primary"></i>{{ item.number }}
                  </div>
                  <div class="text-muted small mt-1">
                    <i class="bi bi-people me-1"></i>до {{ item.capacity }} чел.
                  </div>
                  <div class="text-muted small mt-1" v-if="item.user_display">
                    <i class="bi bi-person-circle me-1"></i>{{ item.user_display }}
                  </div>
                </div>
                <div v-if="item.picture">
                  <img :src="item.picture" class="rounded shadow-sm" style="max-height: 60px; cursor: pointer;" alt="" data-bs-toggle="modal" data-bs-target="#classroomPictureModal" @click="onShowPicture(item.picture)">
                </div>
              </div>

              <div class="small mb-1 d-flex justify-content-between">
                <span class="text-muted"><i class="bi bi-calendar-week me-1"></i>Уроков в неделю</span>
                <strong>{{ item.weekly_lessons }}</strong>
              </div>
              <div class="small mb-1 d-flex justify-content-between">
                <span class="text-muted"><i class="bi bi-speedometer2 me-1"></i>Использование</span>
                <strong>{{ item.utilization_percent }}%</strong>
              </div>
              <div class="progress mb-2" style="height: 4px;">
                <div class="progress-bar" :class="utilizationBarClass(item.utilization_percent)" :style="{ width: utilizationWidth(item.utilization_percent) }"></div>
              </div>

              <div class="d-flex justify-content-between small text-muted mb-1">
                <span><i class="bi bi-person-badge me-1"></i>Учителей: <strong class="text-dark">{{ item.teachers_count }}</strong></span>
                <span><i class="bi bi-people me-1"></i>Групп: <strong class="text-dark">{{ item.groups_count }}</strong></span>
              </div>
              <div class="small text-muted mb-2">
                <i class="bi bi-book me-1"></i>Предметов: <strong class="text-dark">{{ item.subjects_count }}</strong>
              </div>

              <div class="week-load mt-auto d-flex justify-content-between align-items-end gap-1 pt-2 border-top">
                <div v-for="(label, i) in WEEK_LABELS" :key="i" class="flex-grow-1 d-flex flex-column align-items-center gap-1">
                  <div class="day-bar rounded-1" :class="dayBarClass(item, i + 1)" :style="{ height: dayBarHeight(item, i + 1) + 'px' }" :title="dayTitle(item, i + 1)"></div>
                  <small class="text-muted" style="font-size: 0.65rem;">{{ label }}</small>
                </div>
              </div>
            </div>
            <div class="card-footer bg-white border-top-0 d-flex justify-content-end gap-2 pb-3">
              <button class="btn btn-sm btn-outline-primary" @click="onClassroomEditClick(item)" data-bs-toggle="modal" data-bs-target="#editClassroomModal">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="onDeleteClassroom(item)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #modals>
      <div class="modal fade" id="editClassroomModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-light">
              <h5 class="modal-title">Редактировать кабинет</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Номер</label>
                  <input type="text" class="form-control" v-model="classroomToEdit.number" />
                </div>
                <div class="col-12">
                  <label class="form-label">Вместимость</label>
                  <input type="number" class="form-control" v-model="classroomToEdit.capacity" min="1" />
                </div>
                <div class="col-12">
                  <label class="form-label">Картинка</label>
                  <input class="form-control" type="file" ref="classroomEditPictureRef" @change="classroomEditPictureChange" />
                </div>
                <div v-if="classroomEditImageUrl" class="col-12">
                  <img :src="classroomEditImageUrl" class="rounded shadow-sm" style="max-height: 60px;" alt="">
                </div>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
              <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateClassroom">Сохранить</button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal fade" id="classroomPictureModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header border-0">
              <h5 class="modal-title">Просмотр</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center pb-4">
              <img :src="classroomModalPictureUrl" class="img-fluid rounded" style="max-height: 75vh;" alt="">
            </div>
          </div>
        </div>
      </div>
    </template>
  </CrudPage>
</template>

<style scoped>
.classroom-card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.classroom-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.15);
}
.day-bar {
  width: 100%;
  min-height: 3px;
  transition: height 0.2s ease;
}
</style>