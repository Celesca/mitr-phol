import { useState, useEffect } from 'react'
import './App.css'

// Import Leaflet components
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Import data service
import type { FarmData } from './services/farmData'
import { fetchFarmData, THAILAND_CONFIG } from './services/farmData'

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

function App() {
  const [currentView, setCurrentView] = useState<'welcome' | 'map' | 'survey'>('welcome')
  const [selectedFarm, setSelectedFarm] = useState<FarmData | null>(null)
  const [showFullSummary, setShowFullSummary] = useState(false)
  const [farmData, setFarmData] = useState<FarmData[]>([])
  const [loading, setLoading] = useState(false)

  // Load farm data on component mount
  useEffect(() => {
    const loadFarmData = async () => {
      setLoading(true)
      try {
        const data = await fetchFarmData()
        setFarmData(data)
      } catch (error) {
        console.error('Error loading farm data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadFarmData()
  }, [])

  const handleMapClick = () => {
    setCurrentView('map')
  }

  const handleSurveyClick = () => {
    setCurrentView('survey')
  }

  const handleBackToWelcome = () => {
    setCurrentView('welcome')
    setSelectedFarm(null)
    setShowFullSummary(false)
  }

  const handleFarmClick = (farm: FarmData) => {
    setSelectedFarm(farm)
    setShowFullSummary(false)
  }

  const getMarkerColor = (isAnomaly: boolean, cssDifference: number) => {
    if (isAnomaly) {
      return cssDifference > 0 ? '#dc2626' : '#ea580c' // Red for high anomaly, orange for low
    }
    return '#16a34a' // Green for normal
  }

  const createCustomIcon = (isAnomaly: boolean, cssDifference: number) => {
    const color = getMarkerColor(isAnomaly, cssDifference)
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="
        background-color: ${color};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: white;
      ">${isAnomaly ? '!' : '✓'}</div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    })
  }

  if (currentView === 'map') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <button
                onClick={handleBackToWelcome}
                className="flex items-center text-green-600 mb-2 hover:text-green-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                กลับ
              </button>
              <h1 className="text-2xl font-bold text-gray-800">แผนที่แปลงอ้อยประเทศไทย</h1>
              <p className="text-gray-600 text-sm mt-1">
                แสดงตำแหน่งแปลงอ้อยและข้อมูลความผิดปกติ
              </p>
              {loading && (
                <div className="mt-2 text-sm text-blue-600">
                  กำลังโหลดข้อมูล...
                </div>
              )}
            </div>

            <div className="flex flex-col lg:flex-row">
              {/* Map Container */}
              <div className="flex-1 h-96 lg:h-[600px]">
                <MapContainer
                  center={THAILAND_CONFIG.center}
                  zoom={THAILAND_CONFIG.defaultZoom}
                  style={{ height: '100%', width: '100%' }}
                  maxBounds={THAILAND_CONFIG.bounds}
                  maxBoundsViscosity={1.0}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  {farmData.map((farm: FarmData) => (
                    <Marker
                      key={farm.farm_id}
                      position={[farm.latitude, farm.longitude]}
                      icon={createCustomIcon(farm.is_anomaly, farm.css_difference)}
                      eventHandlers={{
                        click: () => handleFarmClick(farm),
                      }}
                    >
                      <Popup>
                        <div className="p-2 min-w-[200px]">
                          <h3 className="font-bold text-gray-800">{farm.farm_name}</h3>
                          <p className="text-sm text-gray-600">ID: {farm.farm_id}</p>
                          <p className={`text-sm font-medium ${farm.is_anomaly ? 'text-red-600' : 'text-green-600'}`}>
                            {farm.is_anomaly ? '⚠️ มีความผิดปกติ' : '✅ ปกติ'}
                          </p>
                          <p className="text-sm">
                            ความแตกต่าง CSS: <span className={farm.css_difference < 0 ? 'text-red-600' : 'text-green-600'}>
                              {farm.css_difference > 0 ? '+' : ''}{farm.css_difference.toFixed(1)}
                            </span>
                          </p>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>

              {/* Farm Details Panel */}
              <div className="w-full lg:w-80 bg-gray-50 p-4 border-t lg:border-t-0 lg:border-l border-gray-200">
                {selectedFarm ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-800">{selectedFarm.farm_name}</h3>
                      <p className="text-sm text-gray-600">รหัสแปลง: {selectedFarm.farm_id}</p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">สถานะ:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          selectedFarm.is_anomaly
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {selectedFarm.is_anomaly ? 'ผิดปกติ' : 'ปกติ'}
                        </span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">ความแตกต่าง CSS:</span>
                        <span className={`font-bold ${
                          selectedFarm.css_difference < 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {selectedFarm.css_difference > 0 ? '+' : ''}{selectedFarm.css_difference.toFixed(1)}
                        </span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">สรุปการดำเนินการ:</h4>
                      <div className="bg-white rounded-lg p-3 border">
                        <p className="text-sm text-gray-600 leading-relaxed">
                          {showFullSummary
                            ? selectedFarm.summarize_action
                            : `${selectedFarm.summarize_action.substring(0, 100)}...`
                          }
                        </p>
                        {selectedFarm.summarize_action.length > 100 && (
                          <button
                            onClick={() => setShowFullSummary(!showFullSummary)}
                            className="text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium"
                          >
                            {showFullSummary ? 'แสดงน้อยลง' : 'แสดงทั้งหมด'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500">
                    <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <p className="text-sm">คลิกที่จุดบนแผนที่เพื่อดูรายละเอียด</p>
                  </div>
                )}

                {/* Legend */}
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">สัญลักษณ์:</h4>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-green-600 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-600">ปกติ</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-600">ผิดปกติ (ต่ำ)</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-red-600 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-600">ผิดปกติ (สูง)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (currentView === 'survey') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">
            <button
              onClick={handleBackToWelcome}
              className="flex items-center text-green-600 mb-4 hover:text-green-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              กลับ
            </button>
            <h1 className="text-2xl font-bold text-gray-800 mb-4">แบบสอบถาม</h1>
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-600">แบบสอบถามกำลังพัฒนา...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-full mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">มิตรผล</h1>
          <p className="text-lg text-gray-600">ผู้ช่วยชาวไร่อ้อย</p>
          <p className="text-sm text-gray-500 mt-1">ระบบจัดการและดูแลแปลงอ้อย</p>
        </div>

        {/* Main Options */}
        <div className="space-y-4">
          {/* Map Option */}
          <div
            onClick={handleMapClick}
            className="bg-white rounded-2xl shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                </div>
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-gray-800">See the map</h3>
                <p className="text-gray-600 text-sm">ดูแผนที่แปลงอ้อยและข้อมูลพื้นที่</p>
              </div>
              <div className="flex-shrink-0">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Survey Option */}
          <div
            onClick={handleSurveyClick}
            className="bg-white rounded-2xl shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-gray-800">ตอบแบบสอบถาม</h3>
                <p className="text-gray-600 text-sm">กรอกข้อมูลและประเมินสภาพแปลงอ้อย</p>
              </div>
              <div className="flex-shrink-0">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-500">
            © 2025 มิตรผล - ระบบจัดการแปลงอ้อยอัจฉริยะ
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
