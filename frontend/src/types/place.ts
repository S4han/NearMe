import type { LatLng } from './location'

// 화면 표시용 장소. Google Places 응답에서 필요한 필드만 옮겨 담는다(저장/캐시하지 않음)
export type NearbyPlace = {
  id: string
  name: string
  location: LatLng
  address: string
  typeLabel: string
  distance: number // 검색 기준점에서의 직선거리(m)
}

// 장소 상세(사용자가 요청할 때만 조회)
export type PlaceDetails = {
  rating: number | null
  ratingCount: number | null
  openingHours: string[]
  phone: string
  website: string
  googleMapsUrl: string
}
