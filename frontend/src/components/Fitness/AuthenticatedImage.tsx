import { Flex, Spinner, Text } from "@chakra-ui/react"
import { useEffect, useState } from "react"

interface AuthenticatedImageProps {
  attachmentId: string
}

/**
 * Component to load images with authentication.
 * Fetches images from the backend using the user's auth token.
 */
export function AuthenticatedImage({ attachmentId }: AuthenticatedImageProps) {
  const [imageSrc, setImageSrc] = useState<string | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let objectUrl: string | null = null
    const loadImage = async () => {
      try {
        const token = localStorage.getItem("fitness_copilot_token")
        const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const response = await fetch(
          `${baseUrl}/api/v1/upload/image/${attachmentId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        )
        if (!response.ok) throw new Error("Failed to load image")
        const blob = await response.blob()
        objectUrl = URL.createObjectURL(blob)
        setImageSrc(objectUrl)
      } catch {
        setError(true)
      }
    }
    loadImage()
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [attachmentId])

  if (error) {
    return (
      <Flex
        bg="gray.100"
        p={4}
        align="center"
        justify="center"
        borderRadius="lg"
        minH="80px"
      >
        <Text fontSize="2xl">📷</Text>
        <Text fontSize="sm" color="gray.500" ml={2}>
          Image
        </Text>
      </Flex>
    )
  }

  if (!imageSrc) {
    return (
      <Flex
        bg="gray.100"
        p={4}
        align="center"
        justify="center"
        borderRadius="lg"
        minH="80px"
      >
        <Spinner size="sm" />
      </Flex>
    )
  }

  return (
    <img
      src={imageSrc}
      alt="Uploaded"
      style={{
        maxHeight: "150px",
        maxWidth: "100%",
        objectFit: "cover",
        borderRadius: "8px",
      }}
    />
  )
}
