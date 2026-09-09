import type { Hostel } from '../types/hostel'

export function hostelLabel(hostels: Hostel[], id: string): string {
  const hostel = hostels.find((item) => item.id === id)
  if (!hostel) {
    return id
  }
  return `${hostel.name} (${hostel.code})`
}
