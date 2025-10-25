import { api } from "@/lib/api";

export type RetryPolicy = {
  id: number;
  org_id: number;
  name: string;
  max_retries: number;
  initial_delay_minutes: number;
  backoff_multiplier: number;
  max_delay_minutes: number;
  enabled_channels: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type RetryPolicyInput = {
  name: string;
  max_retries: number; // 1-10
  initial_delay_minutes: number; // >= 0
  backoff_multiplier: number; // >= 1
  max_delay_minutes: number; // >= initial
  enabled_channels?: string[]; // defaults server-side to ["email"]
};

// NOTE: Backend routes are /v1/retry/policies (not /v1/retry_policies)

export async function listPolicies(): Promise<RetryPolicy[]> {
  return api.get<RetryPolicy[]>("/v1/retry/policies");
}

export async function getActivePolicy(): Promise<RetryPolicy | null> {
  return api.get<RetryPolicy | null>("/v1/retry/policies/active");
}

export async function createPolicy(input: RetryPolicyInput): Promise<RetryPolicy> {
  return api.post<RetryPolicy>("/v1/retry/policies", input);
}

export async function deletePolicy(id: number): Promise<void> {
  await api.delete<void>(`/v1/retry/policies/${id}`);
}
