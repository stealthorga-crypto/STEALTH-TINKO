/**
 * Analytics API response types
 */

export interface RecoveryRateResponse {
  recovery_rate: number;
  total_failures: number;
  recovered: number;
  period_days: number;
}

export interface FailureCategoryResponse {
  categories: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
}

export interface RevenueRecoveredResponse {
  total_recovered: number;
  currency: string;
  period_days: number;
  by_month?: Array<{
    month: string;
    amount: number;
  }>;
}

export interface AttemptsByChannelResponse {
  channels: Array<{
    channel: string;
    count: number;
    success_rate: number;
  }>;
}

export interface DashboardStats {
  totalRecovered: string;
  recoveryRate: number;
  activeRules: number;
  alerts: number;
  merchants: number;
  periodComparison?: string;
}
