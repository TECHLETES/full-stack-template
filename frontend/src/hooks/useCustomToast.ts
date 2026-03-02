import { toast } from "sonner"

const useCustomToast = () => {
  const showSuccessToast = (description: string) => {
    toast.success("Success!", {
      description,
    })
  }

  const showErrorToast = (description: string) => {
    toast.error("Something went wrong!", {
      description,
    })
  }

  const showToast = (
    title: string,
    description: string,
    type: "success" | "error",
  ) => {
    if (type === "success") {
      toast.success(title, {
        description,
      })
    } else if (type === "error") {
      toast.error(title, {
        description,
      })
    }
  }

  return { showSuccessToast, showErrorToast, showToast }
}

export default useCustomToast
