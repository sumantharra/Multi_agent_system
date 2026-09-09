import { PageEmpty } from '../components/PageState'

export function ComingSoonPage({ title }: { title: string }) {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">{title}</h1>
      <section className="mt-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <PageEmpty message="This screen will be added in a follow-up. Use Hostels for now, or the API docs for deliveries, invoices, and payments." />
      </section>
    </div>
  )
}
