import React, { useState } from 'react';
import { Shield, Eye, EyeOff } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const demoAccounts = [
    {
      title: 'Inspector (Police)',
      email: 'inspector.kumar@tourism.gov.in',
      password: 'password123',
      description: 'Full access to all features'
    },
    {
      title: 'Admin (Tourism Dept)',
      email: 'admin.singh@tourism.gov.in', 
      password: 'admin123',
      description: 'Administrative access'
    },
    {
      title: 'Officer (Police)',
      email: 'officer.sharma@tourism.gov.in',
      password: 'officer123',
      description: 'Limited field officer access'
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" 
         style={{backgroundColor: '#111827'}}>
      <div className="w-full max-w-md">
        <div className="rounded-lg shadow-2xl p-8 border"
             style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full" style={{backgroundColor: '#3B82F6'}}>
                <Shield className="w-8 h-8" style={{color: '#FFFFFF'}} />
              </div>
            </div>
            <h1 className="text-2xl font-bold" style={{color: '#F3F4F6'}}>
              Tourism Safety
            </h1>
            <p className="text-sm mt-1" style={{color: '#9CA3AF'}}>
              Command Center Login
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 rounded-lg border" 
                   style={{backgroundColor: '#FEE2E2', borderColor: '#EF4444', color: '#DC2626'}}>
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#F3F4F6'}}>
                Email Address
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="officer@tourism.gov.in"
                className="w-full border"
                style={{
                  backgroundColor: '#374151',
                  borderColor: '#4B5563',
                  color: '#F3F4F6'
                }}
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#F3F4F6'}}>
                Password
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pr-10 border"
                  style={{
                    backgroundColor: '#374151',
                    borderColor: '#4B5563',
                    color: '#F3F4F6'
                  }}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                  style={{color: '#9CA3AF'}}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full py-3 font-semibold transition-colors"
              style={{
                backgroundColor: '#3B82F6',
                color: '#FFFFFF'
              }}
              onMouseEnter={(e) => {
                if (!loading) e.target.style.backgroundColor = '#2563EB';
              }}
              onMouseLeave={(e) => {
                if (!loading) e.target.style.backgroundColor = '#3B82F6';
              }}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Signing In...
                </div>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Demo Accounts */}
          <div className="mt-8">
            <div className="text-center mb-4">
              <p className="text-sm font-medium" style={{color: '#9CA3AF'}}>Demo Accounts</p>
            </div>
            <div className="space-y-2">
              {demoAccounts.map((account, index) => (
                <button
                  key={index}
                  onClick={() => handleDemoLogin(account.email, account.password)}
                  disabled={loading}
                  className="w-full p-3 text-left rounded-lg border transition-colors"
                  style={{
                    backgroundColor: '#374151',
                    borderColor: '#4B5563',
                    color: '#F3F4F6'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.target.style.backgroundColor = '#4B5563';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) {
                      e.target.style.backgroundColor = '#374151';
                    }
                  }}
                >
                  <div className="font-medium">{account.title}</div>
                  <div className="text-xs mt-1" style={{color: '#9CA3AF'}}>
                    {account.description}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-xs" style={{color: '#9CA3AF'}}>
              Secure access to tourism safety monitoring system
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;