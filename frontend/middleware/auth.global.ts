export default defineNuxtRouteMiddleware(async (to) => {
  // This line prevents middleware from running when site
  // is generated with `npm run generate`
  if (process.server) return;

  // Import data from useAuth composable
  const { isAuthenticated, refetchUser, havePerms } = useAuth();

  // Because we are storing user in app memory we will
  // have to refetch user on each page refresh
  // NOTE: Changing path with vue-router does not count
  // as page refresh
  if (to.path !== "/login" && !isAuthenticated.value) {
    await refetchUser();
  }

  // Extract permissions from page meta
  const routePermissions = to.meta?.permissions as string[];

  // If user do not have required perms then navigate to /
  if (!havePerms(routePermissions)) return navigateTo("/");
});
