export const APP_ROUTES = {
  home: '/',
  users: '/users',
  roles: '/roles',
  permissions: '/permissions',
  policies: '/policies',
} as const

export type AppRouteKey = keyof typeof APP_ROUTES


