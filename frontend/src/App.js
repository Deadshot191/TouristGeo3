import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import LiveMap from './pages/LiveMap';
import Alerts from './pages/Alerts';
import TouristDatabase from './pages/TouristDatabase';
import Settings from './pages/Settings';
import EFIRDocuments from './pages/EFIRDocuments';
import EFIRForm from './pages/EFIRForm';
import EFIRDetail from './pages/EFIRDetail';
import TouristDetailModal from './components/TouristDetailModal';
import { wsManager } from './services/api';

function AppContent() {
  const [selectedTourist, setSelectedTourist] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    wsManager.connectDashboard();
    
    return () => {
      wsManager.disconnect();
    };
  }, []);

  const handleTouristSelect = (tourist) => {
    setSelectedTourist(tourist);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedTourist(null);
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen" style={{backgroundColor: '#111827'}}>
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route 
              path="/" 
              element={<LiveMap onTouristSelect={handleTouristSelect} />} 
            />
            <Route 
              path="/alerts" 
              element={<Alerts onTouristSelect={handleTouristSelect} />} 
            />
            <Route 
              path="/tourists" 
              element={<TouristDatabase onTouristSelect={handleTouristSelect} />} 
            />
            <Route 
              path="/settings" 
              element={<Settings />} 
            />
          </Routes>
        </main>
        {isModalOpen && selectedTourist && (
          <TouristDetailModal
            tourist={selectedTourist}
            isOpen={isModalOpen}
            onClose={handleCloseModal}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;