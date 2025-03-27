<!-- Handle process componet -->

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import ImageUploader from './ImageUploader.vue'

const selectedFile = ref<File | null>(null)

const onFileSelected = (file: File) => {
    selectedFile.value = file
    console.log(selectedFile)
}
    
</script>

<template>
    <div class="handle-process-container">
        <ImageUploader @file-selected="onFileSelected" />
    </div>
</template>

<style scoped>
.handle-process-container {
    margin: 5px;
}
</style>