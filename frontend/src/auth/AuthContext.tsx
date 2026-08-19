import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { getMe, login as loginRequest, logout as logoutRequest } from '../api/auth'
import { setAccessTokenGetter } from '../api/client'
import type { AuthUser } from '../types/auth'

const TOKEN_KEY = 'rrvma_access_token'

type AuthContextValue = {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setAccessTokenGetter(() => token)
  }, [token])

  useEffect(() => {
    let cancelled = false
    async function loadUser() {
      if (!token) {
        setUser(null)
        setLoading(false)
        return
      }
      try {
        const me = await getMe()
        if (!cancelled) {
          setUser(me)
        }
      } catch {
        if (!cancelled) {
          sessionStorage.removeItem(TOKEN_KEY)
          setToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    void loadUser()
    return () => {
      cancelled = true
    }
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    const result = await loginRequest(email, password)
    sessionStorage.setItem(TOKEN_KEY, result.access_token)
    setToken(result.access_token)
    const me = await getMe()
    setUser(me)
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutRequest()
    } catch {
      // ignore network errors on logout
    }
    sessionStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, token, loading, login, logout }),
    [user, token, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
