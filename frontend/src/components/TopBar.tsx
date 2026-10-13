import { categories, type PlaceCategory } from '../config/categories'

export type BackendStatus = 'checking' | 'ok' | 'error'

type TopBarProps = {
  category: PlaceCategory
  onCategoryChange: (c: PlaceCategory) => void
  backendStatus?: BackendStatus // 없으면 Backend 상태 표시 숨김(Backend 미배포 환경)
}

function TopBar({ category, onCategoryChange, backendStatus }: TopBarProps) {
  return (
    <div className="pointer-events-auto rounded-3xl bg-white/90 p-2.5 shadow-lg ring-1 ring-black/5 backdrop-blur-md md:p-3">
      <div className="flex items-center justify-between px-1">
        <h1 className="text-base font-extrabold tracking-tight md:text-lg">
          <span className="text-blue-600">Near</span>Me
        </h1>
        {/* 정상일 때는 숨기고, 서버에 연결되지 않을 때만 알린다 */}
        {backendStatus === 'error' && (
          <span className="flex items-center gap-1.5 text-[11px] text-red-600" title="NearMe Backend: error">
            <span className="h-2 w-2 rounded-full bg-red-500" />
            서버 연결 안 됨
          </span>
        )}
      </div>

      {/* 휴대폰에서도 8개가 한 번에 보이도록 4×2 격자(아이콘 위, 이름 아래) */}
      <div className="mt-1.5 grid grid-cols-4 gap-1.5">
        {categories.map((c) => {
          const isSelected = c.id === category
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => onCategoryChange(c.id)}
              aria-pressed={isSelected}
              className={`flex min-w-0 flex-col items-center gap-0.5 rounded-2xl px-1 py-1.5 transition active:scale-95 ${
                isSelected
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span aria-hidden="true" className="text-lg leading-none">
                {c.icon}
              </span>
              <span className="w-full truncate text-center text-[11px] font-medium">{c.name}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TopBar
