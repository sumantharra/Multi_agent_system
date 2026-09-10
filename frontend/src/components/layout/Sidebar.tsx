import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/hostels', label: 'Hostels' },
  { to: '/deliveries', label: 'Deliveries' },
  { to: '/invoices', label: 'Invoices' },
  { to: '/payments', label: 'Payments' },
  { to: '/upload', label: 'Upload' },
] as const

export function Sidebar() {
  return (
    <aside className="flex w-full flex-col border-b border-emerald-100 bg-white md:w-60 md:border-b-0 md:border-r">
      <div className="border-b border-emerald-50 px-5 py-5">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">
          rrvijayamilkagencies.com
        </p>
        <p className="mt-2 text-sm font-semibold text-slate-900">RR Vijaya Milk Agencies</p>
      </div>
      <nav className="flex flex-row gap-1 overflow-x-auto p-3 md:flex-col" aria-label="Main">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                'whitespace-nowrap rounded-xl px-3 py-2 text-sm font-medium',
                isActive
                  ? 'bg-emerald-700 text-white'
                  : 'text-slate-700 hover:bg-emerald-50 hover:text-emerald-900',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
