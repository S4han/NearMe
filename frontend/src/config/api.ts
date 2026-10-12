// Backend 주소. 개발 중에는 Vite 프록시(/api → 127.0.0.1:8000)를 사용하고,
// 배포 환경에서는 VITE_API_BASE_URL 이 설정된 경우에만 Backend를 호출한다
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ''
export const BACKEND_ENABLED: boolean = import.meta.env.DEV || API_BASE_URL !== ''
