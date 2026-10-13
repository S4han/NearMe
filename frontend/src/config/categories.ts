// googleTypes: Places API (New) 장소 유형
// rank: Google에서 받을 20곳을 고르는 기준(화면 목록은 항상 가까운 순으로 다시 정렬)
//   popularity: 반경 안 인기 순 — 가게가 몰린 곳에서 이름난 곳이 작은 가게들에 밀려 빠지지 않도록(맛집·카페·관광지)
//   distance: 가까운 순 — 가장 가까운 곳이 중요한 편의시설
export const categories = [
  { id: 'restaurant', name: '맛집', icon: '🍽️', googleTypes: ['restaurant'], rank: 'popularity' },
  { id: 'cafe', name: '카페', icon: '☕', googleTypes: ['cafe'], rank: 'popularity' },
  { id: 'convenience_store', name: '편의점', icon: '🏪', googleTypes: ['convenience_store'], rank: 'distance' },
  { id: 'parking', name: '주차장', icon: '🅿️', googleTypes: ['parking'], rank: 'distance' },
  { id: 'hospital', name: '병원', icon: '🏥', googleTypes: ['hospital', 'doctor'], rank: 'distance' },
  { id: 'bus_stop', name: '버스 정류소', icon: '🚌', googleTypes: ['bus_stop', 'bus_station'], rank: 'distance' },
  { id: 'airport', name: '공항', icon: '✈️', googleTypes: ['airport'], rank: 'distance' },
  { id: 'tourist_attraction', name: '관광지', icon: '🏝️', googleTypes: ['tourist_attraction'], rank: 'popularity' },
] as const

export type PlaceCategory = (typeof categories)[number]['id']

// 검색 반경(미터). 기본값 3km
export const radiusOptions = [1000, 3000, 5000] as const
export type SearchRadius = (typeof radiusOptions)[number]
export const DEFAULT_RADIUS: SearchRadius = 3000
