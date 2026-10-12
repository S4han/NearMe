export const categories = [
  { id: 'restaurant', name: '맛집', icon: '🍽️' },
  { id: 'cafe', name: '카페', icon: '☕' },
  { id: 'parking', name: '주차장', icon: '🅿️' },
  { id: 'hospital', name: '병원', icon: '🏥' },
  { id: 'bus_stop', name: '버스 정류소', icon: '🚌' },
  { id: 'tourist_attraction', name: '관광지', icon: '🏝️' },
] as const

export type PlaceCategory = (typeof categories)[number]['id']

// 검색 반경(미터). 기본값 3km
export const radiusOptions = [1000, 3000, 5000] as const
export type SearchRadius = (typeof radiusOptions)[number]
export const DEFAULT_RADIUS: SearchRadius = 3000
