import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchArrivals, fetchStationRoutes } from '../services/bus'
import type { ArrivalsResponse, RoutesResponse } from '../types/bus'
import { Spinner } from './icons'

const AUTO_REFRESH_MS = 30_000

function formatTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function minutesLabel(minutes: number): string {
  return minutes <= 1 ? '곧 도착' : `${minutes}분`
}

// 선택한 제주 버스 정류장의 실시간 도착 예정 정보 + 경유 노선
function BusArrivalPanel({ stationId }: { stationId: string }) {
  const [data, setData] = useState<ArrivalsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const reqSeq = useRef(0)

  const [routes, setRoutes] = useState<RoutesResponse | null>(null)
  const [routesOpen, setRoutesOpen] = useState(false)
  const [routesError, setRoutesError] = useState('')

  const load = useCallback(async () => {
    const seq = ++reqSeq.current
    setLoading(true)
    try {
      const result = await fetchArrivals(stationId)
      if (seq !== reqSeq.current) return
      setData(result)
      setError('')
    } catch (e) {
      if (seq !== reqSeq.current) return
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      if (seq === reqSeq.current) setLoading(false)
    }
  }, [stationId])

  // 처음 열 때 조회하고, 열려 있는 동안 30초마다 갱신
  useEffect(() => {
    load()
    const timer = window.setInterval(load, AUTO_REFRESH_MS)
    return () => {
      window.clearInterval(timer)
      reqSeq.current++ // 닫힌 뒤 도착한 응답 무시
    }
  }, [load])

  const toggleRoutes = async () => {
    const next = !routesOpen
    setRoutesOpen(next)
    if (next && !routes) {
      try {
        setRoutes(await fetchStationRoutes(stationId))
        setRoutesError('')
      } catch (e) {
        setRoutesError(e instanceof Error ? e.message : String(e))
      }
    }
  }

  return (
    <div className="mt-3 rounded-xl bg-white p-3 ring-1 ring-blue-100">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-sm font-bold text-gray-900">🚌 실시간 도착 정보</p>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-600 disabled:opacity-60"
        >
          {loading ? <Spinner className="h-3 w-3" /> : '↻'} 새로고침
        </button>
      </div>

      {error && (
        <p className="rounded-lg bg-red-50 p-2 text-xs text-red-700">
          버스 정보를 불러오지 못했습니다. {error}
        </p>
      )}

      {!data && !error && (
        <div className="space-y-2">
          {[0, 1].map((i) => (
            <div key={i} className="h-10 animate-pulse rounded-lg bg-gray-100" />
          ))}
        </div>
      )}

      {data && data.arrivals.length === 0 && (
        <p className="py-3 text-center text-xs text-gray-500">
          도착 예정인 버스가 없습니다.
          <br />
          운행 종료 시간이거나 정보가 없는 정류장일 수 있어요.
        </p>
      )}

      {data && data.arrivals.length > 0 && (
        <ul className="divide-y divide-gray-100">
          {data.arrivals.map((a) => (
            <li key={`${a.routeId}-${a.plateNo ?? ''}-${a.minutes}`} className="flex items-center gap-3 py-2">
              <span className="min-w-12 shrink-0 rounded-md bg-blue-600 px-2 py-1 text-center text-xs font-bold text-white">
                {a.routeNum}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm text-gray-800">{a.destination} 방면</span>
                <span className="block truncate text-xs text-gray-500">
                  {a.remainStations !== null && `${a.remainStations}정류장 전`}
                  {a.currentStationName && ` · 현재 ${a.currentStationName}`}
                  {a.lowFloor && ' · 저상'}
                </span>
              </span>
              <span
                className={`shrink-0 text-sm font-bold ${a.minutes <= 3 ? 'text-red-600' : 'text-gray-900'}`}
              >
                {minutesLabel(a.minutes)}
              </span>
            </li>
          ))}
        </ul>
      )}

      {data && (
        <p className="mt-2 text-[11px] text-gray-400">
          마지막 갱신 {formatTime(data.fetchedAt)} · 30초마다 자동 갱신 · 제주 버스정보시스템
        </p>
      )}

      <button
        type="button"
        onClick={toggleRoutes}
        className="mt-2 w-full rounded-lg bg-gray-50 py-2 text-xs font-semibold text-gray-600"
      >
        {routesOpen ? '경유 노선 접기 ▲' : '이 정류장을 지나는 노선 보기 ▼'}
      </button>

      {routesOpen && (
        <div className="mt-2">
          {routesError && <p className="text-xs text-red-600">노선 정보를 불러오지 못했습니다. {routesError}</p>}
          {!routes && !routesError && <p className="text-xs text-gray-500">노선 정보 불러오는 중…</p>}
          {routes && routes.routes.length === 0 && <p className="text-xs text-gray-500">경유 노선 정보가 없습니다.</p>}
          {routes && routes.routes.length > 0 && (
            <ul className="flex flex-wrap gap-1.5">
              {routes.routes.map((r) => (
                <li
                  key={r.routeId}
                  title={[r.origin, r.destination].filter(Boolean).join(' → ')}
                  className="rounded-md bg-blue-50 px-2 py-1 text-xs text-blue-700"
                >
                  <span className="font-bold">{r.routeName || r.routeNum}</span>
                  {r.destination && <span className="text-blue-500"> {r.destination}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default BusArrivalPanel
