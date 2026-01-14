import { GraduationCap, Menu, MoreVertical } from "lucide-react"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export function ChatHeader() {
  return (
    <header className="bg-primary text-primary-foreground shadow-lg">
      <div className="flex items-center justify-between px-4 py-3 md:px-6 md:py-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="md:hidden text-primary-foreground hover:bg-primary/80">
            <Menu className="h-5 w-5" />
          </Button>

          {/* Logo placeholder */}
          <div className="flex items-center gap-4">
            <Image
              src="/ENSET white.png"
              alt="Logo"
              width={40}
              height={40}
              className="w-32 h-auto object-contain"
            />
            <div>
              <h1 className="text-lg font-semibold">Chat with AI Tutor</h1>
              <p className="text-sm text-primary-foreground/80">Your personal learning assistant</p>
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
