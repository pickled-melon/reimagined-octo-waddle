<script setup>
import { RouterLink, RouterView } from 'vue-router';
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

const profileStore = useProfileStore();
const { isAuthenticated, userName } = storeToRefs(profileStore);

const links = [
  { to: '/classrooms', label: 'Кабинеты', icon: 'bi-door-open' },
  { to: '/subjects', label: 'Дисциплины', icon: 'bi-book' },
  { to: '/study-years', label: 'Годы обучения', icon: 'bi-calendar' },
  { to: '/bell-schedules', label: 'Звонки', icon: 'bi-clock' },
  { to: '/study-groups', label: 'Группы', icon: 'bi-people' },
  { to: '/user-subjects', label: 'Дисциплины учителей', icon: 'bi-person-badge' },
  { to: '/difficulties', label: 'Трудности', icon: 'bi-bar-chart' },
  { to: '/workloads', label: 'Нагрузки', icon: 'bi-list-check' },
  { to: '/lessons', label: 'Расписание', icon: 'bi-grid-3x3' },
  { to: '/profiles', label: 'Профили', icon: 'bi-person-circle' },
  { to: '/admin/', label: 'Панель админа', icon: 'bi-person-fill-gear', external: true },
];

async function onLogoutButtonClick() {
  await profileStore.logout();
}
</script>

<template>
  <div class="d-flex" style="height: 100vh; overflow: hidden;">
    <aside
      class="bg-dark text-white p-3 d-flex flex-column"
      style="width: 240px; flex-shrink: 0; height: 100%;"
    >
      <h5 class="mb-4 text-nowrap">
        <i class="bi bi-calendar-week me-2"></i>Расписание
      </h5>

      <ul
        class="nav flex-column flex-grow-1"
        style="overflow-y: auto; min-height: 0;"
      >
        <li v-for="link in links" :key="link.to" class="nav-item">
          <a
            v-if="link.external"
            :href="link.to"
            class="nav-link text-white-50"
            target="_blank"
          >
            <i :class="['bi', link.icon, 'me-2']"></i>{{ link.label }}
          </a>
          <RouterLink v-else :to="link.to" class="nav-link text-white-50">
            <i :class="['bi', link.icon, 'me-2']"></i>{{ link.label }}
          </RouterLink>
        </li>
      </ul>

      <hr class="text-white-50 mt-3" />

      <div class="mt-1">
        <div v-if="isAuthenticated" class="d-flex flex-column gap-2">
          <div class="text-white-50 small text-truncate">
            <i class="bi bi-person-circle me-1"></i> {{ userName }}
          </div>
          <button
            class="btn btn-outline-danger btn-sm w-100"
            @click="onLogoutButtonClick"
          >
            <i class="bi bi-box-arrow-right me-1"></i> Выйти
          </button>
        </div>
        <div v-else>
          <RouterLink to="/login" class="btn btn-primary btn-sm w-100">
            <i class="bi bi-box-arrow-in-right me-1"></i> Войти
          </RouterLink>
        </div>
      </div>
    </aside>

    <main class="flex-grow-1 bg-light" style="overflow: hidden; height: 100%;">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.nav-link {
  transition: color 0.2s ease, background-color 0.2s ease;
  border-radius: 6px;
  padding: 8px 12px;
}
.nav-link:hover {
  color: #fff !important;
  background-color: rgba(255, 255, 255, 0.1);
}
.nav-link.router-link-active {
  color: #fff !important;
  background-color: #0d6efd;
  font-weight: 500;
}
</style>