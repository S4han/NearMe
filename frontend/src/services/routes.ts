import type { LatLng } from '../types/location'
import { getJson } from './api'

// Backend(/api/routes/eta) 응답. T map 실제 경로 기준(도보는 직선 10km 이내일 때만)
export type RouteSummary = { distance: number; seconds: number }
export type EtaResponse = { walk: RouteSummary | null; car: RouteSummary | null; fetchedAt: string }

export function fetchEta(from: LatLng, to: LatLng): Promise<EtaResponse> {
  const params = new URLSearchParams({
    from_lat: String(from.lat),
    from_lng: String(from.lng),
    to_lat: String(to.lat),
    to_lng: String(to.lng),
  })
  return getJson<EtaResponse>(`/api/routes/eta?${params}`)
}

export function formatDuration(seconds: number): string {
  const minutes = Math.max(1, Math.round(seconds / 60))
  if (minutes < 60) return `${minutes}분`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m ? `${h}시간 ${m}분` : `${h}시간`
}
