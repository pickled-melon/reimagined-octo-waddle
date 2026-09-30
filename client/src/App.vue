<script setup>
import {computed, ref} from 'vue';

const a = ref(13);
const b = ref(23);

const c = computed(() => {
  return a.value + b.value;
})

const list = ref([
  {"fio": "Вася", "group": 1},
  {"fio": "Петя", "group": 1},
  {"fio": "Катя", "group": 2},
  {"fio": "Юля", "group": 2},
]);

const groups = ref({
  1: {"title": "ИСТб-24-1"},
  2: {"title": "ИСТб-24-2"},
});

</script>

<template>
  <div>
    <div v-for="item in list" class="student_item">
      <b>{{ item.fio }}</b> <b>{{ groups[item.group].title }}</b> <br>
    </div>

    <input type="number" v-model="a"><br>
    <input type="number" v-model="b">
    <br>

    <b>{{a}} + {{b}}</b> <span> = {{ c }} </span> <br>
  </div>
</template>

<style scoped>
</style>
