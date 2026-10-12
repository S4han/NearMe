// Backend(/api/bus/...) 응답 타입. 필드 정의는 docs/jeju-bus-api.md 참고

export type BusStation = {
  id: string
  name: string
  lat: number
  lng: number
  direction: 'N' | 'S' | 'E' | 'W' | null
  distance: number
}

export type BusArrival = {
  routeId: string
  routeNum: string
  destination: string
  minutes: number
  remainStations: number | null
  currentStationName: string | null // JTBIS 대체 경로에서는 null
  plateNo: string | null
  lowFloor: boolean | null
}

export type BusRoute = {
  routeId: string
  routeNum: string
  routeName: string
  origin: string | null
  destination: string
}

export type ArrivalsResponse = {
  stationId: string
  arrivals: BusArrival[]
  source: string
  fetchedAt: string
}

export type RoutesResponse = {
  stationId: string
  routes: BusRoute[]
  source: string
  fetchedAt: string
}
