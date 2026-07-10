"use client"

import { Suspense, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

function CallbackHandler() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { setToken } = useAuth()
  const processed = useRef(false)

  useEffect(() => {
    if (processed.current) return
    processed.current = true

    const token = searchParams.get("token")
    if (token) {
      setToken(token)
    }
    router.replace("/")
  }, [searchParams, setToken, router])

  return (
    <div className="flex flex-1 items-center justify-center">
      <p className="text-muted-foreground">Signing you in...</p>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-1 items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    }>
      <CallbackHandler />
    </Suspense>
  )
}
