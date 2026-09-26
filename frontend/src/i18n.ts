export type SupportedLanguage = 'en-IN' | 'mr-IN' | 'hi-IN';

export interface Translations {
  appName: string;
  tagline: string;
  dashboard: string;
  meters: string;
  readings: string;
  alerts: string;
  incidentEvidence: string;
  verification: string;
  scenarioLab: string;
  evaluation: string;
  waterImpact: string;
  settings: string;
  activeAlerts: string;
  criticalAlerts: string;
  totalMeters: string;
  recentConsumption: string;
  baselineExpected: string;
  maxRiskScore: string;
  overallSeverity: string;
  insufficientHistory: string;
  insufficientHistoryDesc: string;
  nextAction: string;
  evidenceHierarchyTitle: string;
  currentReading: string;
  expectedBaseline: string;
  deviation: string;
  persistence: string;
  trend: string;
  estimatedExcess: string;
  riskScore: string;
  severity: string;
  verificationRequired: string;
  acknowledge: string;
  beginVerification: string;
  confirmAbnormal: string;
  markFalseAlarm: string;
  investigate: string;
  resolveIncident: string;
  generateExplanation: string;
  aiExplanationTitle: string;
  sourceGroq: string;
  sourceDeterministic: string;
  switchRole: string;
  filterBySeverity: string;
  allSeverities: string;
  allStatuses: string;
  uploadCsv: string;
  addReading: string;
  createMeter: string;
  refresh: string;
}

