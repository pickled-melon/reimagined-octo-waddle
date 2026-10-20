<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import useProfileStore from '@/stores/profileStore';

const profileStore = useProfileStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const errorText = ref("");

async function onLoginClick() {
    try {
        await profileStore.login(username.value, password.value);
        router.push('/');
    } catch (e) {
        errorText.value = "Неверный логин или пароль";
    }
}
</script>

<template>
    <div class="d-flex justify-content-center p-4">
        <form style="width: 350px" @submit.prevent.stop="onLoginClick">
            <h3 class="text-center mb-4">Вход</h3>
            <div v-if="errorText" class="alert alert-danger">{{ errorText }}</div>
            <div class="mb-3">
                <label class="form-label">Логин</label>
                <input v-model="username" required type="text" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Пароль</label>
                <input v-model="password" required type="password" class="form-control">
            </div>
            <button class="btn btn-primary w-100">Войти</button>
            <div class="text-center mt-3">
                <router-link to="/register">Нет аккаунта? Зарегистрироваться</router-link>
            </div>
        </form>
    </div>
</template>