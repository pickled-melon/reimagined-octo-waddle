import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import MainPage from '@/pages/MainPage.vue'
import useProfileStore from '@/stores/profileStore'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  linkExactActiveClass: 'active-exact',
  routes: [
    { path: "/", component: MainPage },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },
    { path: '/classrooms', component: () => import('@/views/ClassroomsView.vue') },
    { path: '/subjects', component: () => import('@/views/SubjectsView.vue') },
    { path: '/study-years', component: () => import('@/views/StudyYearsView.vue') },
    { path: '/bell-schedules', component: () => import('@/views/BellSchedulesView.vue') },
    { path: '/study-groups', component: () => import('@/views/StudyGroupsView.vue') },
    { path: '/workloads', component: () => import('@/views/WorkloadsView.vue') },
    { path: '/lessons', component: () => import('@/views/LessonsView.vue') },
    { path: '/user-subjects', component: () => import('@/views/UserSubjectsView.vue') },
    { path: '/difficulties', component: () => import('@/views/DifficultiesView.vue') },
    { path: '/profiles', component: () => import('@/views/ProfilesView.vue') },
  ],
})

let authChecked = false

router.beforeEach(async (to, from, next) => {
  const profileStore = useProfileStore()
  if (!authChecked) {
    await profileStore.fetchMe()
    authChecked = true
  }
  const publicPages = ['/login', '/register']
  if (!publicPages.includes(to.path) && !profileStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
