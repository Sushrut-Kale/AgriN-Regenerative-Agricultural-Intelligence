/**
 * AgriN Pre-Configured Demo Scenarios (Phase 19)
 * 
 * STRICT NON-FABRICATION RULE:
 * Clearly labeled synthetic/example farms demonstrating distinct agricultural system behaviors.
 * DEMO DATA — NOT REAL FARM DATA
 */

export const DEMO_SCENARIOS = [
  {
    id: 'scenario-1-punjab',
    title: 'Scenario 1: Irrigated Northern Region (Punjab)',
    badge: 'Irrigated Intensive',
    description: 'High-input alluvial plains with tube-well irrigation, intensive cereal cropping, and balanced fertility.',
    notice: 'DEMO DATA — NOT REAL FARM DATA',
    farmData: {
      farm_id: 'DEMO-PUNJAB-01',
      country: 'India',
      state: 'Punjab',
      district: 'Ludhiana',
      sub_district: 'Ludhiana East',
      village: 'Demo Village North',
      latitude: 30.9010,
      longitude: 75.8573,
      season: 'rabi',
      farm_area: '4.5',
      soil_type: 'alluvial',
      irrigation_available: 'yes',
      water_source: 'borewell',
      drainage: 'good',
      previous_crop: 'rice'
    },
    soilData: {
      N: '240', P: '42', K: '280', S: '18',
      Zn: '1.2', Fe: '6.5', Cu: '0.8', Mn: '4.2', B: '0.7',
      ph: '7.4', EC: '0.45', OC: '0.55'
    },
    envData: {
      temperature: '19.5', humidity: '62', rainfall: '45'
    }
  },
  {
    id: 'scenario-2-rajasthan',
    title: 'Scenario 2: Semi-Arid Region (Rajasthan)',
    badge: 'Semi-Arid Dryland',
    description: 'Coarse sandy soils with moisture stress, elevated electrical conductivity (salinity), and low organic carbon.',
    notice: 'DEMO DATA — NOT REAL FARM DATA',
    farmData: {
      farm_id: 'DEMO-RAJASTHAN-02',
      country: 'India',
      state: 'Rajasthan',
      district: 'Jodhpur',
      sub_district: 'Luni',
      village: 'Demo Thar Hamlet',
      latitude: 26.2389,
      longitude: 73.0243,
      season: 'kharif',
      farm_area: '6.0',
      soil_type: 'sandy',
      irrigation_available: 'no',
      water_source: 'none',
      drainage: 'excessive',
      previous_crop: 'fallow'
    },
    soilData: {
      N: '95', P: '14', K: '160', S: '8',
      Zn: '0.4', Fe: '3.1', Cu: '0.3', Mn: '2.0', B: '0.3',
      ph: '8.4', EC: '2.4', OC: '0.22'
    },
    envData: {
      temperature: '36.8', humidity: '34', rainfall: '18'
    }
  },
  {
    id: 'scenario-3-kerala',
    title: 'Scenario 3: High-Rainfall Region (Kerala)',
    badge: 'High-Rainfall Acidic',
    description: 'High-precipitation Western Ghats foothills with acidic laterite soil, high organic carbon, and plantation ecology.',
    notice: 'DEMO DATA — NOT REAL FARM DATA',
    farmData: {
      farm_id: 'DEMO-KERALA-03',
      country: 'India',
      state: 'Kerala',
      district: 'Wayanad',
      sub_district: 'Vythiri',
      village: 'Demo Plantation Zone',
      latitude: 11.6854,
      longitude: 76.1320,
      season: 'kharif',
      farm_area: '2.0',
      soil_type: 'laterite',
      irrigation_available: 'yes',
      water_source: 'canal',
      drainage: 'moderate',
      previous_crop: 'pepper'
    },
    soilData: {
      N: '180', P: '22', K: '190', S: '14',
      Zn: '0.9', Fe: '12.4', Cu: '1.2', Mn: '7.8', B: '0.5',
      ph: '5.1', EC: '0.28', OC: '1.45'
    },
    envData: {
      temperature: '24.2', humidity: '88', rainfall: '310'
    }
  },
  {
    id: 'scenario-4-maharashtra',
    title: 'Scenario 4: Black-Soil Deccan Region (Maharashtra)',
    badge: 'Deccan Vertisol',
    description: 'Deep clayey Vertisols with high moisture retention, neutral-to-alkaline pH, and rainfed cotton-soybean system.',
    notice: 'DEMO DATA — NOT REAL FARM DATA',
    farmData: {
      farm_id: 'DEMO-MAHARASHTRA-04',
      country: 'India',
      state: 'Maharashtra',
      district: 'Parbhani',
      sub_district: 'Gangakhed',
      village: 'Demo Godavari Belt',
      latitude: 19.2610,
      longitude: 76.7767,
      season: 'kharif',
      farm_area: '3.2',
      soil_type: 'black',
      irrigation_available: 'no',
      water_source: 'borewell',
      drainage: 'poor',
      previous_crop: 'soybean'
    },
    soilData: {
      N: '135', P: '28', K: '240', S: '11',
      Zn: '0.6', Fe: '4.8', Cu: '0.5', Mn: '5.1', B: '0.4',
      ph: '7.9', EC: '0.62', OC: '0.46'
    },
    envData: {
      temperature: '31.0', humidity: '64', rainfall: '110'
    }
  },
  {
    id: 'scenario-5-incomplete',
    title: 'Scenario 5: Incomplete-Data Farm',
    badge: 'Degraded / Missing Data',
    description: 'Demonstrates graceful degradation: only geographic location is specified; zero lab soil metrics provided.',
    notice: 'DEMO DATA — NOT REAL FARM DATA',
    farmData: {
      farm_id: 'DEMO-INCOMPLETE-05',
      country: 'India',
      state: 'Bihar',
      district: 'Gaya',
      sub_district: 'Bodh Gaya',
      village: '',
      latitude: null,
      longitude: null,
      season: 'kharif',
      farm_area: '1.5',
      soil_type: '',
      irrigation_available: 'unknown',
      water_source: '',
      drainage: 'unknown',
      previous_crop: ''
    },
    soilData: {
      N: '', P: '', K: '', S: '',
      Zn: '', Fe: '', Cu: '', Mn: '', B: '',
      ph: '', EC: '', OC: ''
    },
    envData: {
      temperature: '', humidity: '', rainfall: ''
    }
  }
];
