// Backend(/api/flights/...) 응답 타입. 필드 정의는 docs/flight-api.md 참고

export type Airport = {
  code: string // IATA (예: CJU)
  name: string
  shortName: string
  lat: number
  lng: number
  distance: number
}

export type FlightDirection = 'departure' | 'arrival'

export type FlightStatus = {
  flightNo: string
  airline: string
  direction: FlightDirection
  counterpart: string // 출발편은 도착지, 도착편은 출발지
  counterpartCode: string | null
  international: boolean
  scheduledTime: string // HH:MM
  estimatedTime: string | null // 변경 시각(예정과 같으면 null)
  status: string | null // 출발, 도착, 지연, 결항, 탑승중 …
  gate: string | null
}

export type FlightStatusResponse = {
  airport: { code: string; name: string }
  direction: FlightDirection
  flights: FlightStatus[]
  fetchedAt: string
}
