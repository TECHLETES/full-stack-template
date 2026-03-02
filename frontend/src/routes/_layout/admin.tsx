import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense, useState } from "react"

import { NotificationsService, type UserPublic, UsersService } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { columns, type UserTableData } from "@/components/Admin/columns"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: ["users"],
  }
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!user.is_superuser) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Admin - FastAPI Template",
      },
    ],
  }),
})

function UsersTableContent() {
  const { user: currentUser } = useAuth()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const tableData: UserTableData[] = users.data.map((user: UserPublic) => ({
    ...user,
    isCurrentUser: currentUser?.id === user.id,
  }))

  return <DataTable columns={columns} data={tableData} />
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  )
}

function TestNotificationButton() {
  const [isLoading, setIsLoading] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleSendTestNotification = async () => {
    setIsLoading(true)
    try {
      const response = await NotificationsService.sendTestNotificationToAll()
      showSuccessToast(response.message)
    } catch (error) {
      showErrorToast(
        error instanceof Error
          ? error.message
          : "Failed to send test notification",
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Button
      onClick={handleSendTestNotification}
      disabled={isLoading}
      variant="outline"
    >
      {isLoading ? "Sending..." : "Send Test Notification"}
    </Button>
  )
}

function Admin() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-muted-foreground">
            Manage user accounts and permissions
          </p>
        </div>
        <div className="flex gap-2 my-4">
          <TestNotificationButton />
          <AddUser />
        </div>
      </div>
      <UsersTable />
    </div>
  )
}
