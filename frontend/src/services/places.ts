import { MAX_RESULTS } from '../config/maps'
import type { LatLng } from '../types/location'
import type { NearbyPlace, PlaceDetails } from '../types/place'

type SearchParams = {
  center: LatLng
  radius: number
  types: readonly string[]
  rankBy: 'distance' | 'popularity'
}

// 비용 통제: 목록 표시에 필요한 최소 필드만 요청한다(Nearby Search Pro 등급).
// 평점·영업시간·전화번호 등은 장소 상세 단계에서 필요할 때만 요청한다.
const FIELDS = ['id', 'displayName', 'location', 'formattedAddress', 'primaryTypeDisplayName']

async function loadPlacesLibrary(): Promise<google.maps.PlacesLibrary> {
  if (typeof google === 'undefined' || !google.maps?.importLibrary) {
    throw new Error('지도가 아직 로드되지 않았습니다.')
  }
  return (await google.maps.importLibrary('places')) as google.maps.PlacesLibrary
}

export async function searchNearbyPlaces({
  center,
  radius,
  types,
  rankBy,
}: SearchParams): Promise<NearbyPlace[]> {
  const { Place, SearchNearbyRankPreference } = await loadPlacesLibrary()

  const { places } = await Place.searchNearby({
    fields: FIELDS,
    locationRestriction: { center, radius },
    includedTypes: [...types],
    maxResultCount: MAX_RESULTS,
    rankPreference:
      rankBy === 'distance'
        ? SearchNearbyRankPreference.DISTANCE
        : SearchNearbyRankPreference.POPULARITY,
  })

  return places.flatMap((p) => {
    if (!p.location) return []
    const location = { lat: p.location.lat(), lng: p.location.lng() }
    return [
      {
        id: p.id,
        name: p.displayName ?? '(이름 없음)',
        location,
        address: p.formattedAddress ?? '',
        typeLabel: p.primaryTypeDisplayName ?? '',
        distance: distanceMeters(center, location),
      },
    ]
  })
}

// 상세 필드는 Place Details Enterprise 등급이므로 사용자가 '상세정보'를 눌렀을 때만 1회 조회
const DETAIL_FIELDS = [
  'rating',
  'userRatingCount',
  'regularOpeningHours',
  'nationalPhoneNumber',
  'websiteURI',
  'googleMapsURI',
]

export async function fetchPlaceDetails(id: string): Promise<PlaceDetails> {
  const { Place } = await loadPlacesLibrary()
  const place = new Place({ id })
  await place.fetchFields({ fields: DETAIL_FIELDS })
  return {
    rating: place.rating ?? null,
    ratingCount: place.userRatingCount ?? null,
    openingHours: place.regularOpeningHours?.weekdayDescriptions ?? [],
    phone: place.nationalPhoneNumber ?? '',
    website: place.websiteURI ?? '',
    googleMapsUrl: place.googleMapsURI ?? '',
  }
}

// 두 좌표 사이 직선거리(m), 하버사인 공식
export function distanceMeters(a: LatLng, b: LatLng): number {
  const R = 6371000
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(b.lat - a.lat)
  const dLng = toRad(b.lng - a.lng)
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(h))
}

export function formatDistance(m: number): string {
  return m < 1000 ? `${Math.round(m)}m` : `${(m / 1000).toFixed(1)}km`
}

// Google 지도 길찾기 링크(API 호출 없음). 한국은 대중교통 길찾기만 지원
export function directionsUrl(place: NearbyPlace): string {
  const params = new URLSearchParams({
    api: '1',
    destination: `${place.location.lat},${place.location.lng}`,
    destination_place_id: place.id,
    travelmode: 'transit',
  })
  return `https://www.google.com/maps/dir/?${params}`
}
