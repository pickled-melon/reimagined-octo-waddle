<script setup>
import axios from 'axios';
import { onBeforeMount, ref } from 'vue';
import Cookies from 'js-cookie';

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
});

const loading = ref(false);
const classrooms = ref([]);
const classroomToEdit = ref({});
const classroomToAdd = ref({});

async function fetchClassrooms() {
  loading.value = true;
  const r = await axios.get("/api/classrooms/");
  classrooms.value = r.data;
  loading.value = false;
}

async function onRemoveClick(classroom) {
  if (!confirm(`Удалить кабинет ${classroom.number}?`)) return;
  await axios.delete(`/api/classrooms/${classroom.id}/`);
  await fetchClassrooms();
}

async function onClassroomAdd() {
  await axios.post("/api/classrooms/", { ...classroomToAdd.value });
  classroomToAdd.value = {};
  await fetchClassrooms();
}

function onClassroomEditClick(classroom) {
  classroomToEdit.value = { ...classroom };
}

async function onUpdateClassroom() {
  await axios.put(`/api/classrooms/${classroomToEdit.value.id}/`, {
    ...classroomToEdit.value,
  });
  await fetchClassrooms();
}

onBeforeMount(async () => {
  await fetchClassrooms();
});
</script>

<template>
  <div class="container py-4">

    <div class="d-flex align-items-center justify-content-between mb-4">
      <h1 class="h3 mb-0">
        <i class="bi bi-door-open me-2"></i>Кабинеты
      </h1>
      <span class="badge text-bg-secondary">
        Всего: {{ classrooms.length }}
      </span>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white">
        <i class="bi bi-plus-circle me-2"></i>Добавить кабинет
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onClassroomAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label">Номер</label>
              <input
                type="text"
                class="form-control"
                v-model="classroomToAdd.number"
                placeholder="Например, 101"
                required
              />
            </div>
            <div class="col-md-5">
              <label class="form-label">Вместимость</label>
              <input
                type="number"
                class="form-control"
                v-model="classroomToAdd.capacity"
                placeholder="Например, 30"
                min="1"
                required
              />
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100">
                <i class="bi bi-plus-lg me-1"></i>Добавить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <div v-else-if="classrooms.length === 0" class="alert alert-info">
      <i class="bi bi-info-circle me-2"></i>Список кабинетов пуст.
    </div>

    <div v-else class="row g-3">
      <div
        v-for="item in classrooms"
        :key="item.id"
        class="col-sm-6 col-md-4 col-lg-3"
      >
        <div class="card h-100 classroom-card">
          <div class="card-body d-flex align-items-start justify-content-between">
            <div>
              <div class="fs-5 fw-semibold">
                <i class="bi bi-door-closed me-2 text-primary"></i>{{ item.number }}
              </div>
              <div class="text-muted small mt-1">
                <i class="bi bi-people me-1"></i>до {{ item.capacity }} чел.
              </div>
            </div>
          </div>
          <div class="card-footer bg-white d-flex justify-content-end gap-2">
            <button
              class="btn btn-sm btn-outline-primary"
              @click="onClassroomEditClick(item)"
              data-bs-toggle="modal"
              data-bs-target="#editClassroomModal"
              title="Редактировать"
            >
              <i class="bi bi-pencil"></i>
            </button>
            <button
              class="btn btn-sm btn-outline-danger"
              @click="onRemoveClick(item)"
              title="Удалить"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editClassroomModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-pencil-square me-2"></i>Редактировать кабинет
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
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
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
              Отмена
            </button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="onUpdateClassroom"
            >
              <i class="bi bi-check-lg me-1"></i>Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.classroom-card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.classroom-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
}
</style>