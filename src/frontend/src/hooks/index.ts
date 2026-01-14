// GanaPortal Custom Hooks
// FE-001: Core Hooks Export

export { useAuth, useAuthStore, useRequireAuth, useHasRole, useHasPermission } from './use-auth'
export { useApi, usePaginatedApi, useMutation } from './use-api'
export { useToast, useToastStore, showApiError, type Toast } from './use-toast'
export { useMediaQuery, useIsMobile, useIsTablet, useIsDesktop } from './use-media-query'
export { useDebounce, useDebouncedCallback } from './use-debounce'
export { useLocalStorage, useSessionStorage } from './use-storage'
