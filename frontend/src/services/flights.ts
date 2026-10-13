import type { Airport, FlightDirection, FlightStatusResponse } from '../types/flight'
import type { LatLng } from '../types/location'
import type { NearbyPlace } from '../types/place'
import { getJson } from './api'

// 공항은 드물어 생활 반경(1~5km)으로는 찾기 어려우므로 고정 반경으로 검색한다
export const AIRPORT_SEARCH_RADIUS = 50_000

export async function searchNearbyAirports(center: LatLng): Promise<NearbyPlace[]> {
  const params = new URLSearchParams({
    lat: String(center.lat),
    lng: String(center.lng),
    radius: String(AIRPORT_SEARCH_RADIUS),
  })
  const { airports } = await getJson<{ airports: Airport[] }>(`/api/flights/airports/nearby?${params}`)
  return airports.map((a) => ({
    id: a.code,
    kind: 'airport',
    name: a.name,
    location: { lat: a.lat, lng: a.lng },
    address: '',
    typeLabel: `공항 · ${a.code}`,
    distance: a.distance,
  }))
}

export function fetchFlightStatus(code: string, direction: FlightDirection): Promise<FlightStatusResponse> {
  const params = new URLSearchParams({ direction })
  return getJson<FlightStatusResponse>(`/api/flights/airports/${encodeURIComponent(code)}/status?${params}`)
}
