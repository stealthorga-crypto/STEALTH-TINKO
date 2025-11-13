"use client";

import Link from "next/link";
import { useState } from "react";
import { PublicOnlyRoute } from "@/components/auth/ProtectedRoute";

type SignupMethod = 'google' | 'phone' | 'email' | null;
type FormStep = 'method' | 'personal' | 'business' | 'payment' | 'otp' | 'complete';

interface PersonalInfo {
  firstName: string;
  lastName: string;
  email?: string;
  password?: string;
  phoneNumber: string;
  countryCode: string;
}

interface BusinessInfo {
  companyName: string;
  businessType: string;
  website?: string;
  industry: string;
}

interface PaymentProviders {
  razorpay?: {
    keyId: string;
    keySecret: string;
  };
  stripe?: {
    publishableKey: string;
    secretKey: string;
  };
  ccavenue?: {
    merchantId: string;
    accessCode: string;
    workingKey: string;
  };
  paytm?: {
    merchantId: string;
    merchantKey: string;
  };
}

export default function SignupPage() {
  const [currentStep, setCurrentStep] = useState<FormStep>('method');
  const [selectedMethod, setSelectedMethod] = useState<SignupMethod>(null);
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    phoneNumber: '',
    countryCode: '+1'
  });
  const [businessInfo, setBusinessInfo] = useState<BusinessInfo>({
    companyName: '',
    businessType: '',
    website: '',
    industry: ''
  });
  const [paymentProviders, setPaymentProviders] = useState<PaymentProviders>({});
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [otpSent, setOtpSent] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://stealth-tinko-prod-app-1762804410.azurewebsites.net";
  const DEV_MODE = process.env.NODE_ENV === 'development';

  const handleGoogleSignUp = () => {
    const base = process.env.NEXT_PUBLIC_API_URL || "https://stealth-tinko-prod-app-1762804410.azurewebsites.net";
    const url = `${base}/v1/auth/oauth/google/start`;
    window.location.href = url;
  };

  const handleMethodSelection = (method: 'phone' | 'email') => {
    setSelectedMethod(method);
    setCurrentStep('personal');
    setError(null);
  };

  const handlePersonalInfoSubmit = () => {
    // Validation
    if (!personalInfo.firstName || !personalInfo.lastName || !personalInfo.phoneNumber) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (selectedMethod === 'email' && (!personalInfo.email || !personalInfo.password)) {
      setError('Please provide email and password');
      return;
    }

    setError(null);
    setCurrentStep('business');
  };

  const handleBusinessInfoSubmit = () => {
    if (!businessInfo.companyName || !businessInfo.businessType || !businessInfo.industry) {
      setError('Please fill in all business information fields');
      return;
    }
    
    setError(null);
    setCurrentStep('payment');
  };

  const handlePaymentSubmit = async () => {
    // Check if at least one payment provider is configured
    const hasProvider = Object.values(paymentProviders).some(provider => {
      if (!provider) return false;
      return Object.values(provider).every(value => 
        typeof value === 'string' && value.trim().length > 0
      );
    });

    if (!hasProvider) {
      setError('Please configure at least one payment provider');
      return;
    }

    setError(null);
    if (selectedMethod === 'phone') {
      // Send OTP for phone verification
      await sendOTP();
    } else {
      // For email signup, complete registration
      setCurrentStep('complete');
    }
  };

  const sendOTP = async () => {
    setOtpLoading(true);
    setError(null);
    
    try {
      // In development mode, simulate OTP sending without actual backend call
      if (DEV_MODE) {
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
        setOtpSent(true);
        setCurrentStep('otp');
        setError('🧪 DEV MODE: Use "123456" as OTP for testing');
        return;
      }

      const response = await fetch(`${API_BASE}/mobile/send-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: `${personalInfo.countryCode}${personalInfo.phoneNumber}`
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setOtpSent(true);
        setCurrentStep('otp');
      } else {
        // Handle specific Twilio configuration errors
        if (data.message?.includes('Twilio') || data.message?.includes('SMS') || data.message?.includes('credentials')) {
          setError('SMS service not configured. Please contact support or try email signup.');
        } else {
          setError(data.message || 'Failed to send OTP. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error sending OTP:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setOtpLoading(false);
    }
  };

  const verifyOTP = async () => {
    if (!otpCode || otpCode.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // In development mode, accept "123456" as valid OTP
      if (DEV_MODE) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
        
        if (otpCode === '123456') {
          await createUserAccount();
          return;
        } else {
          setError('🧪 DEV MODE: Use "123456" as OTP for testing');
          return;
        }
      }

      const response = await fetch(`${API_BASE}/mobile/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: `${personalInfo.countryCode}${personalInfo.phoneNumber}`,
          otp: otpCode
        }),
      });

      const data = await response.json();

      if (response.ok) {
        await createUserAccount();
      } else {
        // Handle specific Twilio configuration errors
        if (data.message?.includes('Twilio') || data.message?.includes('SMS') || data.message?.includes('credentials')) {
          setError('SMS service not configured. Please contact support or try email signup.');
        } else {
          setError(data.message || 'Invalid OTP. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error verifying OTP:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const createUserAccount = async () => {
    try {
      // This would be your user registration endpoint
      const userData = {
        personalInfo,
        businessInfo,
        paymentProviders,
        signupMethod: selectedMethod,
        phoneVerified: true
      };

      // For now, just show success - you'll need to implement the actual registration endpoint
      setCurrentStep('complete');
    } catch (error) {
      console.error('Error creating user account:', error);
      setError('Failed to create account. Please try again.');
    }
  };

  const resendOTP = async () => {
    await sendOTP();
  };

  const handleOTPSubmit = async () => {
    await verifyOTP();
  };

  const goBack = () => {
    if (currentStep === 'personal') setCurrentStep('method');
    else if (currentStep === 'business') setCurrentStep('personal');
    else if (currentStep === 'payment') setCurrentStep('business');
    else if (currentStep === 'otp') setCurrentStep('payment');
  };

  return (
    <PublicOnlyRoute>
      <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
        <div className="w-full max-w-lg">
          <div className="text-center mb-8">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              Tinko
            </Link>
            <h1 className="text-3xl font-bold text-slate-900 mt-4">Create your account</h1>
            <p className="text-slate-600 mt-2">Start recovering failed payments today</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Method Selection */}
            {currentStep === 'method' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">How would you like to sign up?</h2>
                  <p className="text-slate-600">Choose your preferred registration method</p>
                </div>

                <div className="space-y-4">
                  <button
                    type="button"
                    onClick={handleGoogleSignUp}
                    className="w-full px-6 py-4 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-3 transition-colors"
                  >
                    <span className="font-medium">Continue with Google</span>
                  </button>

                  <div className="flex items-center my-4">
                    <div className="flex-1 h-px bg-slate-200" />
                    <span className="px-4 text-slate-500 text-sm">or</span>
                    <div className="flex-1 h-px bg-slate-200" />
                  </div>

                  <button
                    type="button"
                    onClick={() => handleMethodSelection('phone')}
                    className="w-full px-6 py-4 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-3 transition-colors"
                  >
                    <span className="font-medium">Sign up with Phone (No Password)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleMethodSelection('email')}
                    className="w-full px-6 py-4 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-3 transition-colors"
                  >
                    <span className="font-medium">Sign up with Email & Password</span>
                  </button>
                </div>
              </div>
            )}

            {/* Personal Information Step */}
            {currentStep === 'personal' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">Personal Information</h2>
                  <p className="text-slate-600">Tell us about yourself</p>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">First Name *</label>
                      <input
                        type="text"
                        value={personalInfo.firstName}
                        onChange={(e) => setPersonalInfo({...personalInfo, firstName: e.target.value})}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Last Name *</label>
                      <input
                        type="text"
                        value={personalInfo.lastName}
                        onChange={(e) => setPersonalInfo({...personalInfo, lastName: e.target.value})}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Doe"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number *</label>
                    <div className="flex gap-2">
                      <select
                        value={personalInfo.countryCode}
                        onChange={(e) => setPersonalInfo({...personalInfo, countryCode: e.target.value})}
                        className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="+1">+1 (US)</option>
                        <option value="+91">+91 (IN)</option>
                        <option value="+44">+44 (UK)</option>
                        <option value="+61">+61 (AU)</option>
                      </select>
                      <input
                        type="tel"
                        value={personalInfo.phoneNumber}
                        onChange={(e) => setPersonalInfo({...personalInfo, phoneNumber: e.target.value})}
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="1234567890"
                      />
                    </div>
                  </div>

                  {selectedMethod === 'email' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email Address *</label>
                        <input
                          type="email"
                          value={personalInfo.email}
                          onChange={(e) => setPersonalInfo({...personalInfo, email: e.target.value})}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="john@example.com"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Password *</label>
                        <input
                          type="password"
                          value={personalInfo.password}
                          onChange={(e) => setPersonalInfo({...personalInfo, password: e.target.value})}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="••••••••"
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={goBack}
                    className="flex-1 px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handlePersonalInfoSubmit}
                    disabled={isLoading}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Continue
                  </button>
                </div>
              </div>
            )}

            {/* Business Information Step */}
            {currentStep === 'business' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">Business Information</h2>
                  <p className="text-slate-600">Tell us about your business</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Company Name *</label>
                    <input
                      type="text"
                      value={businessInfo.companyName}
                      onChange={(e) => setBusinessInfo({...businessInfo, companyName: e.target.value})}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Acme Inc."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Business Type *</label>
                    <select
                      value={businessInfo.businessType}
                      onChange={(e) => setBusinessInfo({...businessInfo, businessType: e.target.value})}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Business Type</option>
                      <option value="ecommerce">E-commerce</option>
                      <option value="saas">SaaS</option>
                      <option value="marketplace">Marketplace</option>
                      <option value="subscription">Subscription</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Industry *</label>
                    <select
                      value={businessInfo.industry}
                      onChange={(e) => setBusinessInfo({...businessInfo, industry: e.target.value})}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Industry</option>
                      <option value="technology">Technology</option>
                      <option value="retail">Retail</option>
                      <option value="finance">Finance</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="education">Education</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Website (Optional)</label>
                    <input
                      type="url"
                      value={businessInfo.website}
                      onChange={(e) => setBusinessInfo({...businessInfo, website: e.target.value})}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com"
                    />
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={goBack}
                    className="flex-1 px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleBusinessInfoSubmit}
                    disabled={isLoading}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Continue
                  </button>
                </div>
              </div>
            )}

            {/* Payment Providers Step */}
            {currentStep === 'payment' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">Payment Provider Setup</h2>
                  <p className="text-slate-600">Configure your payment providers (at least one required)</p>
                  {DEV_MODE && (
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800 text-sm">
                        🧪 <strong>Development Mode:</strong> SMS service may not be configured. You can still test the flow!
                      </p>
                    </div>
                  )}
                </div>

                <div className="space-y-6">
                  {/* Razorpay */}
                  <div className="border border-slate-200 rounded-lg p-4">
                    <h3 className="font-semibold text-slate-900 mb-3">Razorpay</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Key ID</label>
                        <input
                          type="text"
                          value={paymentProviders.razorpay?.keyId || ''}
                          onChange={(e) => setPaymentProviders({
                            ...paymentProviders,
                            razorpay: { ...paymentProviders.razorpay, keyId: e.target.value, keySecret: paymentProviders.razorpay?.keySecret || '' }
                          })}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="rzp_test_..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Key Secret</label>
                        <input
                          type="password"
                          value={paymentProviders.razorpay?.keySecret || ''}
                          onChange={(e) => setPaymentProviders({
                            ...paymentProviders,
                            razorpay: { keyId: paymentProviders.razorpay?.keyId || '', keySecret: e.target.value }
                          })}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Stripe */}
                  <div className="border border-slate-200 rounded-lg p-4">
                    <h3 className="font-semibold text-slate-900 mb-3">Stripe</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Publishable Key</label>
                        <input
                          type="text"
                          value={paymentProviders.stripe?.publishableKey || ''}
                          onChange={(e) => setPaymentProviders({
                            ...paymentProviders,
                            stripe: { ...paymentProviders.stripe, publishableKey: e.target.value, secretKey: paymentProviders.stripe?.secretKey || '' }
                          })}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="pk_test_..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Secret Key</label>
                        <input
                          type="password"
                          value={paymentProviders.stripe?.secretKey || ''}
                          onChange={(e) => setPaymentProviders({
                            ...paymentProviders,
                            stripe: { publishableKey: paymentProviders.stripe?.publishableKey || '', secretKey: e.target.value }
                          })}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="sk_test_..."
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={goBack}
                    className="flex-1 px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handlePaymentSubmit}
                    disabled={isLoading || otpLoading}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {otpLoading ? 'Sending OTP...' : 'Continue'}
                  </button>
                </div>
              </div>
            )}

            {/* OTP Verification Step */}
            {currentStep === 'otp' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">Phone Verification</h2>
                  <p className="text-slate-600">
                    We've sent a 6-digit code to {personalInfo.countryCode} {personalInfo.phoneNumber}
                  </p>
                  {DEV_MODE && (
                    <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-yellow-800 text-sm">
                        🧪 <strong>Development Mode:</strong> Use "123456" as the OTP code for testing
                      </p>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Enter OTP *</label>
                    <input
                      type="text"
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-2xl tracking-widest"
                      placeholder="000000"
                      maxLength={6}
                    />
                  </div>

                  <div className="text-center">
                    <button 
                      onClick={resendOTP}
                      disabled={otpLoading}
                      className="text-blue-600 hover:text-blue-700 text-sm disabled:opacity-50"
                    >
                      {otpLoading ? 'Sending...' : 'Didn\'t receive the code? Resend'}
                    </button>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={goBack}
                    className="flex-1 px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleOTPSubmit}
                    disabled={isLoading || otpCode.length !== 6}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoading ? 'Verifying...' : 'Verify & Complete'}
                  </button>
                </div>
              </div>
            )}

            {/* Complete Step */}
            {currentStep === 'complete' && (
              <div className="space-y-6 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">Account Created Successfully!</h2>
                  <p className="text-slate-600">
                    Welcome to Tinko! Your account has been created and you can now start recovering failed payments.
                  </p>
                </div>
                <Link
                  href="/dashboard"
                  className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Go to Dashboard
                </Link>
              </div>
            )}

            <p className="mt-6 text-center text-sm text-slate-600">
              Already have an account?{" "}
              <Link href="/auth/signin" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </PublicOnlyRoute>
  );
}
