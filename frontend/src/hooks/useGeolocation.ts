import { useCallback, useEffect, useState } from 'react'
import type { LatLng } from '../types/location'

export type GeoStatus = 'idle' | 'locating' | 'granted' | 'denied' | 'unavailable'

// 브라우저 GPS 위치(userLocation). 권한 거부/실패 시 position은 null로 유지
export function useGeolocation() {
  const [position, setPosition] = useState<LatLng | null>(null)
  const [status, setStatus] = useState<GeoStatus>('idle')

  const locate = useCallback(() => {
    if (!('geolocation' in navigator)) {
      setStatus('unavailable')
      return
    }
    setStatus('locating')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setStatus('granted')
      },
      (err) => setStatus(err.code === err.PERMISSION_DENIED ? 'denied' : 'unavailable'),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    )
  }, [])

  useEffect(() => {
    locate()
  }, [locate])

  return { position, status, locate }
}
