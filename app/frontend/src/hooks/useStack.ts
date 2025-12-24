'use client';

import useSWR from 'swr';
import { apiClient } from '@/lib/api-client';
import type { StackSummary, StackInfo, Resource } from '@/types/stack';

export function useStacks() {
  const { data, error, isLoading, mutate } = useSWR<StackSummary[]>(
    '/stacks',
    () => apiClient.listStacks(),
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
    }
  );

  return {
    stacks: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export function useStack(stackName: string | null) {
  const { data, error, isLoading, mutate } = useSWR<StackInfo>(
    stackName ? `/stacks/${stackName}` : null,
    () => (stackName ? apiClient.getStack(stackName) : null),
    {
      refreshInterval: 10000, // Refresh every 10 seconds
      revalidateOnFocus: true,
    }
  );

  return {
    stack: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export function useStackResources(stackName: string | null) {
  const { data, error, isLoading, mutate } = useSWR<Resource[]>(
    stackName ? `/stacks/${stackName}/resources` : null,
    () => (stackName ? apiClient.getStackResources(stackName) : null),
    {
      refreshInterval: 15000, // Refresh every 15 seconds
    }
  );

  return {
    resources: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export function useStackOutputs(stackName: string | null) {
  const { data, error, isLoading, mutate } = useSWR<Record<string, any>>(
    stackName ? `/stacks/${stackName}/outputs` : null,
    () => (stackName ? apiClient.getStackOutputs(stackName) : null)
  );

  return {
    outputs: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}
