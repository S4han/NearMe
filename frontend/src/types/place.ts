import type { LatLng } from './location'

// 화면 표시용 장소. Google Places 응답에서 필요한 필드만 옮겨 담는다(저장/캐시하지 않음)
export type NearbyPlace = {
  id: string // google: Google placeId / busStop: 제주 BIS 정류장 ID / airport: 공항 IATA 코드
  kind: 'google' | 'busStop' | 'airport'
  name: string
  location: LatLng
  address: string
  typeLabel: string
  distance: number // 검색 기준점에서의 직선거리(m)
}

