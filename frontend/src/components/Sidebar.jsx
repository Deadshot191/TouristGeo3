import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Map, AlertTriangle, Users, Settings, LogOut, Shield, FileText } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Live Map', href: '/', icon: Map, current: location.pathname === '/' },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle, current: location.pathname === '/alerts' },
    { name: 'Tourist Database', href: '/tourists', icon: Users, current: location.pathname === '/tourists' },
    { name: 'E-FIR Documents', href: '/efir', icon: FileText, current: location.pathname === '/efir' || location.pathname.startsWith('/efir/') },
    { name: 'Settings', href: '/settings', icon: Settings, current: location.pathname === '/settings' },
  ];

  const handleLogout = () => {
    logout();
  };

  if (!user) return null;

  return (
    <div className="flex flex-col w-64 border-r" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
      {/* Logo Section */}
      <div className="flex items-center justify-center h-16 px-4 border-b" style={{borderColor: '#374151'}}>
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8" style={{color: '#3B82F6'}} />
          <div>
            <h1 className="text-lg font-bold" style={{color: '#F3F4F6'}}>Tourism Safety</h1>
            <p className="text-xs" style={{color: '#9CA3AF'}}>Command Center</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`
                flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                ${item.current
                  ? 'shadow-lg'
                  : 'hover:bg-opacity-50'
                }
              `}
              style={{
                backgroundColor: item.current ? '#3B82F6' : 'transparent',
                color: item.current ? '#FFFFFF' : '#9CA3AF'
              }}
              onMouseEnter={(e) => {
                if (!item.current) {
                  e.target.style.backgroundColor = '#374151';
                  e.target.style.color = '#F3F4F6';
                }
              }}
              onMouseLeave={(e) => {
                if (!item.current) {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.color = '#9CA3AF';
                }
              }}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Officer Profile */}
      <div className="p-4 border-t" style={{borderColor: '#374151'}}>
        <div className="flex items-center space-x-3 mb-4">
          <Avatar className="w-10 h-10">
            <AvatarFallback style={{backgroundColor: '#3B82F6', color: '#FFFFFF'}}>
              {user.full_name.split(' ').map(n => n[0]).join('')}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate" style={{color: '#F3F4F6'}}>
              {user.full_name}
            </p>
            <p className="text-xs truncate" style={{color: '#9CA3AF'}}>
              {user.department}
            </p>
            {user.badge_number && (
              <p className="text-xs" style={{color: '#9CA3AF'}}>
                Badge: {user.badge_number}
              </p>
            )}
          </div>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleLogout}
          className="w-full transition-colors"
          style={{
            borderColor: '#374151',
            color: '#9CA3AF',
            backgroundColor: 'transparent'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#374151';
            e.target.style.color = '#F3F4F6';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
            e.target.style.color = '#9CA3AF';
          }}
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;