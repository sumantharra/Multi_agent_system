export type AuthUser = {
  id: string
  email: string
  role: string
  active: boolean
}

export type TokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
}

export type BrandInfo = {
  name: string
  domain: string
}
