export function PageLoading({ message }: { message: string }) {
  return <p className="mt-4 text-slate-600">{message}</p>
}

export function PageEmpty({ message }: { message: string }) {
  return <p className="mt-4 text-slate-600">{message}</p>
}

export function PageError({ message }: { message: string }) {
  return <p className="mt-4 text-red-600">{message}</p>
}
