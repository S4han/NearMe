import { useEffect, useState } from 'react'
import {
  categories,
  radiusOptions,
  DEFAULT_RADIUS,
  type PlaceCategory,
  type SearchRadius,
} from './config/categories'
import MapView from './components/MapView'
import { DEFAULT_CENTER } from './config/maps'
import { useGeolocation, type GeoStatus } from './hooks/useGeolocation'
import type { LatLng } from './types/location'
import type { NearbyPlace } from './types/place'
import PlaceList, { type SearchStatus } from './components/PlaceList'
import { searchNearbyPlaces } from './services/places'

type BackendStatus = 'checking' | 'ok' | 'error'

const geoMessages: Record<GeoStatus, string> = {
  idle: '',
  locating: '현재 위치를 확인하는 중…',
  granted: '현재 위치를 중심으로 표시합니다.',
  denied: '위치 권한이 거부되어 제주시청을 중심으로 표시합니다. 지도를 움직여 검색하세요.',
  unavailable: '현재 위치를 가져올 수 없어 제주시청을 중심으로 표시합니다. 지도를 움직여 검색하세요.',
}

function App() {
  const [category, setCategory] = useState<PlaceCategory>('restaurant')
  const [radius, setRadius] = useState<SearchRadius>(DEFAULT_RADIUS)
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking')

  // 위치 상태 분리: userLocation(GPS) / mapCenter(현재 지도 중심) / searchCenter(검색 확정 좌표)
  const { position: userLocation, status: geoStatus, locate } = useGeolocation()
  const [mapCenter, setMapCenter] = useState<LatLng>(DEFAULT_CENTER)
  const [searchCenter, setSearchCenter] = useState<LatLng | null>(null)

  // 검색 결과
  const [places, setPlaces] = useState<NearbyPlace[]>([])
  const [searchStatus, setSearchStatus] = useState<SearchStatus>('idle')
  const [searchLabel, setSearchLabel] = useState('')
  const [searchError, setSearchError] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const selected = categories.find((c) => c.id === category)!

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status?: string }) =>
        setBackendStatus(data.status === 'ok' ? 'ok' : 'error'),
      )
      .catch(() => setBackendStatus('error'))
  }, [])

  const handleSearch = async () => {
    // 지도 이동만으로는 검색하지 않고, 버튼을 누른 순간의 지도 중심을 검색 기준으로 확정
    const center = mapCenter
    setSearchCenter(center)
    setSearchStatus('loading')
    setSelectedId(null)
    try {
      const result = await searchNearbyPlaces({
        center,
        radius,
        types: selected.googleTypes,
        rankBy: selected.rankBy,
      })
      setPlaces(result)
      setSearchLabel(`${selected.icon} ${selected.name} · 반경 ${radius / 1000}km`)
      setSearchStatus('done')
    } catch (e) {
      console.error('Nearby search failed', e)
      setPlaces([])
      setSearchError(e instanceof Error ? e.message : String(e))
      setSearchStatus('error')
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col bg-gray-50 px-4 py-6">
      <header className="mb-4">
        <h1 className="text-2xl font-bold text-blue-600">NearMe</h1>
        <p className="text-sm text-gray-500">내 주변 장소와 교통정보 찾기</p>
      </header>

      <section className="mb-4 grid grid-cols-3 gap-2">
        {categories.map((c) => {
          const isSelected = c.id === category
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setCategory(c.id)}
              aria-pressed={isSelected}
              className={`flex flex-col items-center rounded-xl border px-2 py-3 text-sm transition ${
                isSelected
                  ? 'border-blue-600 bg-blue-600 text-white shadow'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-blue-300'
              }`}
            >
              <span className="text-xl">{c.icon}</span>
              <span className="mt-1">{c.name}</span>
            </button>
          )
        })}
      </section>

      <h2 className="mb-3 text-lg font-semibold text-gray-800">
        {selected.icon} {selected.name} 검색
      </h2>

      <section className="mb-4">
        <div className="mb-2 flex items-center justify-between gap-2">
          <p className="text-xs text-gray-500">{geoMessages[geoStatus]}</p>
          <button
            type="button"
            onClick={locate}
            disabled={geoStatus === 'locating'}
            className="shrink-0 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-700 hover:border-blue-300 disabled:opacity-50"
          >
            📍 내 위치
          </button>
        </div>
        <MapView
          userLocation={userLocation}
          searchCenter={searchCenter}
          places={places}
          selectedId={selectedId}
          onSelectPlace={setSelectedId}
          onCenterChange={setMapCenter}
        />
      </section>

      <section className="mb-4 flex gap-2">
        {radiusOptions.map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRadius(r)}
            aria-pressed={r === radius}
            className={`flex-1 rounded-full border py-2 text-sm transition ${
              r === radius
                ? 'border-blue-600 bg-blue-50 font-semibold text-blue-700'
                : 'border-gray-200 bg-white text-gray-600'
            }`}
          >
            {r / 1000}km
          </button>
        ))}
      </section>

      <button
        type="button"
        onClick={handleSearch}
        disabled={searchStatus === 'loading'}
        className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white shadow hover:bg-blue-700 active:bg-blue-800 disabled:opacity-60"
      >
        {searchStatus === 'loading' ? '검색 중…' : '이 지역 검색'}
      </button>

      <PlaceList
        status={searchStatus}
        places={places}
        label={searchLabel}
        error={searchError}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <footer className="mt-auto pt-6 text-center text-xs text-gray-500">
        NearMe Backend:{' '}
        <span
          className={
            backendStatus === 'ok'
              ? 'font-semibold text-green-600'
              : backendStatus === 'error'
                ? 'font-semibold text-red-600'
                : 'text-gray-400'
          }
        >
          {backendStatus}
        </span>
      </footer>
    </div>
  )
}

export default App
