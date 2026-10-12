import type { Airport, FlightDirection, FlightScheduleResponse, FlightStatusResponse } from '../types/flight'
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
    address: a.code,
    typeLabel: '공항 · 실시간 운항정보',
    distance: a.distance,
  }))
}

export function fetchFlightStatus(code: string, direction: FlightDirection): Promise<FlightStatusResponse> {
  const params = new URLSearchParams({ direction })
  return getJson<FlightStatusResponse>(`/api/flights/airports/${encodeURIComponent(code)}/status?${params}`)
}

export function fetchFlightSchedule(dep: string, arr: string): Promise<FlightScheduleResponse> {
  const params = new URLSearchParams({ dep, arr })
  return getJson<FlightScheduleResponse>(`/api/flights/schedule?${params}`)
}

// 국내선 노선 선택용(Backend services/flights.py AIRPORTS와 같은 순서·코드)
export const DOMESTIC_AIRPORTS = [
  { code: 'GMP', name: '김포' },
  { code: 'PUS', name: '김해' },
  { code: 'CJU', name: '제주' },
  { code: 'TAE', name: '대구' },
  { code: 'CJJ', name: '청주' },
  { code: 'KWJ', name: '광주' },
  { code: 'MWX', name: '무안' },
  { code: 'RSU', name: '여수' },
  { code: 'USN', name: '울산' },
  { code: 'KPO', name: '포항경주' },
  { code: 'HIN', name: '사천' },
  { code: 'YNY', name: '양양' },
  { code: 'KUV', name: '군산' },
  { code: 'WJU', name: '원주' },
] as const
