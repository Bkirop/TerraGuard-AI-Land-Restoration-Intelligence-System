import React, { useState } from 'react';
import LocationSelector from './components/LocationSelector';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [locationName, setLocationName] = useState('');

  const handleLocationSelect = (id, name) => {
    setSelectedLocation(id);
    setLocationName(name);
  };

  return (
    <div className="App">
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #2c5f2d 0%, #1b3a1f 100%)',
        color: 'white',
        padding: '20px 0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 20px' }}>
          <h1 style={{ fontSize: '28px', margin: 0 }}>
            🌍 TerraGuard AI
          </h1>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9, fontSize: '14px' }}>
            Land Restoration Intelligence System
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
        <LocationSelector onLocationSelect={handleLocationSelect} />

        {selectedLocation ? (
          <Dashboard
            locationId={selectedLocation}
            locationName={locationName}
          />
        ) : (
          <div style={{
            background: 'white',
            padding: '60px',
            borderRadius: '12px',
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h2>Welcome to TerraGuard AI</h2>
            <p style={{ color: '#666', marginTop: '10px' }}>
              Select a location above to view its restoration dashboard
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;