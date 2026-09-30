<script setup>
import {computed, ref} from 'vue';

const a = ref(13);
const b = ref(23);

const c = computed(() => {
  return a.value + b.value;
})

</script>

<template>
  <div>
    <input type="number" v-model="a"><br>
    <input type="number" v-model="b">
    <br>

    <b>{{a}} + {{b}}</b> <span> = {{ c }} </span> <br>
  </div>
</template>

<style scoped>
</style>
