<script lang="ts" setup>
const username = ref('');
const password = ref('');

const data = computed(() => {
  const userInfo = {
    username: username.value,
    password: password.value,
  };

  return JSON.stringify(userInfo);
});

const { user, login } = useAuth(data);
</script>

<template>
  <form
    @submit.prevent="login"
    class="form"
  >
    <label for="username">Username</label>
    <input
      id="username"
      type="text"
      v-model="username"
    />

    <label for="password">Password</label>
    <input
      id="password"
      type="password"
      v-model="password"
    />
    <button>SUBMIT</button>

    <div>User {{ user }}</div>
  </form>
</template>

<style>
.form {
  display: flex;
  flex-flow: column;
  width: 320px;
}
</style>
