import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
  };

  const fillDemoCredentials = (type) => {
    const credentials = {
      inspector: {
        email: 'inspector.kumar@tourism.gov.in',
        password: 'password123'
      },
      admin: {
        email: 'admin.singh@tourism.gov.in', 
        password: 'admin123'
      },
      officer: {
        email: 'officer.sharma@tourism.gov.in',
        password: 'officer123'
      }
    };

    setFormData(credentials[type]);
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="w-full max-w-md p-6">
        <Card className="bg-slate-800 border-slate-700 shadow-2xl">
          <CardHeader className="space-y-1 text-center">
            <div className="flex items-center justify-center mb-4">
              <Shield className="w-12 h-12 text-blue-400" />
            </div>
            <CardTitle className="text-2xl font-bold text-white">
              Tourism Safety
            </CardTitle>
            <p className="text-slate-400">
              Command Center Login
            </p>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive" className="bg-red-900/20 border-red-700">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-red-300">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-300">
                  Email Address
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="officer@tourism.gov.in"
                  className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-slate-300">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    className="bg-slate-700 border-slate-600 text-white placeholder-slate-400 pr-10"
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-slate-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-slate-400" />
                    )}
                  </Button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                disabled={isLoading}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6">
              <div className="text-center text-sm text-slate-400 mb-3">
                Demo Accounts
              </div>
              <div className="grid grid-cols-1 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fillDemoCredentials('inspector')}
                  className="text-xs border-slate-600 text-slate-300 hover:bg-slate-700"
                  disabled={isLoading}
                >
                  Inspector (Police)
                </Button>
                <Button
                  variant="outline"
                  size="sm" 
                  onClick={() => fillDemoCredentials('admin')}
                  className="text-xs border-slate-600 text-slate-300 hover:bg-slate-700"
                  disabled={isLoading}
                >
                  Admin (Tourism Dept)
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fillDemoCredentials('officer')}
                  className="text-xs border-slate-600 text-slate-300 hover:bg-slate-700"
                  disabled={isLoading}
                >
                  Officer (Police)
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;