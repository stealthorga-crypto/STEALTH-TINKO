export type ApiMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestOptions = Omit<RequestInit, "method"> & {
  parseJson?: boolean;
  timeout?: number;
  retry?: boolean;
  retryCount?: number;
  retryDelay?: number;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
    public readonly code?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";

const buildUrl = (path: string) => {
  if (/^https?:\/\//.test(path)) {
    return path;
  }

  if (!baseUrl) {
    console.warn("NEXT_PUBLIC_API_URL is not set; falling back to relative path request.");
    return path;
  }

  try {
    return new URL(path, baseUrl).toString();
  } catch (err) {
    console.error("Failed to construct API URL", err);
    return path;
  }
};

const request = async <T>(path: string, method: ApiMethod, options: RequestOptions = {}) => {
  const {
    parseJson = true,
    headers,
    timeout = 30000,
    retry = true,
    retryCount = 2,
    retryDelay = 1000,
    ...init
  } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  let attempts = 0;

  while (attempts <= (retry ? retryCount : 0)) {
    try {
      // Try to add Authorization header from stored token (localStorage or cookie)
      let authHeader: Record<string, string> = {};
      try {
        if (typeof window !== "undefined") {
          const ls = window.localStorage?.getItem("auth_token");
          const cookie = typeof document !== "undefined" ? document.cookie : "";
          const m = cookie.match(/(?:^|; )authjs\.session-token=([^;]+)/);
          const token = ls || (m ? decodeURIComponent(m[1]) : undefined);
          if (token) {
            authHeader = { Authorization: `Bearer ${token}` };
          }
        }
      } catch {}

      const response = await fetch(buildUrl(path), {
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
          ...authHeader,
        },
        signal: controller.signal,
        credentials: "include", // Send cookies for session
        ...init,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let body: unknown;

        if (parseJson) {
          try {
            body = await response.json();
          } catch {
            body = await response.text();
          }
        }

        // Don't retry client errors (4xx) except rate limits (429)
        if (response.status >= 400 && response.status < 500 && response.status !== 429) {
          throw new ApiError(
            response.statusText || "Request failed",
            response.status,
            body,
            "CLIENT_ERROR"
          );
        }

        // Retry server errors (5xx) and rate limits
        if (retry && attempts < retryCount) {
          attempts++;
          await sleep(retryDelay * attempts);
          continue;
        }

        throw new ApiError(
          response.statusText || "Request failed",
          response.status,
          body,
          "SERVER_ERROR"
        );
      }

      if (!parseJson || response.status === 204) {
        return undefined as T;
      }

      return (await response.json()) as T;
    } catch (error) {
      clearTimeout(timeoutId);

      // Abort error (timeout)
      if (error instanceof Error && error.name === "AbortError") {
        throw new ApiError("Request timeout", 408, { timeout }, "TIMEOUT");
      }

      // Network error
      if (error instanceof TypeError) {
        if (retry && attempts < retryCount) {
          attempts++;
          await sleep(retryDelay * attempts);
          continue;
        }

        throw new ApiError("Network error - check your connection", 0, null, "NETWORK_ERROR");
      }

      // Re-throw ApiError
      if (error instanceof ApiError) {
        throw error;
      }

      // Unknown error
      throw new ApiError(
        error instanceof Error ? error.message : "Unknown error",
        500,
        null,
        "UNKNOWN_ERROR"
      );
    }
  }

  throw new ApiError("Service unavailable after retries", 503, { attempts }, "RETRY_EXHAUSTED");
};

export const api = {
  get: <T>(path: string, options?: RequestOptions) => request<T>(path, "GET", options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, "POST", {
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, "PUT", {
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, "PATCH", {
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    }),
  delete: <T>(path: string, options?: RequestOptions) => request<T>(path, "DELETE", options),
};

/**
 * Health check endpoint
 */
export const healthCheck = () => api.get<{ status: string; version: string }>("/healthz");

/**
 * React Query integration helpers
 */
export const queryKeys = {
  organizations: ["organizations"] as const,
  organization: (id: string) => ["organizations", id] as const,
  recoveries: (orgId: string, params?: Record<string, string | number | boolean>) =>
    ["recoveries", orgId, params] as const,
  recovery: (orgId: string, recoveryId: string) =>
    ["recoveries", orgId, recoveryId] as const,
  rules: (orgId: string) => ["rules", orgId] as const,
  events: (orgId: string, params?: Record<string, string | number | boolean>) => ["events", orgId, params] as const,
  logs: (orgId: string, params?: Record<string, string | number | boolean>) => ["logs", orgId, params] as const,
};
