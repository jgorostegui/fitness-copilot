import { defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  client: "legacy/axios",
  input: "./openapi.json",
  output: "./src/client",
  plugins: [
    {
      name: "@hey-api/sdk",
      asClass: true,
      operationId: true,
      methodNameBuilder: (operation) => {
        // Get operation ID and convert to method name
        const operationId = operation.id || ""
        // operationId format: "login-login_access_token" -> "loginAccessToken"
        // Split by hyphen, take last part, convert snake_case to camelCase
        const parts = operationId.split("-")
        const methodPart =
          parts.length > 1 ? parts.slice(1).join("-") : parts[0]

        // Convert snake_case to camelCase
        const camelCase = methodPart.replace(/_([a-z])/g, (_, letter) =>
          letter.toUpperCase(),
        )

        return camelCase.charAt(0).toLowerCase() + camelCase.slice(1)
      },
    },
  ],
})
