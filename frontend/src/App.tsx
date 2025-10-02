import { useState } from 'react'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState<'welcome' | 'map' | 'survey'>('welcome')

  const handleMapClick = () => {
    setCurrentView('map')
  }

  const handleSurveyClick = () => {
    setCurrentView('survey')
  }

  const handleBackToWelcome = () => {
    setCurrentView('welcome')
  }

  if (currentView === 'map') {
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
            <h1 className="text-2xl font-bold text-gray-800 mb-4">แผนที่แปลงอ้อย</h1>
            <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
              <p className="text-gray-500">แผนที่กำลังโหลด...</p>
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
