import React from 'react';
import { MapPin } from 'lucide-react';

const MiniMap = ({ locationHistory = [], currentLocation, className = "" }) => {
  // Generate breadcrumb trail with realistic movement
  const generateTrail = () => {
    const basePoints = [
      { x: 20, y: 60, time: '2 hrs ago' },
      { x: 35, y: 45, time: '1.5 hrs ago' },
      { x: 50, y: 55, time: '1 hr ago' },
      { x: 65, y: 40, time: '30 min ago' },
      { x: 80, y: 35, time: 'Current' }
    ];
    return basePoints;
  };

  const trailPoints = generateTrail();

  return (
    <div className={`relative bg-slate-600 rounded-lg overflow-hidden ${className}`}>
      {/* Map Background Grid */}
      <div className="absolute inset-0 opacity-20">
        <div className="w-full h-full" style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)',
          backgroundSize: '8px 8px'
        }}></div>
      </div>
      
      {/* Simulated Map Features (Roads/Areas) */}
      <div className="absolute inset-0">
        {/* Main road */}
        <div className="absolute bg-slate-500 opacity-40" style={{
          left: '10%',
          top: '45%',
          width: '80%',
          height: '6px',
          borderRadius: '3px',
          transform: 'rotate(-5deg)'
        }}></div>
        
        {/* Side road */}
        <div className="absolute bg-slate-500 opacity-30" style={{
          left: '45%',
          top: '20%',
          width: '4px',
          height: '50%',
          borderRadius: '2px',
          transform: 'rotate(10deg)'
        }}></div>
        
        {/* Safe zone indicator */}
        <div className="absolute bg-emerald-500 opacity-20 rounded-full" style={{
          left: '60%',
          top: '25%',
          width: '30px',
          height: '30px'
        }}></div>
      </div>
      
      {/* Location Trail */}
      <div className="absolute inset-0">
        {/* Trail line connecting points */}
        <svg className="absolute inset-0 w-full h-full">
          <path
            d={`M${trailPoints.map(p => `${p.x},${p.y}`).join(' L')}`}
            stroke="#60a5fa"
            strokeWidth="2"
            fill="none"
            strokeDasharray="3,3"
            className="opacity-80"
          />
        </svg>
        
        {/* Location points */}
        {trailPoints.map((point, index) => (
          <div
            key={index}
            className={`absolute transform -translate-x-1/2 -translate-y-1/2 ${
              index === trailPoints.length - 1 
                ? 'w-4 h-4 bg-red-500 animate-pulse' 
                : 'w-3 h-3 bg-blue-400'
            } rounded-full border-2 border-white shadow-sm`}
            style={{
              left: `${point.x}%`,
              top: `${point.y}%`
            }}
            title={point.time}
          />
        ))}
      </div>
      
      {/* Map Controls */}
      <div className="absolute top-2 right-2 flex flex-col space-y-1">
        <button className="w-6 h-6 bg-slate-700 hover:bg-slate-600 text-white text-xs rounded flex items-center justify-center border border-slate-500">
          +
        </button>
        <button className="w-6 h-6 bg-slate-700 hover:bg-slate-600 text-white text-xs rounded flex items-center justify-center border border-slate-500">
          -
        </button>
      </div>
      
      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-slate-800 bg-opacity-90 rounded px-2 py-1">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
          <span className="text-xs text-slate-300">Trail</span>
          <div className="w-2 h-2 bg-red-500 rounded-full ml-2"></div>
          <span className="text-xs text-slate-300">Current</span>
        </div>
      </div>
      
      {/* Current location info overlay */}
      <div className="absolute top-2 left-2 bg-slate-800 bg-opacity-90 rounded px-2 py-1">
        <div className="flex items-center space-x-1">
          <MapPin className="w-3 h-3 text-blue-400" />
          <span className="text-xs text-slate-300">Live Trail</span>
        </div>
      </div>
    </div>
  );
};

export default MiniMap;