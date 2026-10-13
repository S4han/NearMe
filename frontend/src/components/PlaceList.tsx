import { useEffect } from 'react'
import { directionsUrl, distanceMeters, formatDistance, placeDetailsUrl } from '../services/places'
import type { LatLng } from '../types/location'
import type { NearbyPlace } from '../types/place'
import BusArrivalPanel from './BusArrivalPanel'
import FlightPanel from './FlightPanel'

export type SearchStatus = 'idle' | 'loading' | 'done' | 'error'

type PlaceListProps = {
  status: SearchStatus
  places: NearbyPlace[]
  error: string
  selectedId: string | null
  onSelect: (id: string) => void
  userLocation: LatLng | null // 있으면 거리는 내 위치 기준으로 표시(정렬·번호는 검색 지점 기준 유지)
  searchCenter: LatLng | null
}

// 검색 지점이 내 위치에서 이만큼 이상 떨어져 있으면 거리 앞에 '내 위치에서'를 붙여 구분
const FAR_FROM_ME_M = 500

function Message({ icon, title, body }: { icon: string; title: string; body?: string }) {
  return (
    <div className="flex flex-col items-center py-6 text-center">
      <span className="text-3xl" aria-hidden="true">
        {icon}
      </span>
      <p className="mt-2 text-sm font-semibold text-gray-700">{title}</p>
      {body && <p className="mt-1 text-xs break-all text-gray-500">{body}</p>}
    </div>
  )
}

function PlaceList({ status, places, error, selectedId, onSelect, userLocation, searchCenter }: PlaceListProps) {
  // 지도를 옮겨 다른 지역을 검색해도, 길을 모르는 사용자에게 필요한 건 지금 내 위치에서의 거리
  const searchedAway =
    userLocation !== null && searchCenter !== null && distanceMeters(userLocation, searchCenter) >= FAR_FROM_ME_M
  const distanceLabel = (p: NearbyPlace) =>
    userLocation
      ? `${searchedAway ? '내 위치에서 ' : ''}${formatDistance(distanceMeters(userLocation, p.location))}`
      : formatDistance(p.distance)

  // 지도에서 마커를 누르면 목록의 해당 항목이 보이도록 스크롤
  useEffect(() => {
    if (selectedId) {
      document.getElementById(`place-${selectedId}`)?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [selectedId])

  if (status === 'idle') {
    return <Message icon="🗺️" title="지도를 움직이고 ‘이 지역 검색’을 눌러 보세요" />
  }

  if (status === 'loading') {
    return (
      <ul className="space-y-2" aria-label="검색 중">
        {[0, 1, 2].map((i) => (
          <li key={i} className="h-20 animate-pulse rounded-2xl bg-gray-100" />
        ))}
      </ul>
    )
  }

  if (status === 'error') {
    return <Message icon="⚠️" title="검색에 실패했습니다. 잠시 후 다시 시도하세요." body={error} />
  }

  if (places.length === 0) {
    return <Message icon="🔍" title="결과가 없습니다" body="반경을 넓히거나 지도를 옮겨 다시 검색해 보세요." />
  }

  return (
    <ul className="space-y-2">
      {places.map((p, i) => {
        const isSelected = p.id === selectedId
        return (
          <li
            key={p.id}
            id={`place-${p.id}`}
            className={`rounded-2xl p-3 transition ${
              isSelected ? 'bg-blue-50 ring-2 ring-blue-500' : 'bg-white ring-1 ring-gray-100 hover:bg-gray-50'
            }`}
          >
            <button type="button" onClick={() => onSelect(p.id)} className="flex w-full gap-3 text-left">
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${
                  isSelected ? 'bg-red-600' : 'bg-blue-600'
                }`}
              >
                {i + 1}
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex items-baseline justify-between gap-2">
                  <span className="truncate font-semibold text-gray-900">{p.name}</span>
                  <span className="shrink-0 text-xs font-medium text-gray-500">{distanceLabel(p)}</span>
                </span>
                {p.typeLabel && <span className="block text-xs text-blue-600">{p.typeLabel}</span>}
                {p.address && <span className="mt-0.5 block truncate text-xs text-gray-500">{p.address}</span>}
                {p.kind === 'busStop' && !isSelected && (
                  <span className="mt-1 block text-xs font-semibold text-blue-600">눌러서 실시간 도착 정보 보기 ›</span>
                )}
                {p.kind === 'airport' && !isSelected && (
                  <span className="mt-1 block text-xs font-semibold text-blue-600">눌러서 실시간 출발·도착 현황 보기 ›</span>
                )}
              </span>
            </button>
            <div className="mt-2 flex gap-2 pl-10">
              <a
                href={placeDetailsUrl(p)}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-200"
              >
                {p.kind === 'google' ? '상세정보' : '지도에서 보기'}
              </a>
              <a
                href={directionsUrl(p)}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
              >
                길찾기
              </a>
            </div>
            {p.kind === 'busStop' && isSelected && <BusArrivalPanel stationId={p.id} />}
            {p.kind === 'airport' && isSelected && <FlightPanel airportCode={p.id} />}
          </li>
        )
      })}
    </ul>
  )
}

export default PlaceList
