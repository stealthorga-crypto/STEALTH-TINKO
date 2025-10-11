export type ApiMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestOptions = Omit<RequestInit, "method"> & {
  parseJson?: boolean;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

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
  const { parseJson = true, headers, ...init } = options;

  const response = await fetch(buildUrl(path), {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    ...init,
  });

  if (!response.ok) {
    let body: unknown;

    if (parseJson) {
      try {
        body = await response.json();
      } catch {
        body = await response.text();
      }
    }

    throw new ApiError(response.statusText || "Request failed", response.status, body);
  }

  if (!parseJson || response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
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
