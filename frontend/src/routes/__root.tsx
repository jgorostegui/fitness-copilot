import { Outlet, createRootRoute } from "@tanstack/react-router"
import { Box, Text } from "@chakra-ui/react"

const NotFound = () => (
  <Box h="100vh" display="flex" alignItems="center" justifyContent="center">
    <Text>Page not found</Text>
  </Box>
)

export const Route = createRootRoute({
  component: () => <Outlet />,
  notFoundComponent: NotFound,
})
