import type { ReactNode } from 'react'
import { radiusOptions, type SearchRadius } from '../config/categories'
import { LocateIcon } from './icons'

type BottomSheetProps = {
  open: boolean
  onToggle: () => void
  title: string
  subtitle: string
  radius: SearchRadius
  onRadiusChange: (r: SearchRadius) => void
  onLocate: () => void
  locating: boolean
  children: ReactNode
}

// 모바일: 하단 시트(탭으로 펼치기/접기), 데스크톱(md 이상): 왼쪽 패널에 항상 펼쳐짐
function BottomSheet({
  open,
  onToggle,
  title,
  subtitle,
  radius,
  onRadiusChange,
  onLocate,
  locating,
  children,
}: BottomSheetProps) {
  return (
    <section className="pointer-events-auto relative flex flex-col rounded-t-3xl bg-white shadow-[0_-8px_30px_rgba(0,0,0,0.12)] md:min-h-0 md:flex-1 md:rounded-3xl md:shadow-lg md:ring-1 md:ring-black/5">
      <button
        type="button"
        onClick={onLocate}
        disabled={locating}
        aria-label="내 위치로 이동"
        className="absolute -top-14 right-3 flex h-11 w-11 items-center justify-center rounded-full bg-white text-blue-600 shadow-lg ring-1 ring-black/5 transition active:scale-95 disabled:opacity-60 md:hidden"
      >
        <LocateIcon />
      </button>

      <button
        type="button"
        onClick={onToggle}
        aria-label={open ? '목록 접기' : '목록 펼치기'}
        className="flex w-full justify-center pt-2.5 pb-1 md:hidden"
      >
        <span className="h-1.5 w-10 rounded-full bg-gray-300" />
      </button>

      <div className="flex items-center justify-between gap-3 px-4 pt-1 pb-3 md:pt-4">
        <button type="button" onClick={onToggle} className="min-w-0 text-left md:pointer-events-none">
          <p className="truncate text-base font-bold">{title}</p>
          <p className="truncate text-xs text-gray-500">{subtitle}</p>
        </button>
        <div className="flex shrink-0 rounded-full bg-gray-100 p-1" role="group" aria-label="검색 반경">
          {radiusOptions.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => onRadiusChange(r)}
              aria-pressed={r === radius}
              className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                r === radius ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500'
              }`}
            >
              {r / 1000}km
            </button>
          ))}
        </div>
      </div>

      <div
        className={`${open ? 'block' : 'hidden'} max-h-[34vh] overflow-y-auto overscroll-contain border-t border-gray-100 px-3 pt-3 pb-[max(1rem,env(safe-area-inset-bottom))] md:block md:max-h-none md:flex-1`}
      >
        {children}
      </div>
    </section>
  )
}

export default BottomSheet
