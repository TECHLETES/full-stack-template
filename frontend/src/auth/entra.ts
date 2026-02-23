import {
  type Configuration,
  LogLevel,
  PublicClientApplication,
} from "@azure/msal-browser"
import type { EntraConfigResponse } from "@/client"

let msalInstance: PublicClientApplication | null = null
let entraConfig: EntraConfigResponse | null = null

export const loginScopes = ["openid", "profile", "email", "User.Read"]

export const isEntraEnabled = (): boolean => {
  return Boolean(entraConfig?.client_id)
}

export const getMsalInstance = (): PublicClientApplication => {
  if (!msalInstance) {
    throw new Error("MSAL not initialized. Call initEntra() first.")
  }
  return msalInstance
}

export const initEntra = async (): Promise<void> => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/entra/config`)
    if (!response.ok) return
    
    entraConfig = await response.json()
    
    if (!entraConfig.client_id) return
    
    const msalConfig: Configuration = {
      auth: {
        clientId: entraConfig.client_id,
        authority: entraConfig.authority,
        redirectUri: window.location.origin,
        postLogoutRedirectUri: "/",
      },
      cache: {
        cacheLocation: "localStorage",
      },
      system: {
        loggerOptions: {
          loggerCallback: (_level, message) => {
            if (_level === LogLevel.Error) console.error(message)
          },
          logLevel: LogLevel.Error,
        },
      },
    }
    
    msalInstance = new PublicClientApplication(msalConfig)
  } catch (error) {
    console.error("Failed to initialize Entra:", error)
  }
}
