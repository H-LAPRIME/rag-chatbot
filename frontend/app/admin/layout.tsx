import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { FileManager } from "@/components/admin/file-manager"
import { Toaster } from "@/components/ui/sonner"


export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode
}>) {
    return (
        <div className="min-h-screen bg-muted/30 flex flex-col">
            <AdminHeader />
            <div className="flex-1 flex">
                <AdminSidebar />
                <main className="flex-1 p-4 md:p-6 lg:p-8 overflow-auto">
                    <div className="max-w-6xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
            <Toaster />
        </div>
    )
}
