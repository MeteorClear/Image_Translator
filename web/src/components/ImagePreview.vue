<!-- Image preview componet -->

<script setup lang="ts">
defineProps<{ imageUrl: string, displayText: string }>()
</script>

<template>
    <div class="image-preview">
        <img :src="imageUrl" alt="source image" />
        <p>{{ displayText }}</p>
    </div>
</template>

<style scoped>
.image-preview {
    margin: 5px;
    width: 100%;
}
</style>