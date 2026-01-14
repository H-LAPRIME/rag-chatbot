"use client"

import { useState, useRef, useEffect } from "react"
import { ChatHeader } from "./chat-header"
import { ChatMessages } from "./chat-messages"
import { ChatInput } from "./chat-input"
import { QuickActions } from "./quick-actions"
import axios from "axios"
import { API_URL } from "@/lib/utils"

export interface Message {
  id: string
  content: string
  sender: "user" | "bot"
  timestamp: Date
}

const initialMessages: Message[] = [
  {
    id: "1",
    content: JSON.stringify({
      intro_message: "Hello! 👋 Welcome to the University Assistant. I'm here to help you with admissions, course information, campus services, and more. How can I assist you today?",
      content: {
        structured: [],
        rawtext: ""
      }
    }),
    sender: "bot",
    timestamp: new Date(),
  },
]

const botResponses: Record<string, string> = {
  admission:
    "For admissions inquiries, you can apply online through our portal at admissions.university.edu. Application deadlines are December 1st for Early Decision and January 15th for Regular Decision. Would you like more information about specific programs?",
  courses:
    "We offer over 200 undergraduate and graduate programs across 12 colleges. You can browse our course catalog at catalog.university.edu or use our degree planner tool. What field of study interests you?",
  financial:
    "Financial aid information is available through our Student Financial Services office. We offer scholarships, grants, loans, and work-study programs. The FAFSA priority deadline is March 1st. Need help with a specific financial aid question?",
  housing:
    "On-campus housing includes traditional residence halls, suite-style living, and apartments. Housing applications open March 15th for incoming freshmen. Current students can apply for housing lottery in February.",
  default:
    "Thank you for your question. I'm processing your request. For immediate assistance, you can also contact our Student Services office at (555) 123-4567 or email support@university.edu. Is there anything specific I can help you with?",
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setMessages(initialMessages)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getBotResponse = async (userMessage: string): Promise<string> => {
    try {
      const response = await axios.post(`${API_URL}/api/chat`, { message: userMessage });
      return response.data.reply || JSON.stringify({ intro_message: botResponses['default'] });
    } catch (err) {
      console.error("Error in getBotResponse:", err);
    }
    return JSON.stringify({ intro_message: botResponses['default'] });
  }

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsTyping(true)

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: await getBotResponse(content),
      sender: "bot",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, botMessage])
    setIsTyping(false)

  }

  const handleQuickAction = (action: string) => {
    handleSendMessage(action)
  }

  return (
    <div className="flex flex-col h-screen w-full mx-auto">
      <ChatHeader />
      <div className="flex-1 overflow-hidden flex flex-col">
        <ChatMessages messages={messages} isTyping={isTyping} messagesEndRef={messagesEndRef} />
        <QuickActions onAction={handleQuickAction} />
        <ChatInput onSend={handleSendMessage} />
      </div>
    </div>
  )
}
