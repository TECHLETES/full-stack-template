import { useQuery } from "@tanstack/react-query"
import { UtilsService } from "@/client"

const useAppConfig = () => {
  const {
    data: config,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["appConfig"],
    queryFn: UtilsService.getAppConfig,
  })

  return {
    config,
    isLoading,
    error,
  }
}

export default useAppConfig
