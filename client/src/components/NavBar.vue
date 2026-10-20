<script setup>
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

const profileStore = useProfileStore();
const { isAuthenticated, userName } = storeToRefs(profileStore);

async function onLogoutButtonClick() {
    profileStore.logout();
}
</script>

<template>
    <nav class="navbar navbar-expand-sm bg-body-tertiary mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Расписание</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse w-100 justify-content-between" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <router-link class="nav-link" to="/">Главная</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/classrooms">Кабинеты</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/subjects">Дисциплины</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/study-years">Годы</router-link>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/admin" target="_blank">Админка</a>
                    </li>
                </ul>
                <div role="search">
                    <span v-if="isAuthenticated" class="me-3">Авторизован: <b>{{ userName }}</b></span>
                    <button v-if="isAuthenticated" class="btn btn-outline-danger btn-sm" @click="onLogoutButtonClick">
                        Выйти
                    </button>
                    <router-link v-else to="/login" class="btn btn-outline-primary btn-sm">
                        Войти
                    </router-link>
                </div>
            </div>
        </div>
    </nav>
</template>