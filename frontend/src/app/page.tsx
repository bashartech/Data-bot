"use client"

export const dynamic = "force-dynamic"

import { useState, useRef, useEffect, useCallback } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { useAuth } from "@/lib/auth-context"
import { api, type Conversation, type Message } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent } from "@/components/ui/sheet"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Send,
  Menu,
  Plus,
  Trash2,
  LogOut,
  Sun,
  Moon,
  MessageSquare,
} from "lucide-react"
import { useTheme } from "@/components/theme-provider"

export default function Home() {
  const { user, loading, loginWithGoogle, logout } = useAuth()

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    )
  }

  if (!user) {
    return <LoginScreen onLogin={loginWithGoogle} />
  }

  return <ChatApp user={user} onLogout={logout} />
}

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4">
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Enterprise AI Chatbot</h1>
        <p className="text-muted-foreground max-w-sm">
          Ask questions about products and get instant answers powered by AI.
        </p>
      </div>
      <Button size="lg" className="gap-2" onClick={onLogin}>
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Login with Google
      </Button>
    </div>
  )
}

interface ChatAppProps {
  user: { id: string; email: string; name: string; picture: string | null }
  onLogout: () => void
}

function ChatApp({ user, onLogout }: ChatAppProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConvId, setCurrentConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const [showTyping, setShowTyping] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const hasFirstTokenRef = useRef(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    if (currentConvId) {
      api.conversations.messages(currentConvId).then(setMessages)
    } else {
      setMessages([])
    }
  }, [currentConvId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const loadConversations = async () => {
    try {
      const list = await api.conversations.list()
      setConversations(list || [])
    } catch {
      // ignore
    }
  }

  const handleNewChat = () => {
    setCurrentConvId(null)
    setMessages([])
    setInput("")
  }

  const handleDeleteConv = async (id: string) => {
    try {
      await api.conversations.delete(id)
      setConversations((prev) => prev.filter((c) => c.id !== id))
      if (currentConvId === id) {
        setCurrentConvId(null)
        setMessages([])
      }
    } catch {
      // ignore
    }
  }

  const handleSend = useCallback(async () => {
    if (!input.trim() || streaming) return
    const msg = input.trim()
    setInput("")
    setStreaming(true)
    setShowTyping(true)
    hasFirstTokenRef.current = false

    const userMsg: Message = {
      id: "temp-user",
      role: "user",
      content: msg,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      const response = await api.chat.send(msg, currentConvId || undefined)
      if (!response.ok) {
        throw new Error("Chat request failed")
      }
      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let collected = ""
      let newConvId = currentConvId

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split("\n")
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === "token") {
              if (!hasFirstTokenRef.current) {
                hasFirstTokenRef.current = true
                setShowTyping(false)
              }
              collected += data.content
              setMessages((prev) => {
                const copy = [...prev]
                if (copy.length > 0 && copy[copy.length - 1].id === "temp-ai") {
                  copy[copy.length - 1] = {
                    ...copy[copy.length - 1],
                    content: collected,
                  }
                } else {
                  copy.push({
                    id: "temp-ai",
                    role: "assistant",
                    content: collected,
                    created_at: new Date().toISOString(),
                  })
                }
                return copy
              })
            } else if (data.type === "done") {
              newConvId = data.conversation_id
            } else if (data.type === "error") {
              console.error("Chat error:", data.content)
            }
          } catch {
            // ignore parse errors
          }
        }
      }

      setCurrentConvId(newConvId)
      await loadConversations()
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: "temp-error",
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setShowTyping(false)
      setStreaming(false)
    }
  }, [input, streaming, currentConvId])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const initials = user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  const showTypingIndicator = streaming && showTyping

  function SidebarContent() {
    return (
      <>
        <div className="p-3">
          <Button variant="outline" className="w-full justify-start gap-2" onClick={handleNewChat}>
            <Plus className="h-4 w-4" />
            New Chat
          </Button>
        </div>
        <Separator />
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {conversations.length === 0 && !streaming && (
              <p className="text-xs text-muted-foreground text-center py-4">No conversations yet</p>
            )}
            {conversations.length === 0 && streaming && (
              <p className="text-xs text-muted-foreground text-center py-4">Loading...</p>
            )}
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center justify-between gap-2 rounded-md px-3 py-2 text-sm cursor-pointer hover:bg-accent transition-colors ${
                  currentConvId === conv.id ? "bg-accent" : ""
                }`}
                onClick={() => setCurrentConvId(conv.id)}
              >
                <MessageSquare className="h-4 w-4 shrink-0" />
                <span className="truncate flex-1 text-left">{conv.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteConv(conv.id)
                  }}
                  className="shrink-0 opacity-0 group-hover:opacity-100 hover:text-destructive transition-opacity"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </>
    )
  }

  return (
    <div className="flex flex-1 h-screen overflow-hidden">
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-72">
          <div className="flex flex-col h-full" onClick={() => setSidebarOpen(false)}>
            <SidebarContent />
          </div>
        </SheetContent>
      </Sheet>

      <div className="hidden md:flex flex-col w-72 border-r bg-sidebar">
        <SidebarContent />
      </div>

      <div className="flex flex-col flex-1 min-w-0">
        <header className="flex items-center justify-between px-4 h-14 border-b shrink-0">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setSidebarOpen(true)}>
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="font-semibold text-sm">Enterprise AI Chatbot</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger className="outline-none">
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.picture || undefined} alt={user.name} />
                    <AvatarFallback>{initials}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <div className="px-2 py-1.5 text-sm">
                  <p className="font-medium">{user.name}</p>
                  <p className="text-muted-foreground truncate">{user.email}</p>
                </div>
                <Separator />
                <DropdownMenuItem onClick={onLogout} className="gap-2">
                  <LogOut className="h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <ScrollArea className="flex-1 px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center gap-2">
              <MessageSquare className="h-12 w-12 text-muted-foreground/50" />
              <h2 className="text-xl font-semibold">Ask about products</h2>
              <p className="text-muted-foreground max-w-sm">
                Ask about product details, pricing, availability, and more.
              </p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`rounded-lg px-4 py-2.5 max-w-[80%] prose prose-sm dark:prose-invert ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground prose-headings:text-primary-foreground prose-a:text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content || ""}
                      </ReactMarkdown>
                    )}
                  </div>
                </div>
              ))}

              {showTypingIndicator && (
                <div className="flex gap-3 justify-start">
                  <div className="rounded-lg px-4 py-3 max-w-[80%] bg-muted">
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        <div className="border-t p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={streaming ? "AI is thinking..." : "Ask about products..."}
              disabled={streaming}
              className="flex-1"
            />
            <Button onClick={handleSend} disabled={!input.trim() || streaming} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
