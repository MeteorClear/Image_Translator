<!-- Handle process componet -->

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import ImageUploader from './ImageUploader.vue'
import ImagePreview from './ImagePreview.vue'
import ProcessedImageViewer from './ProcessedImageViewer.vue'

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
    fileHash.value = ''
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
            alert('process failure')
            console.error(error)
        }
    }

    try {
        const res = await axios.get(`/download/${fileHash.value}`, { 
            responseType: 'blob' 
        })
        processedImageUrl.value = URL.createObjectURL(res.data)
    } catch (error: any) {
        alert('process failure')
        console.error(error)
    }

    isProcessing.value = false
}

    
</script>

<template>
    <div class="handle-process-container">
        <ImageUploader @file-selected="onFileSelected" />

        <ImagePreview v-if="sourceImageUrl" :imageUrl="sourceImageUrl" />

        <button v-if="selectedFile && !isProcessing" @click="handleProcess">Process</button>

        <div v-if="isProcessing">In progress ...</div>

        <div v-if="processedImageUrl && fileHash">
            <div>File Hash</div>
            <div>{{ fileHash }}</div>
        </div>

        <ProcessedImageViewer v-if="processedImageUrl" :imageUrl="processedImageUrl" />

        
    </div>
</template>

<style scoped>
.handle-process-container {
    margin: 5px;
}
</style>