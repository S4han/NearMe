import type { LatLng } from '../types/location'

// 지도 확대 수준(zoom)에서 화면상 가까이 겹치는 마커를 묶는다. 결과가 최대 20개라 단순 탐욕 방식으로 충분하다
export type Clustered<T> =
  | { kind: 'single'; item: T; index: number }
  | { kind: 'cluster'; members: { item: T; index: number }[]; position: LatLng }

export const CLUSTER_RADIUS_PX = 36 // 이 거리(px) 안의 마커는 하나로 묶음(핀 너비 정도)
export const CLUSTER_MAX_ZOOM = 18 // 이 이상 확대하면 묶지 않음(같은 건물 안 장소 등)

// 웹 메르카토르 기준 전체 지도 픽셀 좌표(256px 타일, 2^zoom 배)
export function toPixel({ lat, lng }: LatLng, zoom: number): { x: number; y: number } {
  const scale = 256 * 2 ** zoom
  const sin = Math.min(Math.max(Math.sin((lat * Math.PI) / 180), -0.9999), 0.9999)
  return {
    x: ((lng + 180) / 360) * scale,
    y: (0.5 - Math.log((1 + sin) / (1 - sin)) / (4 * Math.PI)) * scale,
  }
}

// index는 원래 목록 순서(마커 번호 = index + 1). keepId(선택한 장소)는 항상 따로 표시
export function clusterByPixel<T>(
  items: T[],
  positionOf: (item: T) => LatLng,
  zoom: number,
  keepId: (item: T) => boolean,
  radiusPx = CLUSTER_RADIUS_PX,
): Clustered<T>[] {
  if (zoom >= CLUSTER_MAX_ZOOM) return items.map((item, index) => ({ kind: 'single', item, index }))
  const groups: { anchor: { x: number; y: number }; members: { item: T; index: number }[] }[] = []
  const singles: Clustered<T>[] = []
  items.forEach((item, index) => {
    if (keepId(item)) {
      singles.push({ kind: 'single', item, index })
      return
    }
    const p = toPixel(positionOf(item), zoom)
    const group = groups.find((g) => Math.hypot(g.anchor.x - p.x, g.anchor.y - p.y) <= radiusPx)
    if (group) group.members.push({ item, index })
    else groups.push({ anchor: p, members: [{ item, index }] })
  })
  const result: Clustered<T>[] = groups.map((g) => {
    if (g.members.length === 1) return { kind: 'single', ...g.members[0] }
    const n = g.members.length
    return {
      kind: 'cluster',
      members: g.members,
      position: {
        lat: g.members.reduce((s, m) => s + positionOf(m.item).lat, 0) / n,
        lng: g.members.reduce((s, m) => s + positionOf(m.item).lng, 0) / n,
      },
    }
  })
  return [...result, ...singles]
}
