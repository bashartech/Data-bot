const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 204) {
    return undefined as T
  }

  const data = await res.json()
  if (!res.ok) {
    throw new ApiError(data.detail || "Request failed", res.status)
  }
  return data
}

export interface User {
  id: string
  email: string
  name: string
  picture: string | null
  created_at: string
  last_login: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Conversation {
  id: string
  title: string
  created_at: string
}

export interface Message {
  id: string
  role: string
  content: string
  created_at: string
}

export interface Product {
  id: string
  product_name: string
  category: string
  description: string
  price: number
  stock: number
  manufacturer: string
  created_at: string
}

export interface ProductDetail extends Product {
  specifications: string | null
  warranty: string | null
  country: string | null
  weight: number | null
}

export const api = {
  auth: {
    login: (email: string) =>
      request<LoginResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email }),
      }),
    me: () => request<User>("/auth/me"),
    logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),
    googleLogin: () => {
      window.location.href = `${API_BASE}/auth/login`
    },
  },

  conversations: {
    list: () => request<Conversation[]>("/conversations"),
    create: (title = "New Chat") =>
      request<Conversation>("/conversations", {
        method: "POST",
        body: JSON.stringify({ title }),
      }),
    get: (id: string) => request<Conversation>(`/conversations/${id}`),
    rename: (id: string, title: string) =>
      request<Conversation>(`/conversations/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ title }),
      }),
    delete: (id: string) =>
      request<void>(`/conversations/${id}`, { method: "DELETE" }),
    messages: (id: string) =>
      request<Message[]>(`/conversations/${id}/messages`),
  },

  chat: {
    send: (message: string, conversationId?: string) => {
      const url = `${API_BASE}/chat`
      return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId || null,
        }),
      })
    },
  },

  products: {
    list: (skip = 0, limit = 20) =>
      request<Product[]>(`/products?skip=${skip}&limit=${limit}`),
    search: (q: string, limit = 10) =>
      request<Product[]>(`/products/search?q=${encodeURIComponent(q)}&limit=${limit}`),
    get: (id: string) => request<ProductDetail>(`/products/${id}`),
  },
}
