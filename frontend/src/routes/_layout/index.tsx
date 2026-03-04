import { createFileRoute } from "@tanstack/react-router"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - Techletes",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-sm text-muted-foreground">
          Welcome back, nice to see you again!
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-semibold">
            Getting Started
          </CardTitle>
          <CardDescription className="text-xs">
            Explore the application using the sidebar navigation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Use the sidebar to navigate to Items, Settings, or Admin features.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
