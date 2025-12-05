import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Chat } from "@/client"
import type {
  ChatMessageCreate,
  ChatMessagePublic,
  ChatMessagesPublic,
} from "@/client/types.gen"

export const CHAT_QUERY_KEY = ["chat", "messages"]
export const LOGS_QUERY_KEY = ["logs", "today"]
export const SUMMARY_QUERY_KEY = ["summary", "today"]

/**
 * Hook for managing chat messages with the Brain service.
 *
 * Handles fetching chat history and sending new messages.
 * Automatically invalidates logs and summary queries when
 * food or exercise is logged via chat.
 */
export function useChat(enabled = true) {
  const queryClient = useQueryClient()

  const messagesQuery = useQuery({
    queryKey: CHAT_QUERY_KEY,
    queryFn: async () => {
      const response = await Chat.chatGetMessages({ query: { limit: 100 } })
      if (response.error) {
        throw response.error
      }
      return response.data as ChatMessagesPublic
    },
    enabled,
    staleTime: 1000 * 30, // 30 seconds
  })

  const sendMutation = useMutation({
    mutationFn: async (message: ChatMessageCreate) => {
      // Optimistically add user message to cache immediately
      const tempUserMessage: ChatMessagePublic = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: message.content,
        actionType: "none",
        actionData: null,
        attachmentType: message.attachment_type ?? "none",
        attachmentUrl: message.attachment_url ?? null,
        createdAt: new Date().toISOString(),
      }
      queryClient.setQueryData<ChatMessagesPublic>(CHAT_QUERY_KEY, (old) => {
        if (!old) return { data: [tempUserMessage], count: 1 }
        return {
          data: [...old.data, tempUserMessage],
          count: old.count + 1,
        }
      })

      const response = await Chat.chatSendMessage({ body: message })
      if (response.error) {
        throw response.error
      }
      return response.data as ChatMessagePublic
    },
    onSuccess: (response) => {
      // Add assistant response to cache (user message already added optimistically)
      queryClient.setQueryData<ChatMessagesPublic>(CHAT_QUERY_KEY, (old) => {
        if (!old) return { data: [response], count: 1 }
        return {
          data: [...old.data, response],
          count: old.count + 1,
        }
      })

      // Invalidate logs and summary if action was log_food, log_exercise, or reset
      if (
        response.actionType === "log_food" ||
        response.actionType === "log_exercise" ||
        response.actionType === "reset"
      ) {
        queryClient.invalidateQueries({ queryKey: LOGS_QUERY_KEY })
        queryClient.invalidateQueries({ queryKey: SUMMARY_QUERY_KEY })
      }
    },
    onError: () => {
      // On error, refetch to get correct state
      queryClient.invalidateQueries({ queryKey: CHAT_QUERY_KEY })
    },
  })

  const clearMutation = useMutation({
    mutationFn: async () => {
      const response = await Chat.chatClearMessages()
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    onSuccess: () => {
      // Clear the chat cache
      queryClient.setQueryData<ChatMessagesPublic>(CHAT_QUERY_KEY, {
        data: [],
        count: 0,
      })
      // Also invalidate logs and summary since reset clears those too
      queryClient.invalidateQueries({ queryKey: LOGS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: SUMMARY_QUERY_KEY })
    },
  })

  return {
    messages: messagesQuery.data?.data ?? [],
    count: messagesQuery.data?.count ?? 0,
    isLoading: messagesQuery.isLoading,
    isError: messagesQuery.isError,
    error: messagesQuery.error,
    sendMessage: sendMutation.mutate,
    sendMessageAsync: sendMutation.mutateAsync,
    isSending: sendMutation.isPending,
    clearMessages: clearMutation.mutate,
    clearMessagesAsync: clearMutation.mutateAsync,
    isClearing: clearMutation.isPending,
  }
}
