import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useCEODashboard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["ceo-dashboard"],
    queryFn: () => api.getCEORecommendations(),
    staleTime: 1000 * 60 * 30, // 30 minutes
    refetchInterval: 1000 * 60 * 60, // refetch every hour
  });

  return {
    recommendations: data?.recommendations,
    summary: data,
    isLoading,
    error,
    refetch,
  };
}
