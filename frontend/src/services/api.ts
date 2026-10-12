import { API_BASE_URL } from '../config/api'

// Backend JSON 호출. 오류 응답이면 FastAPI의 detail 메시지를 Error로 던진다
export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`)
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
