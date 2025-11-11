"use client";

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/hooks/useAuth';
import { Phone, Mail, Globe, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode?: 'login' | 'signup';
  title?: string;
}

export function AuthModal({ isOpen, onClose, mode = 'login', title }: AuthModalProps) {
  const [currentTab, setCurrentTab] = useState<'mobile' | 'email' | 'google'>('mobile');
  const [step, setStep] = useState<'input' | 'otp-verify'>('input');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    mobileNumber: '',
    password: '',
    otp: '',
    countryCode: '+1'
  });

  const { 
    signup, 
    sendOTP, 
    verifyOTP, 
    googleLogin, 
    loginWithEmail 
  } = useAuth();

  const resetForm = () => {
    setFormData({
      fullName: '',
      email: '',
      mobileNumber: '',
      password: '',
      otp: '',
      countryCode: '+1'
    });
    setError('');
    setSuccess('');
    setStep('input');
    setLoading(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleTabChange = (tab: 'mobile' | 'email' | 'google') => {
    setCurrentTab(tab);
    setError('');
    setSuccess('');
    setStep('input');
  };

  // Mobile OTP Flow
  const handleMobileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (step === 'input') {
        const fullMobile = `${formData.countryCode}${formData.mobileNumber}`;
        const result = await sendOTP(fullMobile);
        
        if (result.success) {
          setStep('otp-verify');
          setSuccess('OTP sent successfully! Check your phone.');
        } else {
          setError(result.message || 'Failed to send OTP');
        }
      } else {
        const fullMobile = `${formData.countryCode}${formData.mobileNumber}`;
        const result = await verifyOTP(fullMobile, formData.otp);
        
        if (result.success) {
          setSuccess('Login successful!');
          setTimeout(() => {
            handleClose();
          }, 1500);
        } else {
          setError(result.message || 'Invalid OTP');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Email Signup Flow
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'signup') {
        const result = await signup({
          full_name: formData.fullName,
          email: formData.email,
          password: formData.password,
          mobile_number: formData.mobileNumber ? `${formData.countryCode}${formData.mobileNumber}` : undefined
        });
        
        if (result.success) {
          setSuccess('Account created successfully! Please verify your email.');
        } else {
          setError(result.message || 'Signup failed');
        }
      } else {
        const result = await loginWithEmail(formData.email, formData.password);
        
        if (result.success) {
          setSuccess('Login successful!');
          setTimeout(() => {
            handleClose();
          }, 1500);
        } else {
          setError(result.message || 'Login failed');
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Google OAuth Flow
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError('');
    setLoading(true);

    try {
      const result = await googleLogin(credentialResponse.credential);
      
      if (result.success) {
        setSuccess('Google login successful!');
        setTimeout(() => {
          handleClose();
        }, 1500);
      } else {
        setError(result.message || 'Google login failed');
      }
    } catch (err: any) {
      setError(err.message || 'Google login failed');
    } finally {
      setLoading(false);
    }
  };

  const modalTitle = title || (mode === 'signup' ? 'Create Your Account' : 'Welcome Back');

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl font-bold">
            {modalTitle}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Tab Navigation */}
          <Tabs value={currentTab} onValueChange={handleTabChange}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="mobile" className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                Mobile
              </TabsTrigger>
              {mode === 'signup' && (
                <TabsTrigger value="email" className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </TabsTrigger>
              )}
              <TabsTrigger value="google" className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Google
              </TabsTrigger>
            </TabsList>

            {/* Error/Success Messages */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            {/* Mobile OTP Tab */}
            <TabsContent value="mobile">
              <form onSubmit={handleMobileSubmit} className="space-y-4">
                {step === 'input' ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="mobile">Mobile Number</Label>
                      <div className="flex gap-2">
                        <select 
                          value={formData.countryCode}
                          onChange={(e) => setFormData({...formData, countryCode: e.target.value})}
                          className="w-20 px-3 py-2 border rounded-md"
                        >
                          <option value="+1">+1</option>
                          <option value="+91">+91</option>
                          <option value="+44">+44</option>
                          <option value="+86">+86</option>
                        </select>
                        <Input
                          id="mobile"
                          type="tel"
                          required
                          value={formData.mobileNumber}
                          onChange={(e) => setFormData({...formData, mobileNumber: e.target.value})}
                          placeholder="9876543210"
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <Button type="submit" className="w-full" disabled={loading}>
                      {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                      Send OTP
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="text-center space-y-2">
                      <div className="text-sm text-muted-foreground">
                        Enter the 6-digit code sent to
                      </div>
                      <div className="font-medium">
                        {formData.countryCode}{formData.mobileNumber}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="otp">Verification Code</Label>
                      <Input
                        id="otp"
                        type="text"
                        required
                        maxLength={6}
                        value={formData.otp}
                        onChange={(e) => setFormData({...formData, otp: e.target.value.replace(/\D/g, '')})}
                        placeholder="000000"
                        className="text-center text-2xl tracking-widest"
                      />
                    </div>
                    <Button type="submit" className="w-full" disabled={loading || formData.otp.length !== 6}>
                      {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                      Verify & Continue
                    </Button>
                    <Button 
                      type="button" 
                      variant="ghost" 
                      className="w-full" 
                      onClick={() => setStep('input')}
                    >
                      Change Number
                    </Button>
                  </>
                )}
              </form>
            </TabsContent>

            {/* Email Tab (Signup only) */}
            {mode === 'signup' && (
              <TabsContent value="email">
                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      type="text"
                      required
                      value={formData.fullName}
                      onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                      placeholder="John Doe"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      placeholder="john@example.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="mobile-optional">Mobile Number (Optional)</Label>
                    <div className="flex gap-2">
                      <select 
                        value={formData.countryCode}
                        onChange={(e) => setFormData({...formData, countryCode: e.target.value})}
                        className="w-20 px-3 py-2 border rounded-md"
                      >
                        <option value="+1">+1</option>
                        <option value="+91">+91</option>
                        <option value="+44">+44</option>
                        <option value="+86">+86</option>
                      </select>
                      <Input
                        id="mobile-optional"
                        type="tel"
                        value={formData.mobileNumber}
                        onChange={(e) => setFormData({...formData, mobileNumber: e.target.value})}
                        placeholder="9876543210"
                        className="flex-1"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      required
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      placeholder="Create a secure password"
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                    Create Account
                  </Button>
                </form>
              </TabsContent>
            )}

            {/* Google Tab */}
            <TabsContent value="google">
              <div className="flex flex-col items-center space-y-4">
                <div className="text-sm text-muted-foreground text-center">
                  Sign {mode === 'signup' ? 'up' : 'in'} with your Google account
                </div>
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => setError('Google authentication failed')}
                  useOneTap={false}
                  theme="outline"
                  size="large"
                  width="100%"
                />
              </div>
            </TabsContent>
          </Tabs>

          {/* Footer */}
          <div className="text-center text-sm text-muted-foreground">
            {mode === 'signup' ? (
              <>
                Already have an account?{' '}
                <button 
                  className="text-primary hover:underline font-medium"
                  onClick={() => handleClose()}
                >
                  Sign In
                </button>
              </>
            ) : (
              <>
                Don't have an account?{' '}
                <button 
                  className="text-primary hover:underline font-medium"
                  onClick={() => handleClose()}
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}