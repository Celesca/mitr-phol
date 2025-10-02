import React, { useState, useEffect } from 'react'
import type { FarmData } from './services/farmData'
import { fetchFarmData, THAILAND_CONFIG } from './services/farmData'

// Import Leaflet components
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface StructuredOutput {
  extractedData: Array<{
    question: string;
    columnReference: string;
    dataType: string;
    extractedValue?: string | number;
  }>;
  selectedFarm?: FarmData;
}

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
  const [highlightedFarms, setHighlightedFarms] = useState<Set<string>>(new Set())
  const [showFullSummary, setShowFullSummary] = useState(false)
  const [farmData, setFarmData] = useState<FarmData[]>([])
  const [loading, setLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [transcribedText, setTranscribedText] = useState('')
  const [interimText, setInterimText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [structuredOutput, setStructuredOutput] = useState<StructuredOutput | null>(null)
  const [uploadedAudio, setUploadedAudio] = useState<File | null>(null)
  const [recognition, setRecognition] = useState<any>(null)

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

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = true
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'th-TH' // Thai language
      
      recognitionInstance.onresult = (event: any) => {
        let finalTranscript = ''
        let interimTranscript = ''
        
        // Process all results from the last result index
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
        
        // Append final transcript to the main text
        if (finalTranscript) {
          setTranscribedText(prev => prev + finalTranscript)
        }
        
        // Show interim text (this will be replaced as user continues speaking)
        setInterimText(interimTranscript)
      }
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
      }
      
      recognitionInstance.onend = () => {
        setIsRecording(false)
      }
      
      setRecognition(recognitionInstance)
    }
  }, [])

  const startRecording = () => {
    if (recognition && !isRecording) {
      setTranscribedText('')
      setIsRecording(true)
      recognition.start()
    }
  }

  const stopRecording = () => {
    if (recognition && isRecording) {
      recognition.stop()
      setIsRecording(false)
    }
  }

  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedAudio(file)
      // For now, just set a placeholder text. In a real implementation,
      // you would process the audio file for transcription
      setTranscribedText(`อัปโหลดไฟล์เสียง: ${file.name} (จำลองการถอดเสียง)`)
    }
  }

  const handleFinishTranscription = async () => {
    if (!transcribedText.trim()) return
    
    setIsProcessing(true)
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock structured output generation
    const mockStructuredOutput = {
      extractedData: [
        {
          question: "ในรอบเดือนที่ผ่านมา ท่านให้น้ำอ้อยเฉลี่ยกี่ครั้งต่อเดือน?",
          columnReference: "irrigation_frequency_per_month",
          dataType: "ตัวเลข (ครั้ง)",
          extractedValue: 12
        },
        {
          question: "ในการเพาะปลูกรอบนี้ ท่านมีการทำร่องระบายน้ำหรือบริหารจัดการน้ำท่วมขัง (Drainage) อย่างไรบ้าง (มี/ไม่มี/เป็นบางส่วน)?",
          columnReference: "drainage_effort_encoded",
          dataType: "ตัวเลือก",
          extractedValue: "มี"
        },
        {
          question: "ในรอบการเพาะปลูกที่ผ่านมา ท่านใช้ปุ๋ยไนโตรเจน (N) รวมแล้วประมาณกี่กิโลกรัมต่อไร่?",
          columnReference: "total_N_kg_per_rai",
          dataType: "ตัวเลข (กก./ไร่)",
          extractedValue: 45
        },
        {
          question: "และใช้ปุ๋ยโพแทสเซียม (K) รวมแล้วประมาณกี่กิโลกรัมต่อไร่?",
          columnReference: "total_K_kg_per_rai",
          dataType: "ตัวเลข (กก./ไร่)",
          extractedValue: 25
        },
        {
          question: "ท่านมีการฉีดพ่นปุ๋ยทางใบ (Foliar Spray) เฉลี่ยกี่ครั้งต่อเดือนในช่วงที่ผ่านมา?",
          columnReference: "foliar_spray_frequency_per_month",
          dataType: "ตัวเลข (ครั้ง/เดือน)",
          extractedValue: 2
        },
        {
          question: "ท่านมีการลอกกาบใบอ้อย (Leaf Stripping) เฉลี่ยกี่ครั้งต่อเดือน?",
          columnReference: "leaf_stripping_frequency_per_month",
          dataType: "ตัวเลข (ครั้ง/เดือน)",
          extractedValue: 3
        },
        {
          question: "ท่านมีการพูนโคน/ยกร่อง (Hilling Up) เพื่อช่วยการแตกกอและการระบายน้ำหรือไม่ (มี/ไม่มี/บางส่วน)?",
          columnReference: "hilling_up_encoded",
          dataType: "ตัวเลือก",
          extractedValue: "บางส่วน"
        },
        {
          question: "ในการเตรียมดิน/จัดการวัชพืช ท่านมีการไถพรวน/พรวนดิน (Cultivation) รวมกี่ครั้งตลอดรอบการเพาะปลูกนี้?",
          columnReference: "cultivation_frequency_per_cycle",
          dataType: "ตัวเลข (ครั้ง/รอบ)",
          extractedValue: 4
        },
        {
          question: "ท่านมีการฉีดพ่นยาป้องกัน (Preventive Spraying) โรค/แมลง กี่ครั้งต่อรอบการเพาะปลูก?",
          columnReference: "preventive_spraying_frequency",
          dataType: "ตัวเลข (ครั้ง/รอบ)",
          extractedValue: 6
        },
        {
          question: "โดยรวมแล้ว สารกำจัดศัตรูพืชที่ท่านใช้ มีระดับความเป็นพิษเป็นอย่างไร (เช่น ต่ำ, ปานกลาง, สูง)?",
          columnReference: "pesticide_toxicity_level",
          dataType: "ตัวเลือก (ระดับ)",
          extractedValue: "ปานกลาง"
        }
      ],
      selectedFarm: undefined
    }
    
    setStructuredOutput(mockStructuredOutput)
    setIsProcessing(false)
  }

  const resetTranscription = () => {
    setTranscribedText('')
    setInterimText('')
    setStructuredOutput(null)
    setUploadedAudio(null)
    setIsRecording(false)
    if (recognition) {
      recognition.stop()
    }
  }

  const handleMapClick = () => {
    setCurrentView('map')
  }

  const handleSurveyClick = () => {
    setCurrentView('survey')
  }

  const handleBackToWelcome = () => {
    setCurrentView('welcome')
    setSelectedFarm(null)
    setHighlightedFarms(new Set())
    setShowFullSummary(false)
  }

  const handleFarmClick = (farm: FarmData) => {
    setSelectedFarm(farm)
    setShowFullSummary(false)

    // Calculate distances and highlight nearby farms within 5km radius
    const highlighted = new Set<string>()
    highlighted.add(farm.farm_id)

    const maxDistance = 5000 // 5km in meters

    farmData.forEach((otherFarm) => {
      if (otherFarm.farm_id !== farm.farm_id) {
        const distance = calculateDistance(
          farm.latitude, farm.longitude,
          otherFarm.latitude, otherFarm.longitude
        )
        if (distance <= maxDistance) {
          highlighted.add(otherFarm.farm_id)
        }
      }
    })

    setHighlightedFarms(highlighted)
  }

  // Haversine formula to calculate distance between two points on Earth
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371000 // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLon = (lon2 - lon1) * Math.PI / 180
    const a =
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon/2) * Math.sin(dLon/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return R * c // Distance in meters
  }

  const getMarkerColor = (isAnomaly: boolean, neighborhoodAvgYieldDifference: number) => {
    if (isAnomaly) {
      return neighborhoodAvgYieldDifference > 0 ? '#dc2626' : '#ea580c' // Red for high anomaly, orange for low
    }
    return '#16a34a' // Green for normal
  }

  const createCustomIcon = (isAnomaly: boolean, neighborhoodAvgYieldDifference: number, isHighlighted: boolean, isSelected: boolean) => {
    const baseColor = getMarkerColor(isAnomaly, neighborhoodAvgYieldDifference)

    let finalColor = baseColor
    let opacity = 1
    let borderColor = 'white'
    let borderWidth = 3

    if (selectedFarm) {
      if (isSelected) {
        // Selected farm: bright color with gold border
        borderColor = '#fbbf24'
        borderWidth = 4
      } else if (isHighlighted) {
        // Highlighted neighbors: normal color but slightly brighter
        opacity = 0.9
        borderColor = '#3b82f6'
        borderWidth = 3
      } else {
        // Non-highlighted farms: grayed out
        finalColor = '#9ca3af' // Gray color
        opacity = 0.4
        borderColor = '#d1d5db'
        borderWidth = 2
      }
    }

    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="
        background-color: ${finalColor};
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: ${borderWidth}px solid ${borderColor};
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: white;
        opacity: ${opacity};
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
                      icon={createCustomIcon(
                        farm.is_anomaly,
                        farm.neighborhood_avg_yield_difference,
                        highlightedFarms.has(farm.farm_id),
                        selectedFarm?.farm_id === farm.farm_id
                      )}
                      eventHandlers={{
                        click: () => handleFarmClick(farm),
                      }}
                    >
                      <Popup>
                        <div className="p-2 min-w-[200px]">
                          <h3 className="font-bold text-gray-800">{farm.farmer_name}</h3>
                          <p className="text-sm text-gray-600">ID: {farm.farm_id}</p>
                          <p className={`text-sm font-medium ${farm.is_anomaly ? 'text-red-600' : 'text-green-600'}`}>
                            {farm.is_anomaly ? '⚠️ มีความผิดปกติ' : '✅ ปกติ'}
                          </p>
                          <p className="text-sm">
                            ความแตกต่างผลผลิตเฉลี่ย: <span className={farm.neighborhood_avg_yield_difference < 0 ? 'text-red-600' : 'text-green-600'}>
                              {farm.neighborhood_avg_yield_difference > 0 ? '+' : ''}{farm.neighborhood_avg_yield_difference.toFixed(1)}
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
                      <h3 className="text-lg font-bold text-gray-800">{selectedFarm.farmer_name}</h3>
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
                        <span className="text-sm font-medium">ความแตกต่างผลผลิตเฉลี่ย:</span>
                        <span className={`font-bold ${
                          selectedFarm.neighborhood_avg_yield_difference < 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {selectedFarm.neighborhood_avg_yield_difference > 0 ? '+' : ''}{selectedFarm.neighborhood_avg_yield_difference.toFixed(1)}
                        </span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">การวิเคราะห์จาก AI:</h4>
                      <div className="bg-white rounded-lg p-3 border">
                        <p className="text-sm text-gray-600 leading-relaxed">
                          {showFullSummary
                            ? selectedFarm.llm_reasoning
                            : `${selectedFarm.llm_reasoning.substring(0, 100)}...`
                          }
                        </p>
                        {selectedFarm.llm_reasoning.length > 100 && (
                          <button
                            onClick={() => setShowFullSummary(!showFullSummary)}
                            className="text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium"
                          >
                            {showFullSummary ? 'แสดงน้อยลง' : 'แสดงทั้งหมด'}
                          </button>
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">เพื่อนบ้านใกล้เคียง:</h4>
                      <div className="bg-white rounded-lg p-3 border">
                        <p className="text-sm text-gray-600">
                          แปลงใกล้เคียงในรัศมี 5 กม.: {(highlightedFarms.size - 1)} แปลง
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          แปลงเหล่านี้จะถูกไฮไลต์บนแผนที่
                        </p>
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
                      <div className="w-4 h-4 bg-yellow-400 rounded-full mr-2 border-2 border-yellow-600"></div>
                      <span className="text-xs text-gray-600">แปลงที่เลือก</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-blue-400 rounded-full mr-2 border-2 border-blue-600"></div>
                      <span className="text-xs text-gray-600">เพื่อนบ้านใกล้เคียง (≤5km)</span>
                    </div>
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
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-gray-400 rounded-full mr-2 opacity-40"></div>
                      <span className="text-xs text-gray-600">อื่นๆ (ถูกปิดเสียง)</span>
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
        <div className="max-w-4xl mx-auto">
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
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-800 mb-2">ถอดเสียงและวิเคราะห์</h1>
              <p className="text-gray-600">พูดหรืออัปโหลดไฟล์เสียงเพื่อวิเคราะห์สภาพแปลงอ้อย</p>
            </div>

            {/* Voice Recording Section */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800">บันทึกเสียงสด</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">คลิกเพื่อเริ่มบันทึกเสียงและพูดเกี่ยวกับสภาพแปลงอ้อยของคุณ</p>
                <div className="flex items-center justify-center">
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`flex items-center justify-center w-16 h-16 rounded-full font-medium transition-all duration-200 transform hover:scale-105 ${
                      isRecording
                        ? 'bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-200'
                        : 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg shadow-blue-200'
                    }`}
                  >
                    {isRecording ? (
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <rect x="6" y="4" width="4" height="16"/>
                        <rect x="14" y="4" width="4" height="16"/>
                      </svg>
                    ) : (
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="3"/>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 1 14.14 0"/>
                      </svg>
                    )}
                  </button>
                </div>
                <div className="text-center mt-3">
                  {isRecording ? (
                    <div className="flex items-center justify-center text-red-600">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                      <span className="text-sm font-medium">กำลังบันทึก...</span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">คลิกเพื่อเริ่มบันทึก</span>
                  )}
                </div>
                {!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window) && (
                  <div className="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <p className="text-sm text-orange-700 text-center">
                      ⚠️ เบราว์เซอร์นี้ไม่รองรับการบันทึกเสียง<br/>
                      กรุณาใช้อัปโหลดไฟล์เสียงแทน
                    </p>
                  </div>
                )}
              </div>

              {/* Audio Upload Section */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800">อัปโหลดไฟล์เสียง</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">เลือกไฟล์เสียงที่บันทึกไว้เพื่อทำการถอดเสียง</p>
                <div className="text-center">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleAudioUpload}
                    className="hidden"
                    id="audio-upload"
                  />
                  <label
                    htmlFor="audio-upload"
                    className="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 cursor-pointer transition-colors shadow-md hover:shadow-lg"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                    </svg>
                    เลือกไฟล์เสียง
                  </label>
                  {uploadedAudio && (
                    <div className="mt-3 p-2 bg-green-100 border border-green-300 rounded-lg">
                      <p className="text-sm text-green-800">📁 {uploadedAudio.name}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Transcription Display */}
            {(transcribedText || interimText) && (
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-medium text-gray-800 mb-3">ข้อความที่ถอดได้:</h3>
                <div className="bg-white rounded-lg p-3 border min-h-[100px] max-h-[200px] overflow-y-auto">
                  <p className="text-gray-700 whitespace-pre-wrap">
                    {transcribedText}
                    {interimText && (
                      <span className="text-gray-500 italic">{interimText}</span>
                    )}
                  </p>
                  {isRecording && (
                    <div className="flex items-center mt-2 text-sm text-blue-600">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                      กำลังฟัง...
                    </div>
                  )}
                </div>
                <div className="flex space-x-3 mt-3">
                  <button
                    onClick={handleFinishTranscription}
                    disabled={isProcessing || (!transcribedText.trim() && !interimText.trim())}
                    className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isProcessing ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                        กำลังวิเคราะห์...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        เสร็จสิ้น
                      </>
                    )}
                  </button>
                  <button
                    onClick={resetTranscription}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    ล้างข้อมูล
                  </button>
                </div>
              </div>
            )}

            {/* Structured Output Display */}
            {structuredOutput && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-800">ผลการวิเคราะห์ข้อมูล</h3>
                </div>

                {/* Farm Selection */}
                <div className="bg-white rounded-lg border border-gray-200 shadow-sm mb-6">
                  <div className="px-4 py-3 border-b border-gray-200">
                    <h4 className="text-lg font-semibold text-gray-800">เลือกแปลงอ้อย</h4>
                  </div>
                  <div className="p-4">
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        ค้นหาและเลือกแปลงอ้อย
                      </label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        value={structuredOutput.selectedFarm?.farm_id || ''}
                        onChange={(e) => {
                          const selectedFarmId = e.target.value
                          const selectedFarm = farmData.find(farm => farm.farm_id === selectedFarmId)
                          setStructuredOutput(prev => prev ? {
                            ...prev,
                            selectedFarm: selectedFarm
                          } : null)
                        }}
                      >
                        <option value="">เลือกแปลงอ้อย...</option>
                        {farmData.map((farm) => (
                          <option key={farm.farm_id} value={farm.farm_id}>
                            {farm.farm_id} - {farm.farmer_name}
                          </option>
                        ))}
                      </select>
                    </div>
                    {structuredOutput.selectedFarm && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center">
                          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/>
                            </svg>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-green-800">
                              เลือกแล้ว: {structuredOutput.selectedFarm.farm_id} - {structuredOutput.selectedFarm.farmer_name}
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                              ข้อมูลการถอดเสียงจะถูกบันทึกสำหรับแปลงนี้
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Extracted Data Table */}
                <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
                  <div className="px-4 py-3 border-b border-gray-200">
                    <h4 className="text-lg font-semibold text-gray-800">ข้อมูลที่ได้จากการถอดเสียง</h4>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            คำถามที่ถามเกษตรกร
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ข้อมูลที่ต้องการ (Column Reference)
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ประเภทข้อมูล
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ค่าที่ได้
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {structuredOutput.extractedData.map((item, index) => (
                          <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {item.question}
                            </td>
                            <td className="px-6 py-4 text-sm font-mono text-blue-600">
                              {item.columnReference}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700">
                              {item.dataType}
                            </td>
                            <td className="px-6 py-4 text-sm font-semibold text-green-600">
                              {item.extractedValue !== undefined ? (
                                typeof item.extractedValue === 'number' ? 
                                  item.extractedValue : 
                                  item.extractedValue
                              ) : (
                                <span className="text-gray-400">ไม่ได้ระบุ</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
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
