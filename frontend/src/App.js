import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Sidebar from './components/Sidebar';
import LiveMap from './pages/LiveMap';
import Alerts from './pages/Alerts';
import TouristDatabase from './pages/TouristDatabase';
import Settings from './pages/Settings';
import TouristDetailModal from './components/TouristDetailModal';

function App() {
  const [selectedTourist, setSelectedTourist] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleTouristSelect = (tourist) => {
    setSelectedTourist(tourist);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedTourist(null);
  };

  return (
    <div className="App">
      <BrowserRouter>
        <div className="flex h-screen bg-slate-900">
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
      </BrowserRouter>
    </div>
  );
}

export default App;