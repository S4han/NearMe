import { API_BASE_URL } from '../config/api'
import type { ArrivalsResponse, BusStation, RoutesResponse } from '../types/bus'
import type { LatLng } from '../types/location'
import type { NearbyPlace } from '../types/place'

// 제주도 대략 범위(마라도~우도 포함). 이 안에서는 버스 정류소를 제주 BIS 데이터로 검색한다
const JEJU_BOUNDS = { south: 33.1, north: 33.6, west: 126.1, east: 127.0 }

export function isInJeju({ lat, lng }: LatLng): boolean {
  return (
    lat >= JEJU_BOUNDS.south && lat <= JEJU_BOUNDS.north && lng >= JEJU_BOUNDS.west && lng <= JEJU_BOUNDS.east
  )
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // 본문이 JSON이 아니면 상태 코드만 사용
    }
    throw new Error(detail)
  }
  return (await res.json()) as T
}

const DIRECTION_LABEL: Record<string, string> = { N: '북쪽 방향', S: '남쪽 방향', E: '동쪽 방향', W: '서쪽 방향' }

export async function searchNearbyBusStations(center: LatLng, radius: number): Promise<NearbyPlace[]> {
  const params = new URLSearchParams({
    lat: String(center.lat),
    lng: String(center.lng),
    radius: String(radius),
    limit: '20',
  })
  const { stations } = await getJson<{ stations: BusStation[] }>(`/api/bus/stations/nearby?${params}`)
  return stations.map((s) => ({
    id: s.id,
    kind: 'busStop',
    name: s.name,
    location: { lat: s.lat, lng: s.lng },
    address: s.direction ? DIRECTION_LABEL[s.direction] : '',
    typeLabel: '제주 버스 정류장',
    distance: s.distance,
  }))
}

export function fetchArrivals(stationId: string): Promise<ArrivalsResponse> {
  return getJson<ArrivalsResponse>(`/api/bus/stations/${encodeURIComponent(stationId)}/arrivals`)
}

export function fetchStationRoutes(stationId: string): Promise<RoutesResponse> {
  return getJson<RoutesResponse>(`/api/bus/stations/${encodeURIComponent(stationId)}/routes`)
}
