import { useEffect, useState } from 'react'
import { formatDistance } from '../services/places'
import { fetchEta, formatDuration, type EtaResponse } from '../services/routes'
import type { LatLng } from '../types/location'

// 선택한 장소까지 내 위치에서 도보·자동차 소요 시간(T map 실제 경로). 키가 없거나 실패하면 표시하지 않는다
function RouteEta({ from, to }: { from: LatLng; to: LatLng }) {
  const [eta, setEta] = useState<EtaResponse | null>(null)
  const [state, setState] = useState<'loading' | 'done' | 'hidden'>('loading')

  useEffect(() => {
    let alive = true
    setState('loading')
    fetchEta(from, to)
      .then((result) => {
        if (!alive) return
        setEta(result)
        setState('done')
      })
      .catch(() => alive && setState('hidden'))
    return () => {
      alive = false
    }
  }, [from, to])

  if (state === 'hidden') return null
  if (state === 'loading') {
    return <p className="mt-2 pl-10 text-xs text-gray-400">내 위치에서 소요 시간 계산 중…</p>
  }
  return (
    <p className="mt-2 flex flex-wrap gap-x-3 gap-y-1 pl-10 text-xs font-semibold text-gray-700">
      {eta?.walk && (
        <span>
          🚶 도보 {formatDuration(eta.walk.seconds)}
          <span className="font-normal text-gray-400"> · {formatDistance(eta.walk.distance)}</span>
        </span>
      )}
      {eta?.car && (
        <span>
          🚗 차 {formatDuration(eta.car.seconds)}
          <span className="font-normal text-gray-400"> · {formatDistance(eta.car.distance)}</span>
        </span>
      )}
    </p>
  )
}

export default RouteEta
