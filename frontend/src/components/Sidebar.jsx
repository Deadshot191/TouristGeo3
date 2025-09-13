import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Map, AlertTriangle, Users, Settings, LogOut, Shield } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { mockOfficer } from '../mock';

const Sidebar = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Live Map', href: '/', icon: Map, current: location.pathname === '/' },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle, current: location.pathname === '/alerts' },
    { name: 'Tourist Database', href: '/tourists', icon: Users, current: location.pathname === '/tourists' },
    { name: 'Settings', href: '/settings', icon: Settings, current: location.pathname === '/settings' },
  ];

  return (
    <div className="flex flex-col w-64 bg-slate-800 border-r border-slate-700">
      {/* Logo Section */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-lg font-bold text-white">Tourism Safety</h1>
            <p className="text-xs text-slate-400">Command Center</p>
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
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }
              `}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Officer Profile */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center space-x-3 mb-4">
          <Avatar className="w-10 h-10">
            <AvatarImage src={mockOfficer.avatar} alt={mockOfficer.name} />
            <AvatarFallback className="bg-blue-600 text-white">
              {mockOfficer.name.split(' ').map(n => n[0]).join('')}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {mockOfficer.name}
            </p>
            <p className="text-xs text-slate-400 truncate">
              {mockOfficer.department}
            </p>
            <p className="text-xs text-slate-500">
              Badge: {mockOfficer.badge}
            </p>
          </div>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;