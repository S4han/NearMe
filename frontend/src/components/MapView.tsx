import { useEffect } from 'react'
import {
  APIProvider,
  AdvancedMarker,
  Map,
  Pin,
  useMap,
  type MapCameraChangedEvent,
} from '@vis.gl/react-google-maps'
import {
  GOOGLE_MAPS_API_KEY,
  GOOGLE_MAPS_MAP_ID,
  DEFAULT_CENTER,
  DEFAULT_ZOOM,
} from '../config/maps'
import type { LatLng } from '../types/location'
import type { NearbyPlace } from '../types/place'

type MapViewProps = {
  userLocation: LatLng | null
  searchCenter: LatLng | null
  places: NearbyPlace[]
  selectedId: string | null
  onSelectPlace: (id: string) => void
  onCenterChange: (center: LatLng) => void
}

// GPS 위치가 새로 잡히면 지도를 그 위치로 이동
function PanTo({ target }: { target: LatLng | null }) {
  const map = useMap()
  useEffect(() => {
    if (map && target) map.panTo(target)
  }, [map, target])
  return null
}

// 모바일에서는 상단 바와 하단 시트가 지도를 가리므로 그만큼 여백을 두고 맞춤
function fitPadding(): number | { top: number; right: number; bottom: number; left: number } {
  if (window.matchMedia('(min-width: 768px)').matches) return 48
  return { top: 180, right: 32, bottom: Math.round(window.innerHeight * 0.34) + 120, left: 32 }
}

// 새 검색 결과가 오면 검색 기준점과 결과가 모두 보이도록 화면 맞춤
function FitToResults({ center, places }: { center: LatLng | null; places: NearbyPlace[] }) {
  const map = useMap()
  useEffect(() => {
    if (!map || !center || places.length === 0) return
    const lats = [center.lat, ...places.map((p) => p.location.lat)]
    const lngs = [center.lng, ...places.map((p) => p.location.lng)]
    map.fitBounds(
      {
        north: Math.max(...lats),
        south: Math.min(...lats),
        east: Math.max(...lngs),
        west: Math.min(...lngs),
      },
      fitPadding(),
    )
  }, [map, center, places])
  return null
}

function MapView({
  userLocation,
  searchCenter,
  places,
  selectedId,
  onSelectPlace,
  onCenterChange,
}: MapViewProps) {
  const selectedPlace = places.find((p) => p.id === selectedId) ?? null

  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-gray-100 p-6 pb-48 text-center text-sm text-gray-500">
        <p className="font-semibold text-gray-700">Google Maps API 키가 설정되지 않았습니다.</p>
        <p className="mt-1">
          <code>VITE_GOOGLE_MAPS_API_KEY</code>를 Codespaces Secret 또는{' '}
          <code>frontend/.env.local</code>에 등록한 뒤 개발 서버를 다시 시작하세요.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full w-full">
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY} language="ko" region="KR">
        <Map
          mapId={GOOGLE_MAPS_MAP_ID}
          defaultCenter={DEFAULT_CENTER}
          defaultZoom={DEFAULT_ZOOM}
          gestureHandling="greedy"
          disableDefaultUI
          onCameraChanged={(ev: MapCameraChangedEvent) => onCenterChange(ev.detail.center)}
          style={{ width: '100%', height: '100%' }}
        >
          <PanTo target={userLocation} />
          <FitToResults center={searchCenter} places={places} />
          <PanTo target={selectedPlace?.location ?? null} />

          {userLocation && (
            <AdvancedMarker position={userLocation} title="내 위치">
              <span className="relative flex h-5 w-5 items-center justify-center">
                <span className="absolute h-full w-full animate-ping rounded-full bg-blue-400 opacity-60" />
                <span className="relative h-4 w-4 rounded-full border-[3px] border-white bg-blue-500 shadow-md" />
              </span>
            </AdvancedMarker>
          )}

          {searchCenter && (
            <AdvancedMarker position={searchCenter} title="검색 기준 위치">
              <div className="h-3 w-3 rounded-full border-2 border-white bg-gray-800 shadow" />
            </AdvancedMarker>
          )}

          {places.map((p, i) => {
            const isSelected = p.id === selectedId
            return (
              <AdvancedMarker
                key={p.id}
                position={p.location}
                title={p.name}
                zIndex={isSelected ? 1000 : i}
                onClick={() => onSelectPlace(p.id)}
              >
                <Pin
                  background={isSelected ? '#dc2626' : '#2563eb'}
                  borderColor={isSelected ? '#991b1b' : '#1e40af'}
                  glyph={String(i + 1)}
                  glyphColor="#ffffff"
                  scale={isSelected ? 1.2 : 1}
                />
              </AdvancedMarker>
            )
          })}
        </Map>
      </APIProvider>
    </div>
  )
}

export default MapView
