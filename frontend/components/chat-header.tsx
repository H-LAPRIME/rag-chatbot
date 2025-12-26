import { GraduationCap, Menu, MoreVertical } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ChatHeader() {
  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="flex items-center justify-between px-4 py-3 md:px-6 md:py-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="md:hidden text-primary-foreground hover:bg-primary/80">
            <Menu className="h-5 w-5" />
          </Button>

          {/* Logo placeholder */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-card flex items-center justify-center shadow-md">
              <GraduationCap className="h-6 w-6 md:h-7 md:w-7 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-base md:text-lg leading-tight">University Assistant</h1>
              <p className="text-xs md:text-sm text-primary-foreground/80">Student Support Chat</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-2 text-sm text-primary-foreground/80">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              Online
            </span>
          </div>
          <Button variant="ghost" size="icon" className="text-primary-foreground hover:bg-primary/80">
            <MoreVertical className="h-5 w-5" />
          </Button>
        </div>
      </div>

    
    </header>
  )
}
