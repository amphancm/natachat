"use client"
import { NavLink, useLocation } from "react-router-dom"
import { FileText, Upload, Target, Package, MessageSquare, MessageCircle, Settings, LogOut } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter, 
  useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button" 
import natachatLogo from "@/assets/natachat-logo.png"
import { useNavigate } from "react-router-dom";
import api from "@/lib/api";

const menuItems = [
  { title: "Chat", url: "/chat", icon: MessageCircle },
  { title: "Documents", url: "/documents", icon: FileText },
  // { title: "Upload Documents Files", url: "/upload-files", icon: Upload },
  { title: "System Prompt", url: "/system-prompt", icon: Target },
  // { title: "Product", url: "/product", icon: Package },
  // { title: "User Feedback", url: "/user-feedback", icon: MessageSquare },
  { title: "Settings", url: "/settings", icon: Settings },
]

export function AppSidebar() {
  const navigate = useNavigate();
  const { state } = useSidebar()
  const location = useLocation()
  const currentPath = location.pathname

  const isActive = (path: string) => currentPath === path
  const isCollapsed = state === "collapsed"

  const handleLogout = () => {
    api.clearToken();
    navigate("/")
  }

  return (
    <Sidebar className={isCollapsed ? "w-14" : "w-64"} collapsible="icon">
      <SidebarContent className="bg-sidebar">
        {/* Logo Section */}
        <div className="flex items-center gap-3 p-4 border-b border-sidebar-border">
          <img
            src={natachatLogo || "/placeholder.svg"}
            alt="Natachat AI"
            className={isCollapsed ? "w-8 h-4" : "w-8 h-7"}
          />
          {!isCollapsed && (
            <div className="flex items-center gap-1">
              <span className="font-semibold text-sidebar-foreground">Natachat</span>
              <span className="font-semibold text-primary">AI</span>
            </div>
          )}
        </div>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      className={({ isActive }) =>
                        `flex items-center gap-3 rounded-lg px-3 py-2 transition-colors ${
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                        }`
                      }
                    >
                      <item.icon className="h-4 w-4" />
                      {!isCollapsed && <span className="text-sm">{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Button
                variant="ghost"
                onClick={handleLogout}
                className="w-full justify-start gap-3 px-3 py-2 h-auto text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              >
                <LogOut className="h-4 w-4" />
                {!isCollapsed && <span className="text-sm">Logout</span>}
              </Button>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
