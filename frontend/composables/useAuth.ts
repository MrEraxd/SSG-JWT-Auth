export default function (
  loginData: { username: string; password: string } | null = null
) {
  // Create a state that will hold our user and provide
  // it to whole app
  const user = useState(
    "user",
    (): { username: string; permissions: string[] } | void => {}
  );

  // This is shortcut for checking if user is authenticated
  const isAuthenticated = computed(() => user.value !== undefined);

  // Function that will allow us to login user
  const { execute: login } = useFetch("/auth/login", {
    server: false,
    baseURL: "http://local.example.com/api",
    body: loginData,
    method: "POST",
    immediate: false,
    watch: false,
    onResponse(data) {
      if (data.response.status === 200) {
        user.value = data.response._data;
        navigateTo("/");
      }
    },
  });

  // After user is logged in (contain valid JWT in cookie)
  // he can open many pages but because we are not using
  // any persistant storage we have to refetch user every
  // time page is refreshed/closed opened again
  const { execute: refetchUser } = useFetch("/auth/me", {
    server: false,
    immediate: false,
    baseURL: "http://local.example.com/api",
    onResponse(data) {
      user.value = data.response._data;
    },
  });

  // Function that will test requierd permissions agains
  // permissions that user have
  function havePerms(requiredPermissions: string[]) {
    if (!requiredPermissions) {
      return true;
    }

    return requiredPermissions?.every((requiredPerm) =>
      user.value?.permissions?.includes(requiredPerm)
    );
  }

  return { login, user, havePerms, isAuthenticated, refetchUser };
}
