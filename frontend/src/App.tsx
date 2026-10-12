import { useEffect, useState } from 'react'
import {
  categories,
  radiusOptions,
  DEFAULT_RADIUS,
  type PlaceCategory,
  type SearchRadius,
} from './config/categories'
import MapView from './components/MapView'

type BackendStatus = 'checking' | 'ok' | 'error'

function App() {
  const [category, setCategory] = useState<PlaceCategory>('restaurant')
  const [radius, setRadius] = useState<SearchRadius>(DEFAULT_RADIUS)
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking')

  const selected = categories.find((c) => c.id === category)!

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status?: string }) =>
        setBackendStatus(data.status === 'ok' ? 'ok' : 'error'),
      )
      .catch(() => setBackendStatus('error'))
  }, [])

  const handleSearch = () => {
    // Step 4: 실제 검색 대신 테스트용 알림
    alert(`${selected.name} / 반경 ${radius / 1000}km`)
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
        <MapView />
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
        className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white shadow hover:bg-blue-700 active:bg-blue-800"
      >
        이 지역 검색
      </button>

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
