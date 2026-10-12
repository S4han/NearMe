import { useState } from 'react'
import { fetchPlaceDetails } from '../services/places'
import type { PlaceDetails } from '../types/place'

// 같은 장소를 다시 열 때 재호출하지 않도록 현재 탭 메모리에만 보관(새로고침 시 사라짐, 저장하지 않음)
const sessionCache = new Map<string, PlaceDetails>()

type Status = 'idle' | 'loading' | 'done' | 'error'

function PlaceDetailsPanel({ placeId }: { placeId: string }) {
  const cached = sessionCache.get(placeId) ?? null
  const [details, setDetails] = useState<PlaceDetails | null>(cached)
  const [status, setStatus] = useState<Status>(cached ? 'done' : 'idle')

  const load = async () => {
    setStatus('loading')
    try {
      const result = await fetchPlaceDetails(placeId)
      sessionCache.set(placeId, result)
      setDetails(result)
      setStatus('done')
    } catch (e) {
      console.error('Place details failed', e)
      setStatus('error')
    }
  }

  if (status === 'idle' || status === 'error') {
    return (
      <div className="mt-2">
        <button
          type="button"
          onClick={load}
          className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700"
        >
          상세정보 보기
        </button>
        {status === 'error' && (
          <p className="mt-1 text-xs text-red-600">상세정보를 불러오지 못했습니다. 다시 시도하세요.</p>
        )}
      </div>
    )
  }

  if (status === 'loading' || !details) {
    return <p className="mt-2 text-xs text-gray-500">상세정보 불러오는 중…</p>
  }

  return (
    <div className="mt-2 space-y-1 rounded-md bg-gray-50 p-2 text-xs text-gray-700">
      <p>
        ⭐{' '}
        {details.rating !== null
          ? `${details.rating.toFixed(1)} (${details.ratingCount ?? 0}명)`
          : '평점 정보 없음'}
      </p>
      <p>
        📞{' '}
        {details.phone ? (
          <a href={`tel:${details.phone}`} className="text-blue-600">
            {details.phone}
          </a>
        ) : (
          '전화번호 정보 없음'
        )}
      </p>
      {details.website && (
        <p className="truncate">
          🌐{' '}
          <a href={details.website} target="_blank" rel="noopener noreferrer" className="text-blue-600">
            {details.website}
          </a>
        </p>
      )}
      {details.openingHours.length > 0 ? (
        <details>
          <summary className="cursor-pointer">🕒 영업시간</summary>
          <ul className="mt-1 pl-5">
            {details.openingHours.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </details>
      ) : (
        <p>🕒 영업시간 정보 없음</p>
      )}
      {details.googleMapsUrl && (
        <a
          href={details.googleMapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block font-semibold text-blue-600"
        >
          Google 지도에서 보기 ↗
        </a>
      )}
    </div>
  )
}

export default PlaceDetailsPanel
