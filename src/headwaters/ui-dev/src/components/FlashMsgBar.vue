<template>
  <div
    class="
      w-full
      text-gray-100 text-center
      opacity-50
      shadow-lg
      bg-blue-500
      transition
      ease-in-out
      duration-500
    "
  >
    {{ this.message }}
  </div>
</template>

<script>
export default {
  props: {
    message: {
      type: String,
      required: true,
    },
  },
};
</script>