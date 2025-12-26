"use client"

import { useEffect, useState } from "react"
import {  Loader2 } from "lucide-react"

interface IndexingOverlayProps {
  isOpen: boolean
  message: string
  title : string
  prog : string
}

export function IndexingOverlay({ isOpen, message , title , prog}: IndexingOverlayProps) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (isOpen) {
      setProgress(0)

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval)
            return 100
          }

          // Update phase based on progress

          return prev + Math.random() * 15 + 5
        })
      }, 400)

      return () => clearInterval(interval)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 backdrop-blur-sm">
      <div className="bg-card rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 border border-border">
        {/* Header */}
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            {/* Animated rings */}
            <div
              className="absolute inset-0 rounded-full border-4 border-primary/20 animate-ping"
              style={{ animationDuration: "2s" }}
            />
            <div
              className="absolute inset-0 rounded-full border-4 border-primary/30 animate-ping"
              style={{ animationDuration: "2s", animationDelay: "0.5s" }}
            />

            {/* Center icon */}
           
          </div>
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-center text-foreground mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground text-center mb-6">{message}</p>


        {/* Progress bar */}
        <div className="mb-4">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <div className="flex justify-end mt-1">
            <span className="text-xs text-muted-foreground">{Math.min(Math.round(progress), 100)}%</span>
          </div>
        </div>

        {/* Phase indicator */}
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>{prog}</span>
        </div>
      

        {/* Animated dots */}
        <div className="mt-6 flex justify-center gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-primary animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
