"use client"

import type React from "react"

import { useState } from "react"
import { Send, Paperclip, Smile } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface ChatInputProps {
  onSend: (message: string) => void
}

export function ChatInput({ onSend }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      onSend(message.trim())
      setMessage("")
    }
  }

  return (
    <div className="bg-card border-t border-border px-4 py-3 md:px-6 md:py-4">
      <form onSubmit={handleSubmit} className="flex items-center gap-2 md:gap-3">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="text-muted-foreground hover:text-foreground hidden md:flex"
        >
          <Paperclip className="h-5 w-5" />
          <span className="sr-only">Attach file</span>
        </Button>

        <div className="flex-1 relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message here..."
            className="pr-10 bg-muted/50 border-border focus-visible:ring-primary rounded-full py-5 md:py-6 text-sm md:text-base"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground h-8 w-8"
          >
            <Smile className="h-5 w-5" />
            <span className="sr-only">Add emoji</span>
          </Button>
        </div>

        <Button
          type="submit"
          size="icon"
          disabled={!message.trim()}
          className="rounded-full h-10 w-10 md:h-12 md:w-12 bg-primary hover:bg-primary/90 text-primary-foreground shadow-md transition-all disabled:opacity-50"
        >
          <Send className="h-4 w-4 md:h-5 md:w-5" />
          <span className="sr-only">Send message</span>
        </Button>
      </form>

      <p className="text-[10px] md:text-xs text-muted-foreground text-center mt-2">
        University Assistant may provide general information. For official inquiries, please contact the registrar.
      </p>
    </div>
  )
}
