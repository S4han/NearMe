import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchFlightStatus } from '../services/flights'
import type { FlightDirection, FlightStatus, FlightStatusResponse } from '../types/flight'
import { Spinner } from './icons'

const AUTO_REFRESH_MS = 60_000

function formatTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function statusColor(status: string | null): string {
  if (!status) return 'bg-gray-100 text-gray-500'
  if (/결항|회항/.test(status)) return 'bg-red-100 text-red-700'
  if (/지연/.test(status)) return 'bg-orange-100 text-orange-700'
  if (/탑승|마감|수속/.test(status)) return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-600'
}

function FlightRow({ f }: { f: FlightStatus }) {
  return (
    <li className="flex items-center gap-3 py-2">
      <span className="w-12 shrink-0 text-center">
        <span className={`block text-sm font-bold ${f.estimatedTime ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
          {f.scheduledTime}
        </span>
        {f.estimatedTime && <span className="block text-sm font-bold text-orange-600">{f.estimatedTime}</span>}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm text-gray-800">
          {f.counterpart || f.counterpartCode}
          {f.international && <span className="ml-1 text-[11px] text-purple-600">국제</span>}
        </span>
        <span className="block truncate text-xs text-gray-500">
          {f.airline} {f.flightNo}
          {f.gate && ` · 게이트 ${f.gate}`}
        </span>
      </span>
      {f.status && (
        <span className={`shrink-0 rounded-md px-2 py-1 text-xs font-semibold ${statusColor(f.status)}`}>{f.status}</span>
      )}
    </li>
  )
}

// 선택한 공항의 실시간 출발/도착 현황(한국공항공사)
function FlightPanel({ airportCode }: { airportCode: string }) {
  const [direction, setDirection] = useState<FlightDirection>('departure')
  const [data, setData] = useState<FlightStatusResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const reqSeq = useRef(0)

  const load = useCallback(async () => {
    const seq = ++reqSeq.current
    setLoading(true)
    try {
      const result = await fetchFlightStatus(airportCode, direction)
      if (seq !== reqSeq.current) return
      setData(result)
      setError('')
    } catch (e) {
      if (seq !== reqSeq.current) return
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      if (seq === reqSeq.current) setLoading(false)
    }
  }, [airportCode, direction])

  // 처음 열 때·출발/도착 전환 시 조회하고, 열려 있는 동안 1분마다 갱신
  useEffect(() => {
    setData(null)
    load()
    const timer = window.setInterval(load, AUTO_REFRESH_MS)
    return () => {
      window.clearInterval(timer)
      reqSeq.current++ // 닫힌 뒤 도착한 응답 무시
    }
  }, [load])

  const tabClass = (d: FlightDirection) =>
    `flex-1 rounded-md py-1.5 text-xs font-semibold transition ${
      direction === d ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
    }`

  return (
    <div className="mt-3 rounded-xl bg-white p-3 ring-1 ring-blue-100">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-sm font-bold text-gray-900">✈️ 실시간 운항 현황</p>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-600 disabled:opacity-60"
        >
          {loading ? <Spinner className="h-3 w-3" /> : '↻'} 새로고침
        </button>
      </div>

      <div className="mb-2 flex gap-1 rounded-lg bg-gray-100 p-1">
        <button type="button" className={tabClass('departure')} onClick={() => setDirection('departure')}>
          출발
        </button>
        <button type="button" className={tabClass('arrival')} onClick={() => setDirection('arrival')}>
          도착
        </button>
      </div>

      {error && <p className="rounded-lg bg-red-50 p-2 text-xs text-red-700">운항 정보를 불러오지 못했습니다. {error}</p>}

      {!data && !error && (
        <div className="space-y-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-10 animate-pulse rounded-lg bg-gray-100" />
          ))}
        </div>
      )}

      {data && data.flights.length === 0 && (
        <p className="py-3 text-center text-xs text-gray-500">
          지금부터 6시간 안에 {direction === 'departure' ? '출발' : '도착'} 예정인 항공편이 없습니다.
        </p>
      )}

      {data && data.flights.length > 0 && (
        <ul className="max-h-80 divide-y divide-gray-100 overflow-y-auto">
          {data.flights.map((f) => (
            <FlightRow key={`${f.flightNo}-${f.scheduledTime}`} f={f} />
          ))}
        </ul>
      )}

      {data && (
        <p className="mt-2 text-[11px] text-gray-400">
          마지막 갱신 {formatTime(data.fetchedAt)} · 1시간 전~6시간 후 · 1분마다 자동 갱신 · 한국공항공사
        </p>
      )}
    </div>
  )
}

export default FlightPanel
