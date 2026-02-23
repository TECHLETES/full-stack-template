import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import { OpenAPI } from "@/client"
import useCustomToast from "./useCustomToast"

interface EntraLoginData {
  access_token: string
  tenant_id?: string
}

interface EntraLoginResponse {
  access_token: string
  token_type: string
}

async function entraLogin(data: EntraLoginData): Promise<EntraLoginResponse> {
  const baseUrl = OpenAPI.BASE || ""
  const response = await fetch(`${baseUrl}/api/v1/auth/entra/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Microsoft login failed")
  }

  return response.json()
}

const useEntraAuth = () => {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()

  const entraLoginMutation = useMutation({
    mutationFn: entraLogin,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token)
      navigate({ to: "/" })
    },
    onError: (error: Error) => {
      showErrorToast(error.message)
    },
  })

  return { entraLoginMutation }
}

export default useEntraAuth
