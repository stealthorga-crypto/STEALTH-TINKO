/**
 * Rate Limiting Utility
 * In-memory only implementation (Redis removed for simplicity)
 */

// In-memory fallback store
const memoryStore = new Map<string, { count: number; resetAt: number }>();

interface RateLimitOptions {
  identifier: string;
  limit: number;
  windowMs: number;
}

interface RateLimitResult {
  success: boolean;
  remaining: number;
  resetAt: number;
}

/**
 * Check rate limit for an identifier
 */
export async function checkRateLimit(options: RateLimitOptions): Promise<RateLimitResult> {
  const { identifier, limit, windowMs } = options;
  const now = Date.now();
  const resetAt = now + windowMs;

  return checkMemoryRateLimit(identifier, limit, windowMs, now, resetAt);
}

/**
 * In-memory rate limiting
 */
function checkMemoryRateLimit(
  identifier: string,
  limit: number,
  windowMs: number,
  now: number,
  resetAt: number
): RateLimitResult {
  const existing = memoryStore.get(identifier);

  // Clean up expired entries
  if (existing && now > existing.resetAt) {
    memoryStore.delete(identifier);
  }

  const current = existing && now <= existing.resetAt ? existing.count + 1 : 1;

  memoryStore.set(identifier, {
    count: current,
    resetAt: existing && now <= existing.resetAt ? existing.resetAt : resetAt,
  });

  const remaining = Math.max(0, limit - current);
  const success = current <= limit;

  return { success, remaining, resetAt };
}

/**
 * Create rate limit check for OTP sending
 */
export async function checkOTPSendRateLimit(ipAddress: string, identifier: string): Promise<RateLimitResult> {
  const limit = parseInt(process.env.RATE_LIMIT_OTP_SEND || '5', 10);
  const windowMs = 60 * 1000; // 1 minute

  // Check both IP and identifier (email/phone)
  const ipResult = await checkRateLimit({
    identifier: `otp:send:ip:${ipAddress}`,
    limit,
    windowMs,
  });

  if (!ipResult.success) {
    return ipResult;
  }

  return checkRateLimit({
    identifier: `otp:send:id:${identifier}`,
    limit,
    windowMs,
  });
}

/**
 * Create rate limit check for OTP verification
 */
export async function checkOTPVerifyRateLimit(ipAddress: string, identifier: string): Promise<RateLimitResult> {
  const limit = parseInt(process.env.RATE_LIMIT_OTP_VERIFY || '10', 10);
  const windowMs = 60 * 1000; // 1 minute

  // Check both IP and identifier
  const ipResult = await checkRateLimit({
    identifier: `otp:verify:ip:${ipAddress}`,
    limit,
    windowMs,
  });

  if (!ipResult.success) {
    return ipResult;
  }

  return checkRateLimit({
    identifier: `otp:verify:id:${identifier}`,
    limit,
    windowMs,
  });
}

/**
 * Clean up expired entries from memory store (call periodically)
 */
export function cleanupMemoryStore(): void {
  const now = Date.now();
  
  for (const [key, value] of memoryStore.entries()) {
    if (now > value.resetAt) {
      memoryStore.delete(key);
    }
  }
}

// Run cleanup every 5 minutes
setInterval(cleanupMemoryStore, 5 * 60 * 1000);
