import { useEffect, useRef, useState } from 'react'
import {
  categories,
  DEFAULT_RADIUS,
  type PlaceCategory,
  type SearchRadius,
} from './config/categories'
import { DEFAULT_CENTER } from './config/maps'
import { API_BASE_URL, BACKEND_ENABLED } from './config/api'
import MapView from './components/MapView'
import TopBar, { type BackendStatus } from './components/TopBar'
import BottomSheet from './components/BottomSheet'
import PlaceList, { type SearchStatus } from './components/PlaceList'
import { LocateIcon, SearchIcon, Spinner } from './components/icons'
import { useGeolocation, type GeoStatus } from './hooks/useGeolocation'
import { searchNearbyPlaces } from './services/places'
import { isInJeju, searchNearbyBusStations } from './services/bus'
import { AIRPORT_SEARCH_RADIUS, searchNearbyAirports } from './services/flights'
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
  // 휴대폰: 검색하면 카테고리 메뉴를 한 줄로 접고, '이 지역 검색' 버튼은 지도를 직접 움직였을 때만 표시
  const [menuOpen, setMenuOpen] = useState(true)
  const [mapMoved, setMapMoved] = useState(false)

  const selected = categories.find((c) => c.id === category)!

  useEffect(() => {
    if (!BACKEND_ENABLED) return
    fetch(`${API_BASE_URL}/api/health`)
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status?: string }) => setBackendStatus(data.status === 'ok' ? 'ok' : 'error'))
      .catch(() => setBackendStatus('error'))
  }, [])

  // 내 위치로 이동하면 이후 카테고리/반경 검색은 새 위치(이동한 지도 중심) 기준으로 한다
  useEffect(() => {
    if (userLocation) setSearchCenter(null)
  }, [userLocation])

  // 늦게 도착한 이전 검색 응답이 최신 결과를 덮어쓰지 않도록 요청 번호로 구분
  const searchSeq = useRef(0)

  const runSearch = async (searchCategory: PlaceCategory, searchRadius: SearchRadius, center: LatLng) => {
    const cat = categories.find((c) => c.id === searchCategory)!
    const seq = ++searchSeq.current
    setSearchCenter(center)
    setMenuOpen(false)
    setMapMoved(false)
    setSearchStatus('loading')
    setSelectedId(null)
    setSheetOpen(true)
    try {
      // 제주 안의 버스 정류소는 제주 BIS 데이터(Backend)로 검색: 실시간 도착 정보 연결, Google 비용 없음
      const useJejuBus = searchCategory === 'bus_stop' && BACKEND_ENABLED && isInJeju(center)
      // 공항은 한국공항공사 공항 목록(Backend)으로 넓은 고정 반경에서 검색: 실시간 출발/도착 현황 연결
      const useAirports = searchCategory === 'airport' && BACKEND_ENABLED
      const result = useJejuBus
        ? await searchNearbyBusStations(center, searchRadius)
        : useAirports
          ? await searchNearbyAirports(center)
          : await searchNearbyPlaces({
              center,
              radius: searchRadius,
              types: cat.googleTypes,
            })
      if (seq !== searchSeq.current) return
      // 모든 검색 결과는 검색 기준점에서 가까운 순으로 표시(목록 번호 = 지도 마커 번호)
      setPlaces([...result].sort((a, b) => a.distance - b.distance))
      setSearchLabel(`${cat.name} · ${(useAirports ? AIRPORT_SEARCH_RADIUS : searchRadius) / 1000}km`)
      setSearchStatus('done')
    } catch (e) {
      if (seq !== searchSeq.current) return
      console.error('Nearby search failed', e)
      setPlaces([])
      setSearchError(e instanceof Error ? e.message : String(e))
      setSearchStatus('error')
    }
  }

  // '이 지역 검색': 지도 이동만으로는 검색하지 않고, 버튼을 누른 순간의 지도 중심을 검색 기준으로 확정
  const handleSearch = () => runSearch(category, radius, mapCenter)

  // 카테고리/반경 변경은 같은 장소에서 다시 찾는 것이므로 직전 검색 기준점을 유지한다.
  // (검색 후 지도가 결과에 맞춰 자동 이동해도 기준점이 따라 움직이지 않도록)
  // 이미 선택된 것을 다시 누르면 호출하지 않음(비용 절약)
  const handleCategoryChange = (c: PlaceCategory) => {
    if (c === category) {
      setMenuOpen(false) // 펼친 메뉴에서 같은 카테고리를 누르면 다시 접기만 한다
      return
    }
    setCategory(c)
    runSearch(c, radius, searchCenter ?? mapCenter)
  }

  const handleRadiusChange = (r: SearchRadius) => {
    if (r === radius) return
    setRadius(r)
    runSearch(category, r, searchCenter ?? mapCenter)
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
  // 아직 검색 전·내 위치로 이동함(searchCenter 초기화)·지도를 끌었음·검색 실패 시에만 버튼 표시
  const showSearchButton =
    isSearching || searchCenter === null || mapMoved || searchStatus === 'error'

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
          onUserMove={() => setMapMoved(true)}
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
        <div
          id="nm-top"
          className="flex flex-col items-center gap-2 p-3 pt-[max(0.75rem,env(safe-area-inset-top))] md:items-stretch md:p-0"
        >
          <div className="w-full">
            <TopBar
              category={category}
              onCategoryChange={handleCategoryChange}
              backendStatus={BACKEND_ENABLED ? backendStatus : undefined}
              collapsed={!menuOpen}
              onExpand={() => setMenuOpen(true)}
            />
          </div>

          {geoMessage && (
            <p className="pointer-events-auto rounded-full bg-gray-900/80 px-3 py-1.5 text-xs text-white backdrop-blur md:self-center">
              {geoMessage}
            </p>
          )}

          {showSearchButton && (
            <button
              type="button"
              onClick={handleSearch}
              disabled={isSearching}
              className="pointer-events-auto flex items-center justify-center gap-2 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 transition hover:bg-blue-700 active:scale-95 disabled:opacity-70 md:py-3"
            >
              {isSearching ? <Spinner /> : <SearchIcon />}
              {isSearching ? '검색 중…' : `이 지역 ${selected.name} 검색`}
            </button>
          )}
        </div>

        <BottomSheet
          open={sheetOpen}
          onToggle={() => setSheetOpen((o) => !o)}
          title={`${selected.icon} ${selected.name}`}
          subtitle={subtitle}
          radius={radius}
          onRadiusChange={handleRadiusChange}
          showRadius={!(category === 'airport' && BACKEND_ENABLED)}
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
