// googleTypes: Places API (New) 장소 유형
export const categories = [
  { id: 'restaurant', name: '맛집', icon: '🍽️', googleTypes: ['restaurant'] },
  { id: 'cafe', name: '카페', icon: '☕', googleTypes: ['cafe'] },
  { id: 'convenience_store', name: '편의점', icon: '🏪', googleTypes: ['convenience_store'] },
  { id: 'parking', name: '주차장', icon: '🅿️', googleTypes: ['parking'] },
  { id: 'hospital', name: '병원', icon: '🏥', googleTypes: ['hospital', 'doctor'] },
  { id: 'bus_stop', name: '버스 정류소', icon: '🚌', googleTypes: ['bus_stop', 'bus_station'] },
  { id: 'airport', name: '공항', icon: '✈️', googleTypes: ['airport'] },
  { id: 'tourist_attraction', name: '관광지', icon: '🏝️', googleTypes: ['tourist_attraction'] },
] as const

export type PlaceCategory = (typeof categories)[number]['id']

// 검색 반경(미터). 기본값 3km
export const radiusOptions = [1000, 3000, 5000] as const
export type SearchRadius = (typeof radiusOptions)[number]
export const DEFAULT_RADIUS: SearchRadius = 3000
