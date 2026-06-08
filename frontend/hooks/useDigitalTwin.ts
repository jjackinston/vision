import { useMutation } from "@tanstack/react-query";
import { api, SimulationParams } from "@/lib/api";

export function useDigitalTwin() {
  const mutation = useMutation({
    mutationFn: (params: SimulationParams) => api.runDigitalTwinSimulation(params),
  });

  return {
    simulate: mutation.mutate,
    simulateAsync: mutation.mutateAsync,
    result: mutation.data,
    isSimulating: mutation.isPending,
    error: mutation.error,
    reset: mutation.reset,
  };
}
