import { createFileRoute } from "@tanstack/react-router"
import { Cloud, Lock, User } from "lucide-react"
import { type FC, useState } from "react"

import ChangePassword from "@/components/UserSettings/ChangePassword"
import UserInformation from "@/components/UserSettings/UserInformation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"
import { cn } from "@/lib/utils"

type TabValue = "my-profile" | "password"

interface TabConfig {
  value: TabValue
  title: string
  description: string
  icon: FC<{ className?: string }>
  component: FC
}

const TABS: TabConfig[] = [
  {
    value: "my-profile",
    title: "My Profile",
    description: "Update your personal information and email address",
    icon: User,
    component: UserInformation,
  },
  {
    value: "password",
    title: "Password & Security",
    description: "Change your password and manage account security",
    icon: Lock,
    component: ChangePassword,
  },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Settings - Techletes",
      },
    ],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()
  const [activeTab, setActiveTab] = useState<TabValue>("my-profile")

  if (!currentUser) {
    return null
  }

  // Check if user is managed by Azure Entra
  const isEntraManagedUser = !!(currentUser as any).azure_user_id

  const active = TABS.find((t) => t.value === activeTab) ?? TABS[0]
  const ActiveComponent = active.component

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      {isEntraManagedUser && (
        <Card className="border border-neutral-200 dark:border-neutral-800 bg-sky-50 dark:bg-slate-900/50">
          <CardContent className="py-2 px-6 flex items-start gap-3">
            <Cloud className="h-5 w-5 text-sky-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">
                Cloud-managed account
              </p>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-2">
                Your account is managed through Microsoft Entra. Please visit
                the Microsoft Entra portal to update your profile information.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-6 items-start">
        {/* Sidebar navigation */}
        <Card className="py-3 gap-0">
          <nav className="flex flex-col gap-1 px-2">
            {TABS.map((tab) => (
              <button
                key={tab.value}
                type="button"
                onClick={() => setActiveTab(tab.value)}
                disabled={isEntraManagedUser}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors text-left w-full",
                  isEntraManagedUser && "cursor-not-allowed opacity-50",
                  activeTab === tab.value
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted",
                )}
              >
                <tab.icon className="h-4 w-4 shrink-0" />
                {tab.title}
              </button>
            ))}
          </nav>
        </Card>

        {/* Content panel */}
        <Card className="gap-0 pb-0">
          <CardHeader className="border-b pb-6">
            <CardTitle className="text-lg">{active.title}</CardTitle>
            <CardDescription>{active.description}</CardDescription>
          </CardHeader>
          <CardContent className="py-6">
            {isEntraManagedUser ? (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground">
                  This setting is not available for Microsoft Entra managed
                  accounts.
                </p>
              </div>
            ) : (
              <ActiveComponent />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
