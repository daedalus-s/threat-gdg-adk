import React, { useState, useEffect } from 'react';
import { AlertTriangle, Phone, Bell, X, Camera, Activity } from 'lucide-react';

const ThreatDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Simulate real-time data updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'threat_decision') {
        setAlerts(prev => [data, ...prev].slice(0, 10));
      }
    };

    return () => ws.close();
  }, []);

  const handleCall911 = (incident) => {
    // In demo, just show alert
    alert(`Calling 911 for incident: ${incident.id}`);
  };

  const handleNotifyContact = (incident) => {
    alert(`Notifying emergency contact for: ${incident.id}`);
  };

  const getThreatColor = (level) => {
    const colors = {
      critical: 'bg-red-600',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-blue-500',
      none: 'bg-green-500'
    };
    return colors[level] || colors.none;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Home Threat Detection</h1>
        <div className="flex gap-4 text-sm">
          <span className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-green-400" />
            {devices.filter(d => d.online).length} Devices Online
          </span>
          <span className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            {alerts.filter(a => a.threat_level !== 'none').length} Active Alerts
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alert Feed */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
          
          {alerts.length === 0 && (
            <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-400">
              No active alerts. System monitoring...
            </div>
          )}

          {alerts.map((alert, idx) => (
            <div
              key={idx}
              className={`bg-gray-800 rounded-lg p-4 border-l-4 ${
                getThreatColor(alert.threat_level)
              } cursor-pointer hover:bg-gray-750 transition`}
              onClick={() => setSelectedIncident(alert)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-semibold text-lg">
                    {alert.threat_level.toUpperCase()} Threat
                  </span>
                </div>
                <span className="text-sm text-gray-400">
                  {new Date(alert.timestamp * 1000).toLocaleTimeString()}
                </span>
              </div>
              
              <p className="text-gray-300 mb-3">
                {alert.decision?.message_to_user || alert.decision?.reasoning}
              </p>
              
              <div className="flex gap-2">
                {alert.decision?.call_911 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCall911(alert);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-medium transition"
                  >
                    <Phone className="w-4 h-4" />
                    Call 911
                  </button>
                )}
                
                {alert.decision?.notify_contacts && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleNotifyContact(alert);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition"
                  >
                    <Bell className="w-4 h-4" />
                    Notify Contact
                  </button>
                )}
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setAlerts(prev => prev.filter((_, i) => i !== idx));
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition"
                >
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Camera Grid */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold mb-4">Live Cameras</h2>
          
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4, 5].map(camId => (
              <div
                key={camId}
                className="bg-gray-800 rounded-lg p-4 aspect-video flex items-center justify-center relative"
              >
                <Camera className="w-8 h-8 text-gray-600" />
                <span className="absolute top-2 left-2 text-xs bg-green-500 px-2 py-1 rounded">
                  CAM {camId}
                </span>
              </div>
            ))}
          </div>

          {/* Device Status */}
          <div className="bg-gray-800 rounded-lg p-4 mt-6">
            <h3 className="font-semibold mb-3">Device Status</h3>
            <div className="space-y-2 text-sm">
              {['Smartwatch', 'Wearable', 'Microphone', 'Smoke Detector'].map(device => (
                <div key={device} className="flex justify-between items-center">
                  <span>{device}</span>
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                    Online
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Incident Modal */}
      {selectedIncident && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg max-w-2xl w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold">Incident Details</h2>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Threat Level</h3>
                <span className={`px-3 py-1 rounded-full text-sm ${getThreatColor(selectedIncident.threat_level)}`}>
                  {selectedIncident.threat_level.toUpperCase()}
                </span>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Reasoning</h3>
                <p className="text-gray-300">
                  {selectedIncident.decision?.reasoning}
                </p>
              </div>
              
              {selectedIncident.decision?.evidence && (
                <div>
                  <h3 className="font-semibold mb-2">Evidence</h3>
                  <ul className="list-disc list-inside text-gray-300">
                    {selectedIncident.decision.evidence.map((ev, i) => (
                      <li key={i}>{ev}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => handleCall911(selectedIncident)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-medium"
                >
                  <Phone className="w-5 h-5" />
                  Call 911
                </button>
                <button
                  onClick={() => handleNotifyContact(selectedIncident)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
                >
                  <Bell className="w-5 h-5" />
                  Notify Contact
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreatDashboard;