// Farm data service
export interface FarmData {
  farm_id: string
  farmer_name: string
  neighborhood_avg_yield_difference: number
  is_anomaly: boolean
  llm_reasoning: string
  nearest_neighbors_indices: number[]
  latitude: number
  longitude: number
}

// Sample farm data - replace with API calls in production
export const sampleFarmData: FarmData[] = [
  {
    farm_id: "F001",
    farmer_name: "นายสมชาย ใจดี",
    neighborhood_avg_yield_difference: -1.2,
    is_anomaly: true,
    llm_reasoning: "แปลงอ้อยนี้มีปัญหาเรื่องการให้น้ำที่ไม่เพียงพอ ส่งผลให้ความหวานของอ้อยต่ำกว่าค่าเฉลี่ย ควรปรับปรุงระบบการให้น้ำและเพิ่มปริมาณน้ำให้เพียงพอต่อความต้องการของอ้อย แปลงนี้ควรได้รับการดูแลเป็นพิเศษในการรดน้ำและการจัดการดิน",
    nearest_neighbors_indices: [1, 2, 3, 4, 5],
    latitude: 13.7563,
    longitude: 100.5018
  },
  {
    farm_id: "F002",
    farmer_name: "นางสาวสมหญิง รักงาน",
    neighborhood_avg_yield_difference: 0.8,
    is_anomaly: false,
    llm_reasoning: "แปลงอ้อยนี้อยู่ในสภาพที่ดี ปริมาณน้ำและการจัดการแปลงอยู่ในระดับมาตรฐาน สามารถเพิ่มผลผลิตได้โดยการปรับปรุงพันธุ์อ้อยและการใช้ปุ๋ยอย่างเหมาะสม แปลงนี้เป็นตัวอย่างที่ดีในการจัดการแปลงอ้อย",
    nearest_neighbors_indices: [0, 2, 3, 6, 7],
    latitude: 13.7650,
    longitude: 100.6477
  },
  {
    farm_id: "F003",
    farmer_name: "นายวิชัย ประสบการณ์",
    neighborhood_avg_yield_difference: -0.5,
    is_anomaly: false,
    llm_reasoning: "แปลงอ้อยนี้มีปัญหาเรื่องวัชพืชที่ขึ้นรก ส่งผลให้การเจริญเติบโตของอ้อยไม่เต็มที่ ควรเพิ่มความถี่ในการตัดแต่งและกำจัดวัชพืช แปลงนี้ต้องการการดูแลในการจัดการวัชพืชมากขึ้น",
    nearest_neighbors_indices: [0, 1, 4, 5, 7],
    latitude: 13.7279,
    longitude: 100.7483
  },
  {
    farm_id: "F004",
    farmer_name: "นางสาวนิด จริงใจ",
    neighborhood_avg_yield_difference: 1.5,
    is_anomaly: true,
    llm_reasoning: "แปลงอ้อยนี้มีผลผลิตสูงกว่าค่าเฉลี่ยอย่างมาก ควรศึกษาปัจจัยที่ทำให้แปลงนี้ประสบความสำเร็จเพื่อนำไปปรับใช้กับแปลงอื่น แปลงนี้เป็นแบบอย่างที่ดีในการจัดการแปลงอ้อยที่มีประสิทธิภาพสูง",
    nearest_neighbors_indices: [1, 2, 5, 6, 7],
    latitude: 13.6930,
    longitude: 100.6004
  },
  {
    farm_id: "F005",
    farmer_name: "นายประสิทธิ์ ทำงาน",
    neighborhood_avg_yield_difference: 0.2,
    is_anomaly: false,
    llm_reasoning: "แปลงอ้อยนี้อยู่ในสภาพปกติ ปริมาณน้ำและการจัดการอยู่ในระดับที่ดี ควรคงรูปแบบการจัดการปัจจุบันไว้ แปลงนี้แสดงให้เห็นถึงการจัดการที่สมดุลและมีประสิทธิภาพ",
    nearest_neighbors_indices: [0, 2, 3, 6, 7],
    latitude: 13.6804,
    longitude: 100.6065
  },
  {
    farm_id: "F006",
    farmer_name: "นายชัยวัฒน์ มุ่งมั่น",
    neighborhood_avg_yield_difference: -0.8,
    is_anomaly: true,
    llm_reasoning: "แปลงอ้อยนี้มีปัญหาเรื่องโรคและแมลง ส่งผลให้ผลผลิตต่ำกว่าค่าเฉลี่ย ควรเพิ่มการตรวจสอบและการใช้สารป้องกันอย่างเหมาะสม แปลงนี้ต้องการการดูแลด้านการป้องกันโรคและแมลงเป็นพิเศษ",
    nearest_neighbors_indices: [1, 3, 4, 5, 7],
    latitude: 13.7200,
    longitude: 100.5200
  },
  {
    farm_id: "F007",
    farmer_name: "นางสาวเพ็ญศรี อดทน",
    neighborhood_avg_yield_difference: 0.3,
    is_anomaly: false,
    llm_reasoning: "แปลงอ้อยนี้อยู่ในสภาพที่ดีโดยรวม การจัดการแปลงและการดูแลอยู่ในระดับมาตรฐาน ควรคงรูปแบบการจัดการปัจจุบันและติดตามผลอย่างต่อเนื่อง",
    nearest_neighbors_indices: [1, 3, 4, 5, 6],
    latitude: 13.8500,
    longitude: 100.4000
  },
  {
    farm_id: "F008",
    farmer_name: "นายธนวัฒน์ พัฒนา",
    neighborhood_avg_yield_difference: -1.8,
    is_anomaly: true,
    llm_reasoning: "แปลงอ้อยนี้มีปัญหาหลายประการรวมถึงการให้น้ำและการจัดการดิน ควรได้รับการปรับปรุงอย่างเร่งด่วน แปลงนี้ต้องการการดูแลและปรับปรุงอย่างครอบคลุม",
    nearest_neighbors_indices: [0, 1, 2, 3, 6],
    latitude: 13.9200,
    longitude: 100.6000
  }
]

// Function to fetch farm data (replace with actual API call)
export const fetchFarmData = async (): Promise<FarmData[]> => {
  try {
    // Load data from the JSON file in public directory
    const response = await fetch('/data/anomalous_farms_data_filtered.json')
    if (!response.ok) {
      throw new Error('Failed to load farm data')
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error loading farm data:', error)
    // Fallback to sample data if JSON loading fails
    return sampleFarmData
  }
}

// Thailand map bounds and center (focused on Kanchanaburi region where the farm data is located)
export const THAILAND_CONFIG = {
  center: [14.0, 99.5] as [number, number], // Center of Kanchanaburi region
  bounds: [
    [13.5, 98.5], // Southwest
    [15.0, 100.5] // Northeast
  ] as [[number, number], [number, number]],
  defaultZoom: 9 // Higher zoom for regional focus
}