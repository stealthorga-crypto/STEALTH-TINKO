"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { AuthModal } from '@/components/auth/AuthModal';
import { useAuth } from '@/hooks/useAuth';
import { User, LogOut, Settings } from 'lucide-react';

export function AuthHeader() {
  const { user, isAuthenticated, loading, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  const handleShowLogin = () => {
    setAuthMode('login');
    setShowAuthModal(true);
  };

  const handleShowSignup = () => {
    setAuthMode('signup');
    setShowAuthModal(true);
  };

  const handleLogout = async () => {
    await logout();
  };

  const getUserInitials = () => {
    if (user?.full_name) {
      return user.full_name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    if (user?.email) {
      return user.email[0].toUpperCase();
    }
    if (user?.mobile_number) {
      return 'U';
    }
    return 'G';
  };

  const getUserDisplayName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.email) return user.email;
    if (user?.mobile_number) return user.mobile_number;
    return 'User';
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <div className="flex items-center space-x-2">
          <Button variant="ghost" onClick={handleShowLogin}>
            Sign In
          </Button>
          <Button onClick={handleShowSignup}>
            Sign Up
          </Button>
        </div>
        
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          mode={authMode}
        />
      </>
    );
  }

  return (
    <div className="flex items-center space-x-4">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-8 w-8">
              <AvatarImage src={user?.avatar_url} alt={getUserDisplayName()} />
              <AvatarFallback>{getUserInitials()}</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end" forceMount>
          <div className="flex items-center justify-start gap-2 p-2">
            <div className="flex flex-col space-y-1 leading-none">
              <p className="font-medium">{getUserDisplayName()}</p>
              {user?.email && user?.mobile_number && (
                <p className="text-xs text-muted-foreground">
                  {user.email}
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                via {user?.auth_provider === 'google' ? 'Google' : 
                     user?.auth_provider === 'mobile_otp' ? 'Mobile' : 'Email'}
              </p>
            </div>
          </div>
          <hr className="my-1" />
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}