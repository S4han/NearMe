// Google Maps 설정. 키는 Codespaces Secret 또는 frontend/.env.local 에서 주입한다.
export const GOOGLE_MAPS_API_KEY: string = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? ''

// AdvancedMarker 사용에 필요. 개발 중에는 Google 제공 DEMO_MAP_ID 사용 가능
export const GOOGLE_MAPS_MAP_ID: string = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || 'DEMO_MAP_ID'

// 위치 권한 거부 시 대체 중심: 제주시청
export const DEFAULT_CENTER = { lat: 33.4996, lng: 126.5312 }
export const DEFAULT_ZOOM = 14
