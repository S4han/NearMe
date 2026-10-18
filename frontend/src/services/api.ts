import { API_BASE_URL } from '../config/api'

// Backend 응답 알림. 응답을 받았다면(오류 상태 코드 포함) 서버에 연결된 것이므로
// App이 '서버 연결 안 됨' 표시를 바로 지우는 데 쓴다
const listeners = new Set<() => void>()

export function onBackendResponse(listener: () => void): () => void {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

// Backend JSON 호출. 오류 응답이면 FastAPI의 detail 메시지를 Error로 던진다
export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
  listeners.forEach((l) => l())
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // 본문이 JSON이 아니면 상태 코드만 사용
    }
    throw new Error(detail)
  }
  return (await res.json()) as T
}
