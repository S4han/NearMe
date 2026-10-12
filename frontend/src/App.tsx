import { useEffect, useRef, useState } from 'react'
import {
  categories,
  DEFAULT_RADIUS,
  type PlaceCategory,
  type SearchRadius,
} from './config/categories'
import { DEFAULT_CENTER } from './config/maps'
import MapView from './components/MapView'
import TopBar, { type BackendStatus } from './components/TopBar'
import BottomSheet from './components/BottomSheet'
import PlaceList, { type SearchStatus } from './components/PlaceList'
import { LocateIcon, SearchIcon, Spinner } from './components/icons'
import { useGeolocation, type GeoStatus } from './hooks/useGeolocation'
import { searchNearbyPlaces } from './services/places'
import type { LatLng } from './types/location'
import type { NearbyPlace } from './types/place'

const geoMessages: Partial<Record<GeoStatus, string>> = {
  locating: '현재 위치를 확인하는 중…',
  denied: '위치 권한이 꺼져 있어 제주시청 기준으로 보여드려요',
  unavailable: '현재 위치를 찾지 못해 제주시청 기준으로 보여드려요',
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
  const [sheetOpen, setSheetOpen] = useState(false)

  const selected = categories.find((c) => c.id === category)!

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status?: string }) => setBackendStatus(data.status === 'ok' ? 'ok' : 'error'))
      .catch(() => setBackendStatus('error'))
  }, [])

  // 늦게 도착한 이전 검색 응답이 최신 결과를 덮어쓰지 않도록 요청 번호로 구분
  const searchSeq = useRef(0)

  const runSearch = async (searchRadius: SearchRadius) => {
    // 지도 이동만으로는 검색하지 않고, 버튼/반경을 누른 순간의 지도 중심을 검색 기준으로 확정
    const seq = ++searchSeq.current
    const center = mapCenter
    setSearchCenter(center)
    setSearchStatus('loading')
    setSelectedId(null)
    setSheetOpen(true)
    try {
      const result = await searchNearbyPlaces({
        center,
        radius: searchRadius,
        types: selected.googleTypes,
        rankBy: selected.rankBy,
      })
      if (seq !== searchSeq.current) return
      setPlaces(result)
      setSearchLabel(`${selected.name} · ${searchRadius / 1000}km`)
      setSearchStatus('done')
    } catch (e) {
      if (seq !== searchSeq.current) return
      console.error('Nearby search failed', e)
      setPlaces([])
      setSearchError(e instanceof Error ? e.message : String(e))
      setSearchStatus('error')
    }
  }

  const handleSearch = () => runSearch(radius)

  // 반경을 바꾸면 바로 다시 검색. 이미 선택된 반경을 다시 누르면 호출하지 않음(비용 절약)
  const handleRadiusChange = (r: SearchRadius) => {
    if (r === radius) return
    setRadius(r)
    runSearch(r)
  }

  const handleSelect = (id: string) => {
    setSelectedId(id)
    setSheetOpen(true)
  }

  const subtitle =
    searchStatus === 'loading'
      ? '주변을 찾는 중…'
      : searchStatus === 'done'
        ? `최근 검색: ${searchLabel} · ${places.length}곳`
        : searchStatus === 'error'
          ? '검색에 실패했어요'
          : '반경을 고르고 이 지역을 검색해 보세요'

  const geoMessage = geoMessages[geoStatus]
  const isSearching = searchStatus === 'loading'

  return (
    <div className="relative h-dvh w-full overflow-hidden bg-gray-100 font-sans text-gray-900">
      {/* 지도: 모바일은 전체 화면, 데스크톱은 왼쪽 패널 오른쪽 영역 */}
      <div className="absolute inset-0 md:left-[452px]">
        <MapView
          userLocation={userLocation}
          searchCenter={searchCenter}
          places={places}
          selectedId={selectedId}
          onSelectPlace={handleSelect}
          onCenterChange={setMapCenter}
        />
      </div>

      <button
        type="button"
        onClick={locate}
        disabled={geoStatus === 'locating'}
        aria-label="내 위치로 이동"
        className="absolute right-6 bottom-6 z-10 hidden h-12 w-12 items-center justify-center rounded-full bg-white text-blue-600 shadow-lg ring-1 ring-black/5 transition active:scale-95 disabled:opacity-60 md:flex"
      >
        <LocateIcon />
      </button>

      {/* 떠 있는 UI: 모바일은 상단 바 + 하단 시트, 데스크톱은 왼쪽 패널 */}
      <div className="pointer-events-none absolute inset-0 z-10 flex flex-col justify-between md:inset-y-4 md:right-auto md:left-4 md:w-[420px] md:justify-start md:gap-3">
        <div className="flex flex-col items-center gap-2 p-3 pt-[max(0.75rem,env(safe-area-inset-top))] md:items-stretch md:p-0">
          <div className="w-full">
            <TopBar category={category} onCategoryChange={setCategory} backendStatus={backendStatus} />
          </div>

          {geoMessage && (
            <p className="pointer-events-auto rounded-full bg-gray-900/80 px-3 py-1.5 text-xs text-white backdrop-blur md:self-center">
              {geoMessage}
            </p>
          )}

          <button
            type="button"
            onClick={handleSearch}
            disabled={isSearching}
            className="pointer-events-auto flex items-center justify-center gap-2 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition hover:bg-blue-700 active:scale-95 disabled:opacity-70 md:py-3"
          >
            {isSearching ? <Spinner /> : <SearchIcon />}
            {isSearching ? '검색 중…' : `이 지역 ${selected.name} 검색`}
          </button>
        </div>

        <BottomSheet
          open={sheetOpen}
          onToggle={() => setSheetOpen((o) => !o)}
          title={`${selected.icon} ${selected.name}`}
          subtitle={subtitle}
          radius={radius}
          onRadiusChange={handleRadiusChange}
          onLocate={locate}
          locating={geoStatus === 'locating'}
        >
          <PlaceList
            status={searchStatus}
            places={places}
            error={searchError}
            selectedId={selectedId}
            onSelect={handleSelect}
          />
        </BottomSheet>
      </div>
    </div>
  )
}

export default App
