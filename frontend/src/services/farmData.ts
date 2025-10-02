// Farm data service
export interface FarmData {
  farm_id: string
  farm_name: string
  latitude: number
  longitude: number
  css_difference: number
  is_anomaly: boolean
  summarize_action: string
}

// Sample farm data - replace with API calls in production
export const sampleFarmData: FarmData[] = [
  {
    farm_id: "F001",
    farm_name: "แปลงอ้อยหนองใหญ่",
    latitude: 13.7563,
    longitude: 100.5018,
    css_difference: -1.2,
    is_anomaly: true,
    summarize_action: "แปลงอ้อยนี้มีปัญหาเรื่องการให้น้ำที่ไม่เพียงพอ ส่งผลให้ความหวานของอ้อยต่ำกว่าค่าเฉลี่ย ควรปรับปรุงระบบการให้น้ำและเพิ่มปริมาณน้ำให้เพียงพอต่อความต้องการของอ้อย แปลงนี้ควรได้รับการดูแลเป็นพิเศษในการรดน้ำและการจัดการดิน"
  },
  {
    farm_id: "F002",
    farm_name: "แปลงอ้อยบางกะปิ",
    latitude: 13.7650,
    longitude: 100.6477,
    css_difference: 0.8,
    is_anomaly: false,
    summarize_action: "แปลงอ้อยนี้อยู่ในสภาพที่ดี ปริมาณน้ำและการจัดการแปลงอยู่ในระดับมาตรฐาน สามารถเพิ่มผลผลิตได้โดยการปรับปรุงพันธุ์อ้อยและการใช้ปุ๋ยอย่างเหมาะสม แปลงนี้เป็นตัวอย่างที่ดีในการจัดการแปลงอ้อย"
  },
  {
    farm_id: "F003",
    farm_name: "แปลงอ้อยลาดกระบัง",
    latitude: 13.7279,
    longitude: 100.7483,
    css_difference: -0.5,
    is_anomaly: false,
    summarize_action: "แปลงอ้อยนี้มีปัญหาเรื่องวัชพืชที่ขึ้นรก ส่งผลให้การเจริญเติบโตของอ้อยไม่เต็มที่ ควรเพิ่มความถี่ในการตัดแต่งและกำจัดวัชพืช แปลงนี้ต้องการการดูแลในการจัดการวัชพืชมากขึ้น"
  },
  {
    farm_id: "F004",
    farm_name: "แปลงอ้อยพระโขนง",
    latitude: 13.6930,
    longitude: 100.6004,
    css_difference: 1.5,
    is_anomaly: true,
    summarize_action: "แปลงอ้อยนี้มีผลผลิตสูงกว่าค่าเฉลี่ยอย่างมาก ควรศึกษาปัจจัยที่ทำให้แปลงนี้ประสบความสำเร็จเพื่อนำไปปรับใช้กับแปลงอื่น แปลงนี้เป็นแบบอย่างที่ดีในการจัดการแปลงอ้อยที่มีประสิทธิภาพสูง"
  },
  {
    farm_id: "F005",
    farm_name: "แปลงอ้อยบางนา",
    latitude: 13.6804,
    longitude: 100.6065,
    css_difference: 0.2,
    is_anomaly: false,
    summarize_action: "แปลงอ้อยนี้อยู่ในสภาพปกติ ปริมาณน้ำและการจัดการอยู่ในระดับที่ดี ควรคงรูปแบบการจัดการปัจจุบันไว้ แปลงนี้แสดงให้เห็นถึงการจัดการที่สมดุลและมีประสิทธิภาพ"
  },
  {
    farm_id: "F006",
    farm_name: "แปลงอ้อยสวนหลวง",
    latitude: 13.7200,
    longitude: 100.5200,
    css_difference: -0.8,
    is_anomaly: true,
    summarize_action: "แปลงอ้อยนี้มีปัญหาเรื่องโรคและแมลง ส่งผลให้ผลผลิตต่ำกว่าค่าเฉลี่ย ควรเพิ่มการตรวจสอบและการใช้สารป้องกันอย่างเหมาะสม แปลงนี้ต้องการการดูแลด้านการป้องกันโรคและแมลงเป็นพิเศษ"
  },
  {
    farm_id: "F007",
    farm_name: "แปลงอ้อยบางเขน",
    latitude: 13.8500,
    longitude: 100.4000,
    css_difference: 0.3,
    is_anomaly: false,
    summarize_action: "แปลงอ้อยนี้อยู่ในสภาพที่ดีโดยรวม การจัดการแปลงและการดูแลอยู่ในระดับมาตรฐาน ควรคงรูปแบบการจัดการปัจจุบันและติดตามผลอย่างต่อเนื่อง"
  },
  {
    farm_id: "F008",
    farm_name: "แปลงอ้อยดอนเมือง",
    latitude: 13.9200,
    longitude: 100.6000,
    css_difference: -1.8,
    is_anomaly: true,
    summarize_action: "แปลงอ้อยนี้มีปัญหาหลายประการรวมถึงการให้น้ำและการจัดการดิน ควรได้รับการปรับปรุงอย่างเร่งด่วน แปลงนี้ต้องการการดูแลและปรับปรุงอย่างครอบคลุม"
  }
]

// Function to fetch farm data (replace with actual API call)
export const fetchFarmData = async (): Promise<FarmData[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))

  // In production, replace with actual API call:
  // const response = await fetch('/api/farms')
  // return response.json()

  return sampleFarmData
}

// Thailand map bounds and center
export const THAILAND_CONFIG = {
  center: [13.7563, 100.5018] as [number, number],
  bounds: [
    [5.6128, 97.3434], // Southwest
    [20.4648, 105.6369] // Northeast
  ] as [[number, number], [number, number]],
  defaultZoom: 7
}