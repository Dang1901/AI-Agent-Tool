export const APP_ROUTES = {
  home: '/',
  users: '/users',
  roles: '/roles',
  permissions: '/permissions',
  policies: '/policies',
  envvars: '/envvars',
  releases: '/releases',
  audit: '/audit',
  logs: '/logs',
} as const

export type AppRouteKey = keyof typeof APP_ROUTES


