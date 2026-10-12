import { directionsUrl, formatDistance } from '../services/places'
import type { NearbyPlace } from '../types/place'

export type SearchStatus = 'idle' | 'loading' | 'done' | 'error'

type PlaceListProps = {
  status: SearchStatus
  places: NearbyPlace[]
  label: string
  error: string
  selectedId: string | null
  onSelect: (id: string) => void
}

function PlaceList({ status, places, label, error, selectedId, onSelect }: PlaceListProps) {
  if (status === 'idle') return null

  if (status === 'loading') {
    return <p className="mt-3 text-center text-sm text-gray-500">검색 중…</p>
  }

  if (status === 'error') {
    return (
      <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        <p className="font-semibold">검색에 실패했습니다. 잠시 후 다시 시도하세요.</p>
        <p className="mt-1 break-all text-xs text-red-500">{error}</p>
      </div>
    )
  }

  if (places.length === 0) {
    return (
      <p className="mt-3 rounded-lg bg-white p-3 text-center text-sm text-gray-500 shadow-sm">
        {label} 결과가 없습니다. 반경을 넓히거나 지도를 옮겨 다시 검색하세요.
      </p>
    )
  }

  return (
    <section className="mt-3">
      <p className="mb-2 text-xs text-gray-500">
        {label} · {places.length}개
      </p>
      <ul className="space-y-2">
        {places.map((p, i) => {
          const isSelected = p.id === selectedId
          return (
            <li
              key={p.id}
              className={`rounded-lg border bg-white p-3 shadow-sm ${
                isSelected ? 'border-red-500' : 'border-gray-200'
              }`}
            >
              <button type="button" onClick={() => onSelect(p.id)} className="w-full text-left">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-semibold text-gray-800">
                    <span className="mr-1 text-blue-600">{i + 1}.</span>
                    {p.name}
                  </span>
                  <span className="shrink-0 text-xs text-gray-500">{formatDistance(p.distance)}</span>
                </div>
                {p.typeLabel && <p className="text-xs text-gray-500">{p.typeLabel}</p>}
                {p.address && <p className="mt-1 text-xs text-gray-600">{p.address}</p>}
              </button>
              <a
                href={directionsUrl(p)}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-block text-xs font-semibold text-blue-600"
              >
                Google 지도 길찾기 ↗
              </a>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

export default PlaceList
