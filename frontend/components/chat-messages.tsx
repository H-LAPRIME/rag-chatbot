import type React from "react"
import { cn } from "@/lib/utils"
import { Bot, User } from "lucide-react"
import type { Message } from "./chat-interface"

interface ChatMessagesProps {
  messages: Message[]
  isTyping: boolean
  messagesEndRef: React.RefObject<HTMLDivElement | null>
}

export function ChatMessages({ messages, isTyping, messagesEndRef }: ChatMessagesProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6 space-y-4 bg-muted/30">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-3 max-w-[85%] md:max-w-[75%]",
            message.sender === "user" ? "ml-auto flex-row-reverse" : "",
          )}
        >
          {/* Avatar */}
          <div
            className={cn(
              "flex-shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm",
              message.sender === "bot"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground",
            )}
          >
            {message.sender === "bot" ? (
              <Bot className="h-4 w-4 md:h-5 md:w-5" />
            ) : (
              <User className="h-4 w-4 md:h-5 md:w-5" />
            )}
          </div>

          {/* Message bubble */}
          <div
            className={cn(
              "rounded-2xl px-4 py-3 shadow-sm",
              message.sender === "bot"
                ? "bg-card text-card-foreground rounded-tl-sm border border-border"
                : "bg-primary text-primary-foreground rounded-tr-sm",
            )}
          >
            <p className="text-sm md:text-base leading-relaxed">{message.content}</p>
            <p
              className={cn(
                "text-[10px] md:text-xs mt-2",
                message.sender === "bot" ? "text-muted-foreground" : "text-primary-foreground/70",
              )}
            >
              {formatTime(message.timestamp)}
            </p>
          </div>
        </div>
      ))}

      {/* Typing indicator */}
      {isTyping && (
        <div className="flex gap-3 max-w-[85%] md:max-w-[75%]">
          <div className="flex-shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-sm">
            <Bot className="h-4 w-4 md:h-5 md:w-5" />
          </div>
          <div className="bg-card text-card-foreground rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-border">
            <div className="flex gap-1.5 items-center h-6">
              <span className="w-2 h-2 rounded-full bg-secondary animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-secondary animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-secondary animate-bounce" />
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}
