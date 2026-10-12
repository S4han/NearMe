import { categories, type PlaceCategory } from '../config/categories'

export type BackendStatus = 'checking' | 'ok' | 'error'

type TopBarProps = {
  category: PlaceCategory
  onCategoryChange: (c: PlaceCategory) => void
  backendStatus: BackendStatus
}

const backendDot: Record<BackendStatus, string> = {
  checking: 'bg-gray-300',
  ok: 'bg-emerald-500',
  error: 'bg-red-500',
}

function TopBar({ category, onCategoryChange, backendStatus }: TopBarProps) {
  return (
    <div className="pointer-events-auto rounded-3xl bg-white/90 p-3 shadow-lg ring-1 ring-black/5 backdrop-blur-md">
      <div className="flex items-center justify-between px-1">
        <h1 className="text-lg font-extrabold tracking-tight">
          <span className="text-blue-600">Near</span>Me
        </h1>
        <span
          className="flex items-center gap-1.5 text-[11px] text-gray-500"
          title={`NearMe Backend: ${backendStatus}`}
        >
          <span className={`h-2 w-2 rounded-full ${backendDot[backendStatus]}`} />
          Backend {backendStatus}
        </span>
      </div>

      <div className="-mx-3 mt-2 flex gap-2 overflow-x-auto px-3 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {categories.map((c) => {
          const isSelected = c.id === category
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => onCategoryChange(c.id)}
              aria-pressed={isSelected}
              className={`flex shrink-0 items-center gap-1.5 rounded-full px-3.5 py-2 text-sm font-medium transition active:scale-95 ${
                isSelected
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span aria-hidden="true">{c.icon}</span>
              {c.name}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TopBar
