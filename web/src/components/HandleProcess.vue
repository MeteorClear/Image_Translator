<!-- Handle process componet -->

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import ImageUploader from './ImageUploader.vue'
import ImagePreview from './ImagePreview.vue'

const selectedFile = ref<File | null>(null)
const sourceImageUrl = ref('')
const processedImageUrl = ref('')

const onFileSelected = (file: File) => {
    selectedFile.value = file
    sourceImageUrl.value = URL.createObjectURL(file)
    processedImageUrl.value = ''
}
    
</script>

<template>
    <div class="handle-process-container">
        <ImageUploader @file-selected="onFileSelected" />

        <ImagePreview v-if="sourceImageUrl" :imageUrl="sourceImageUrl" />
    </div>
</template>

<style scoped>
.handle-process-container {
    margin: 5px;
}
</style>