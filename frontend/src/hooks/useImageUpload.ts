import { useMutation } from "@tanstack/react-query"
import { Upload } from "@/client"

/**
 * Convert a File to base64 string.
 */
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * Hook for uploading images to the backend.
 *
 * Handles file-to-base64 conversion and uploads via POST /api/v1/upload/image.
 * Returns an attachment_id that can be used in chat messages.
 */
export function useImageUpload() {
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      // Read file as base64 data URL
      const dataUrl = await fileToBase64(file)
      // Remove data URL prefix (e.g., "data:image/jpeg;base64,")
      const base64Data = dataUrl.split(",")[1]

      // Upload to backend
      const response = await Upload.uploadUploadImage({
        body: {
          image_base64: base64Data,
          content_type: file.type || "image/jpeg",
        },
      })

      if (response.error) {
        throw response.error
      }

      return response.data.attachmentId
    },
  })

  return {
    uploadImage: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    uploadError: uploadMutation.error,
    reset: uploadMutation.reset,
  }
}
