<script setup lang="ts">
  const { user, havePerms, isAuthenticated } = useAuth();
</script>

<template>
  <div>
    Hello {{ user }}, you've opened dashboard

    <NuxtLink
      v-if="havePerms(['p_orders_r'])"
      to="orders"
    >
      Orders
    </NuxtLink>
  </div>
</template>
