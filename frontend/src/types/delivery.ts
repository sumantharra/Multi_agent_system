export type Paginated<T> = {
  items: T[]
  page: number
  page_size: number
  total: number
}

export type Delivery = {
  id: string
  hostel_id: string
  delivery_date: string
  morning_quantity: string
  evening_quantity: string
  total_quantity: string
  rate_per_liter: string
  notes: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export type DeliveryCreate = {
  hostel_id: string
  delivery_date: string
  morning_quantity: string
  evening_quantity: string
  notes?: string | null
}
