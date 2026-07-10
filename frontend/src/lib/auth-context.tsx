"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api, type User } from "./api"

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string) => Promise<void>
  loginWithGoogle: () => void
  logout: () => Promise<void>
  setToken: (token: string) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      setLoading(false)
      return
    }
    api.auth.me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token")
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email: string) => {
    const res = await api.auth.login(email)
    localStorage.setItem("token", res.access_token)
    setUser(res.user)
  }

  const loginWithGoogle = () => {
    api.auth.googleLogin()
  }

  const logout = async () => {
    try {
      await api.auth.logout()
    } catch {
      // ignore
    }
    localStorage.removeItem("token")
    setUser(null)
  }

  const setToken = (token: string) => {
    localStorage.setItem("token", token)
    api.auth.me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token")
      })
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithGoogle, logout, setToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
