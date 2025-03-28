<!-- Download image component -->

<script setup lang="ts">
defineProps<{ imageUrl: string }>()
</script>

<template>
    <div class="download-image">
        <a :href="imageUrl" download="processed_image.jpg">
            <button>Download</button>
        </a>
    </div>
</template>

<style scoped>
.download-image {
    margin: 5px;
}
</style>