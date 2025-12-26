"use client"

import { BookOpen, GraduationCap, Home, DollarSign } from "lucide-react"
import { Button } from "@/components/ui/button"

interface QuickActionsProps {
  onAction: (action: string) => void
}

const quickActions = [
  { label: "Admissions", icon: GraduationCap, query: "Tell me about admissions and how to apply" },
  { label: "Courses", icon: BookOpen, query: "What courses and programs do you offer?" },
  { label: "Housing", icon: Home, query: "What are the housing options available?" },
  { label: "Financial Aid", icon: DollarSign, query: "Tell me about financial aid and scholarships" },
]

export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <div className="bg-card border-t border-border px-4 py-3 md:px-6">
      <p className="text-xs text-muted-foreground mb-2 font-medium">Quick Actions</p>
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        {quickActions.map((action) => (
          <Button
            key={action.label}
            variant="outline"
            size="sm"
            onClick={() => onAction(action.query)}
            className="flex-shrink-0 gap-1.5 rounded-full text-xs md:text-sm border-border hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <action.icon className="h-3.5 w-3.5 md:h-4 md:w-4" />
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
