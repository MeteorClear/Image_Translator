<!-- Handle process componet -->

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import ImageUploader from './ImageUploader.vue'
import ImagePreview from './ImagePreview.vue'

const selectedFile = ref<File | null>(null)
const sourceImageUrl = ref('')
const processedImageUrl = ref('')
const isProcessing = ref(false)
const fileHash = ref('')

const onFileSelected = (file: File) => {
    selectedFile.value = file
    sourceImageUrl.value = URL.createObjectURL(file)
    processedImageUrl.value = ''
    isProcessing.value = false
}

const handleProcess = async () => {
    if (!selectedFile.value) return
    isProcessing.value = true
    fileHash.value = ''

    try {
        const formData = new FormData()
        formData.append('image', selectedFile.value)

        const { data } = await axios.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data'},
        })

        const { file_hash } = data
        fileHash.value = file_hash
        console.log(fileHash.value)

    } catch (error: any) {
        if (error.response?.status === 303) {
            fileHash.value = error.response?.data.file_hash
            console.log(fileHash.value)
        } else {
            alert('error')
            console.error(error)
        }
    } finally {
        isProcessing.value = false

    }
}

    
</script>

<template>
    <div class="handle-process-container">
        <ImageUploader @file-selected="onFileSelected" />

        <ImagePreview v-if="sourceImageUrl" :imageUrl="sourceImageUrl" />

        <button v-if="selectedFile && !isProcessing" @click="handleProcess">Process</button>
    </div>
</template>

<style scoped>
.handle-process-container {
    margin: 5px;
}
</style>