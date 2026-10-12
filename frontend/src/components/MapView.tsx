import { APIProvider, Map } from '@vis.gl/react-google-maps'
import {
  GOOGLE_MAPS_API_KEY,
  GOOGLE_MAPS_MAP_ID,
  DEFAULT_CENTER,
  DEFAULT_ZOOM,
} from '../config/maps'

function MapView() {
  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="flex h-72 flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white p-4 text-center text-sm text-gray-500">
        <p className="font-semibold text-gray-700">Google Maps API 키가 설정되지 않았습니다.</p>
        <p className="mt-1">
          <code>VITE_GOOGLE_MAPS_API_KEY</code>를 Codespaces Secret 또는{' '}
          <code>frontend/.env.local</code>에 등록한 뒤 개발 서버를 다시 시작하세요.
        </p>
      </div>
    )
  }

  return (
    <div className="h-72 overflow-hidden rounded-xl border border-gray-200">
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY} language="ko" region="KR">
        <Map
          mapId={GOOGLE_MAPS_MAP_ID}
          defaultCenter={DEFAULT_CENTER}
          defaultZoom={DEFAULT_ZOOM}
          gestureHandling="greedy"
          disableDefaultUI={false}
          style={{ width: '100%', height: '100%' }}
        />
      </APIProvider>
    </div>
  )
}

export default MapView
