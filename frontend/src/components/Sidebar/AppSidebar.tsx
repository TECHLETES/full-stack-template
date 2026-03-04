import { Briefcase, Home, Shield, Zap } from "lucide-react"

import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const primaryItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Briefcase, title: "Items", path: "/items" },
]

const adminItems: Item[] = [
  { icon: Shield, title: "Users", path: "/admin" },
  { icon: Zap, title: "Tasks", path: "/admin-tasks" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Menu
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <Main items={primaryItems} />
          </SidebarGroupContent>
        </SidebarGroup>
        {currentUser?.is_superuser && (
          <SidebarGroup>
            <SidebarGroupLabel className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Admin
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <Main items={adminItems} />
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarContent>
      <SidebarFooter>
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