export const translations: Record<SupportedLanguage, Translations> = {
  'en-IN': {
    appName: 'JalRakshak AI',
    tagline: 'Analytics detects. Evidence supports. AI explains. Humans verify.',
    dashboard: 'Dashboard',
    meters: 'Meters',
    readings: 'Readings / Import',
    alerts: 'Alerts',
    incidentEvidence: 'Incident / Evidence',
    verification: 'Verification',
    scenarioLab: 'Scenario Lab',
    evaluation: 'Evaluation',
    waterImpact: 'Water Impact',
    settings: 'Settings',
    activeAlerts: 'Active Alerts',
    criticalAlerts: 'Critical Alerts',
    totalMeters: 'Authorized Meters',
    recentConsumption: 'Latest Consumption',
    baselineExpected: 'Expected Baseline',
    maxRiskScore: 'Max Risk Score',
    overallSeverity: 'Overall Severity',
    insufficientHistory: 'Insufficient History',
    insufficientHistoryDesc: 'Not enough historical readings to establish a reliable baseline. Add more readings to enable baseline-based anomaly analysis.',
    nextAction: 'Next Verification Action',
    evidenceHierarchyTitle: 'Deterministic Evidence Hierarchy',
    currentReading: 'Current Reading',
    expectedBaseline: 'Expected Baseline',
    deviation: 'Deviation Percentage',
    persistence: 'Persistence Intervals',
    trend: 'Consumption Trend',
    estimatedExcess: 'Estimated Excess Consumption',
    riskScore: 'Risk Score',
    severity: 'Severity',
    verificationRequired: 'Physical Verification Required',
    acknowledge: 'Acknowledge Alert',
    beginVerification: 'Begin Verification',
    confirmAbnormal: 'Confirm Abnormal Event',
    markFalseAlarm: 'Mark as False Alarm',
    investigate: 'Mark as Investigating',
    resolveIncident: 'Resolve Incident',
    generateExplanation: 'Request Explanation',
    aiExplanationTitle: 'Explanation Card',
    sourceGroq: 'Source: Groq AI',
    sourceDeterministic: 'Source: Deterministic Fallback',
    switchRole: 'Simulate User Role',
    filterBySeverity: 'Filter by Severity',
    allSeverities: 'All Severities',
    allStatuses: 'All Statuses',
    uploadCsv: 'Upload CSV Readings',
    addReading: 'Add Manual Reading',
    createMeter: 'Register New Meter',
    refresh: 'Refresh Data',
  },
  'mr-IN': {
    appName: 'जल रक्षक AI',
    tagline: 'विश्लेषण शोधते. पुरावा समर्थन करतो. AI स्पष्टीकरण देते. मानव पडताळतो.',
    dashboard: 'डॅशबोर्ड',
    meters: 'मीटर्स',
    readings: 'वाचन / आयात',
    alerts: 'सतर्कता (Alerts)',
    incidentEvidence: 'घटना / पुरावा',
    verification: 'पडताळणी (Verification)',
    scenarioLab: 'परिदृश्य प्रयोगशाळा (Scenario Lab)',
    evaluation: 'मूल्यांकन (Evaluation)',
    waterImpact: 'जल प्रभाव (Water Impact)',
    settings: 'सेटिंग्ज',
    activeAlerts: 'सक्रिय सतर्कता',
    criticalAlerts: 'गंभीर सतर्कता',
    totalMeters: 'अधिकृत मीटर्स',
    recentConsumption: 'अलिकडील वापर',
    baselineExpected: 'अपेक्षित आधारभूत वापर',
    maxRiskScore: 'कमाल जोखीम स्कोअर',
    overallSeverity: 'एकूण तीव्रता',
    insufficientHistory: 'अपुरा इतिहास',
    insufficientHistoryDesc: 'विश्वसनीय आधारभूत वापर स्थापित करण्यासाठी पुरेसा ऐतिहासिक डेटा उपलब्ध नाही. विश्लेषणासाठी अधिक नोंदी जोडा.',
    nextAction: 'पुढील पडताळणी कृती',
    evidenceHierarchyTitle: 'वस्तुनिष्ठ पुरावा क्रमवारी',
    currentReading: 'सध्याचा वापर',
    expectedBaseline: 'अपेक्षित आधारभूत वापर',
    deviation: 'विचलन टक्केवारी',
    persistence: 'सातत्य कालावधी',
    trend: 'वापराचा कल',
    estimatedExcess: 'अंदाजे संभाव्य अतिरिक्त वापर',
    riskScore: 'जोखीम स्कोअर',
    severity: 'तीव्रता',
    verificationRequired: 'भौतिक पडताळणी आवश्यक',
    acknowledge: 'सतर्कतेची दखल घ्या',
    beginVerification: 'पडताळणी सुरू करा',
    confirmAbnormal: 'असामान्य वापराची पुष्टी करा',
    markFalseAlarm: 'खोटा गजर (False Alarm)',
    investigate: 'तपास सुरू करा',
    resolveIncident: 'घटना निकाली काढा',
    generateExplanation: 'स्पष्टीकरण मिळवा',
    aiExplanationTitle: 'स्पष्टीकरण कार्ड',
    sourceGroq: 'स्रोत: ग्रॉक AI (Groq)',
    sourceDeterministic: 'स्रोत: वस्तुनिष्ठ फॉलबॅक (Deterministic)',
    switchRole: 'वापरकर्ता भूमिका निवडा',
    filterBySeverity: 'तीव्रतेनुसार फिल्टर',
    allSeverities: 'सर्व तीव्रता',
    allStatuses: 'सर्व स्थिती',
    uploadCsv: 'CSV वाचन अपलोड करा',
    addReading: 'नोंद नोंदवा',
    createMeter: 'नवीन मीटर जोडा',
    refresh: 'ताजे करा',
  },
  'hi-IN': {
    appName: 'जल रक्षक AI',
    tagline: 'एनालिटिक्स पहचानता है। साक्ष्य समर्थन करता है। AI समझाता है। मानव सत्यापित करता है।',
    dashboard: 'डैशबोर्ड',
    meters: 'मीटर',
    readings: 'रीडिंग / आयात',
    alerts: 'अलर्ट (Alerts)',
    incidentEvidence: 'घटना / साक्ष्य',
    verification: 'सत्यापन (Verification)',
    scenarioLab: 'सिनेरियो लैब',
    evaluation: 'मूल्यांकन',
    waterImpact: 'जल प्रभाव',
    settings: 'सेटिंग्स',
    activeAlerts: 'सक्रिय अलर्ट',
    criticalAlerts: 'गंभीर अलर्ट',
    totalMeters: 'अधिकृत मीटर',
    recentConsumption: 'नवीनतम खपत',
    baselineExpected: 'अपेक्षित बेसलाइन',
    maxRiskScore: 'अधिकतम जोखिम स्कोर',
    overallSeverity: 'समग्र गंभीरता',
    insufficientHistory: 'अपर्याप्त इतिहास',
    insufficientHistoryDesc: 'विश्वसनीय बेसलाइन स्थापित करने के लिए पर्याप्त ऐतिहासिक डेटा उपलब्ध नहीं है। विश्लेषण के लिए अधिक रीडिंग जोड़ें।',
    nextAction: 'अगला सत्यापन कदम',
    evidenceHierarchyTitle: 'विश्लेषणात्मक साक्ष्य पदानुक्रम',
    currentReading: 'वर्तमान रीडिंग',
    expectedBaseline: 'अपेक्षित बेसलाइन',
    deviation: 'विचलन प्रतिशत',
    persistence: 'निरंतरता अंतराल',
    trend: 'खपत का रुझान',
    estimatedExcess: 'अनुमानित अतिरिक्त खपत',
    riskScore: 'जोखिम स्कोर',
    severity: 'गंभीरता',
    verificationRequired: 'भौतिक सत्यापन आवश्यक',
    acknowledge: 'अलर्ट स्वीकार करें',
    beginVerification: 'सत्यापन शुरू करें',
    confirmAbnormal: 'असामान्य घटना की पुष्टि करें',
    markFalseAlarm: 'गलत अलार्म चिह्नित करें',
    investigate: 'जांच जारी रखें',
    resolveIncident: 'घटना का समाधान करें',
    generateExplanation: 'स्पष्टीकरण प्राप्त करें',
    aiExplanationTitle: 'स्पष्टीकरण कार्ड',
    sourceGroq: 'स्रोत: ग्रॉक AI (Groq)',
    sourceDeterministic: 'स्रोत: नियतात्मक फॉलबैक',
    switchRole: 'उपयोगकर्ता भूमिका बदलें',
    filterBySeverity: 'गंभीरता अनुसार फ़िल्टर',
    allSeverities: 'सभी गंभीरता',
    allStatuses: 'सभी स्थितियां',
    uploadCsv: 'CSV फ़ाइल अपलोड करें',
    addReading: 'मैनुअल रीडिंग जोड़ें',
    createMeter: 'नया मीटर पंजीकृत करें',
    refresh: 'डेटा रीफ़्रेश करें',
  },
};
