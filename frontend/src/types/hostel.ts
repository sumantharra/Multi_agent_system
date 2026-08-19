export type Hostel = {
  id: string
  name: string
  code: string
  address: string | null
  contact_name: string | null
  phone: string | null
  default_rate_per_liter: string
  active: boolean
  created_at: string
  updated_at: string
}

export type HostelCreate = {
  name: string
  code: string
  address?: string | null
  contact_name?: string | null
  phone?: string | null
  default_rate_per_liter: string
}

export type PaginatedHostels = {
  items: Hostel[]
  page: number
  page_size: number
  total: number
}
