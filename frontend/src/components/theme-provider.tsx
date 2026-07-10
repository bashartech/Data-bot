"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

type Theme = "dark" | "light" | "system"

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
  attribute?: string
  defaultTheme?: Theme
  enableSystem?: boolean
}

export function ThemeProvider({
  children,
  attribute = "class",
  defaultTheme = "system",
  enableSystem = true,
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(defaultTheme)

  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme | null
    if (saved) {
      setThemeState(saved)
    }
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (attribute === "class") {
      root.classList.remove("light", "dark")
      if (theme === "system" && enableSystem) {
        const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches
        root.classList.add(systemDark ? "dark" : "light")
      } else {
        root.classList.add(theme)
      }
    }
  }, [theme, attribute, enableSystem])

  const setTheme = (t: Theme) => {
    localStorage.setItem("theme", t)
    setThemeState(t)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider")
  return ctx
}
