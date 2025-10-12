import React, { useState, useEffect } from 'react';
import { MapPin, Plus } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const LocationSelector = ({ onLocationSelect }) => {
  const [locations, setLocations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/locations`);
      
      console.log('API Response:', response.data); // Debug log
      
      // Handle different response formats
      let locationData = [];
      
      if (Array.isArray(response.data)) {
        locationData = response.data;
      } else if (response.data.data && Array.isArray(response.data.data)) {
        locationData = response.data.data;
      } else if (response.data.locations && Array.isArray(response.data.locations)) {
        locationData = response.data.locations;
      }
      
      setLocations(locationData);
      
      if (locationData.length > 0) {
        const firstId = locationData[0].id;
        setSelectedId(firstId);
        onLocationSelect(firstId, locationData[0].name);
      }
      
      setError(null);
    } catch (error) {
      console.error('Failed to load locations:', error);
      setError('Failed to load locations');
      
      // Fallback to default locations
      const fallbackLocations = [
        { id: '97bae706-f42d-4fdc-997f-e80c91879663', name: 'Nakuru Conservation Area', country: 'Kenya' },
        { id: '7f1caf9b-cf3b-4566-a310-dbe1566551a', name: 'Maasai Mara Restoration Site', country: 'Kenya' }
      ];
      setLocations(fallbackLocations);
      setSelectedId(fallbackLocations[0].id);
      onLocationSelect(fallbackLocations[0].id, fallbackLocations[0].name);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const id = e.target.value;
    const location = locations.find(loc => loc.id === id);
    setSelectedId(id);
    if (location) {
      onLocationSelect(id, location.name);
    }
  };

  if (loading) {
    return (
      <div style={{
        background: 'white',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        Loading locations...
      </div>
    );
  }

  if (error && locations.length === 0) {
    return (
      <div style={{
        background: '#fff3cd',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px',
        color: '#856404'
      }}>
        ⚠️ {error} - Using fallback data
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      padding: '15px 20px',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '15px'
    }}>
      <MapPin size={24} color="#2c5f2d" />
      <select
        value={selectedId || ''}
        onChange={handleChange}
        style={{
          flex: 1,
          padding: '10px',
          fontSize: '16px',
          border: '1px solid #ddd',
          borderRadius: '6px',
          background: 'white',
          cursor: 'pointer'
        }}
      >
        <option value="">Select Location...</option>
        {locations.map(loc => (
          <option key={loc.id} value={loc.id}>
            {loc.name} - {loc.country}
          </option>
        ))}
      </select>
      <button
        style={{
          padding: '10px 15px',
          background: '#2c5f2d',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '5px'
        }}
        title="Add new location"
      >
        <Plus size={18} />
        Add
      </button>
    </div>
  );
};

export default LocationSelector;