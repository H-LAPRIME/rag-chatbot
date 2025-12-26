"use client"

import type React from "react"

import { useState } from "react"
import {
  FolderOpen,
  MessageSquare,
  BarChart3,
  Settings,
  Users,
  History,
  ChevronLeft,
  ChevronRight,
  Database,
  Shield,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
  active?: boolean
  badge?: string
}

const navItems_data: NavItem[] = [
  { icon: FolderOpen, label: "Knowledge Base", href: "/admin", active: true },
  { icon: MessageSquare, label: "Chat", href: "/admin/logs" },
  { icon: History, label: "Data", href: "/admin/data" },
  { icon: Settings, label: "Settings", href: "/admin/settings" },
]

export function AdminSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [navItems, setNavItems] = useState<NavItem[]>(navItems_data);

  const updateItemsActivity = (href: string) => {
    const updatedItems = navItems.map(item => {
      // Return a new object for each item with the change
      return item.href!=href ? { ...item, active: false } : { ...item, active: true };
    });
    setNavItems(updatedItems);
   }

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col bg-card border-r border-border transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Toggle button */}
      <div className="flex justify-end p-2 border-b border-border">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8 text-muted-foreground hover:text-foreground"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            onClick={()=> updateItemsActivity(item.href)}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
              item.active
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted",
            )}
          >
            <item.icon className={cn("h-5 w-5 shrink-0", item.active ? "text-primary-foreground" : "text-secondary")} />

            {!collapsed && (
              <>
                <span className="font-medium text-sm">{item.label}</span>
                {item.badge && (
                  <span
                    className={cn(
                      "ml-auto text-xs px-2 py-0.5 rounded-full",
                      item.active ? "bg-primary-foreground/20 text-primary-foreground" : "bg-primary/10 text-primary",
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </>
            )}

            {/* Tooltip for collapsed state */}
            {collapsed && (
              <div className="absolute left-full ml-2 px-2 py-1 bg-foreground text-background text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                {item.label}
              </div>
            )}
          </Link>
        ))}
      </nav>

      {/* Bottom section */}
      {!collapsed && (
        <div className="p-4 border-t border-border">
          <div className="p-3 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-medium text-foreground">System Status</span>
            </div>
            <p className="text-xs text-muted-foreground">All services operational</p>
          </div>
        </div>
      )}
    </aside>
  )
}
