import { GraduationCap, Bell, Settings, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function AdminHeader() {
  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="flex items-center justify-between px-4 py-3 md:px-6 md:py-4">
        <div className="flex items-center gap-3">
          {/* Logo placeholder */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-card flex items-center justify-center shadow-md">
              <GraduationCap className="h-6 w-6 md:h-7 md:w-7 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-base md:text-lg leading-tight">Admin Dashboard</h1>
              <p className="text-xs md:text-sm text-primary-foreground/80">Knowledge Base Manager</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
         
          <div className="hidden md:flex items-center gap-3 pl-3 border-l border-primary-foreground/20">
            <Avatar className="h-8 w-8 border-2 border-primary-foreground/30">
              <AvatarFallback className="bg-secondary text-secondary-foreground text-sm">AD</AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium">Admin</span>
          </div>
          <Button variant="ghost" size="icon" className="text-primary-foreground hover:bg-primary/80">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>

     
    </header>
  )
}
