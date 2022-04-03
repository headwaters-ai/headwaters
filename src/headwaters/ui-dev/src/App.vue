<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <header>
    <div>
      <nav class="flex flex-row">
        <div class="m-2">
          <RouterLink to="/">Home</RouterLink>
        </div>
        <div class="m-2">
          <RouterLink to="/about">About</RouterLink>
        </div>
      </nav>
    </div>
  </header>

  <RouterView />
</template>


