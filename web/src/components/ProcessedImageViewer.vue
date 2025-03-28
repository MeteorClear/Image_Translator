<!-- Processed Image Viewer -->

<script setup lang="ts">
defineProps<{ imageUrl: string }>()
</script>

<template>
    <div class="processed-image-viewer">
        <img :src="imageUrl" alt="processed image" />
        <p>Processed Image</p>
    </div>
</template>

<style scoped>
.processed-image-viewer {
    margin: 5px;
    max-width: 500px;
}
</style>