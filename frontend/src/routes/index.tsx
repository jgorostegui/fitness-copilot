import { createFileRoute } from "@tanstack/react-router"
import { FitnessApp } from "@/components/Fitness"

export const Route = createFileRoute("/")({
  component: FitnessApp,
})
