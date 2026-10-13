<script setup>
import { RouterLink, RouterView } from 'vue-router';

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
];

const externalLinks = [
  { to: '/admin/', label: 'Панель админа', icon: 'bi-person-fill-gear' },
];
</script>

<template>
  <div class="d-flex">
    <aside class="bg-dark text-white p-3" style="width: 240px; min-height: 100vh;">
      <h5 class="mb-4"><i class="bi bi-calendar-week me-2"></i>Расписание</h5>
      <ul class="nav flex-column">
        <li v-for="link in links" :key="link.to" class="nav-item">
          <RouterLink :to="link.to" class="nav-link text-white-50">
            <i :class="['bi', link.icon, 'me-2']"></i>{{ link.label }}
          </RouterLink>
        </li>
      </ul>
      <hr class="text-white-50">
      <ul class="nav flex-column">
        <li v-for="link in externalLinks" :key="link.to" class="nav-item">
          <a :href="link.to" class="nav-link text-white-50">
            <i :class="['bi', link.icon, 'me-2']"></i>{{ link.label }}
          </a>
        </li>
      </ul>
    </aside>
    <main class="flex-grow-1 bg-light">
      <RouterView />
    </main>
  </div>
</template>