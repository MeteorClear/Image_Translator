<!-- Image preview componet -->

<script setup lang="ts">
defineProps<{imageUrl: string }>()
</script>

<template>
    <div class="image-preview">
        <img :src="imageUrl" alt="source image" />
        <p>Uploaded Image</p>
    </div>
</template>

<style scoped>
.image-preview {
    margin: 5px;
    max-width: 500px;
}
</style>