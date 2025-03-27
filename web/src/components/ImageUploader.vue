<!-- Image upload componet -->

<script setup lang="ts">
const emit = defineEmits(['file-selected'])

const onFileChange = (e: Event) => {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (file) {
        emit('file-selected', file)
    }
}
</script>

<template>
    <div class="image-uploader">
        <input type="file" accept="image/*" @change="onFileChange" />
    </div>
</template>

<style scoped>
.image-uploader {
    margin: 5px;
}
</style>