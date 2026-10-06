import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/classrooms' },
    { path: '/classrooms', component: () => import('@/views/ClassroomsView.vue') },
    { path: '/subjects', component: () => import('@/views/SubjectsView.vue') },
    { path: '/study-years', component: () => import('@/views/StudyYearsView.vue') },
    { path: '/bell-schedules', component: () => import('@/views/BellSchedulesView.vue') },
    { path: '/profiles', component: () => import('@/views/ProfilesView.vue') },
    { path: '/user-subjects', component: () => import('@/views/UserSubjectsView.vue') },
    { path: '/difficulties', component: () => import('@/views/DifficultiesView.vue') },
    { path: '/study-groups', component: () => import('@/views/StudyGroupsView.vue') },
    { path: '/workloads', component: () => import('@/views/WorkloadsView.vue') },
    { path: '/lessons', component: () => import('@/views/LessonsView.vue') },
  ],
})

export default router
