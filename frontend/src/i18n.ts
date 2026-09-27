export type SupportedLanguage = 'en-IN' | 'mr-IN' | 'hi-IN';

export interface Translations {
  // Brand & Navigation
  appName: string;
  tagline: string;
  waterAnomalyDecisionSupport: string;
  corePrincipleTitle: string;
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
  openMenu: string;
  closeMenu: string;
  logout: string;
  environment: string;
  apiConnected: string;

  // Common Actions & States
  loading: string;
  error: string;
  success: string;
  cancel: string;
  submit: string;
  save: string;
  close: string;
  closeModal: string;
  search: string;
  filter: string;
  refresh: string;
  actions: string;
  noData: string;
  retry: string;
  clearFilters: string;
  viewDetails: string;
  status: string;

  // Safety & Anomaly Terminology
  suspectedAnomaly: string;
  possibleLeak: string;
  estimatedExcessConsumption: string;
  physicalVerificationRequired: string;
  routineObservation: string;
  safetyDisclaimer: string;

  // Severity & Status
  severity: string;
  riskScore: string;
  severityCritical: string;
  severityHigh: string;
  severityMedium: string;
  severityLow: string;
  statusOpen: string;
  statusAcknowledged: string;
  statusVerifying: string;
  statusConfirmed: string;
  statusFalseAlarm: string;
  statusInvestigating: string;
  statusResolved: string;

  // Dashboard View
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
  loadingAnalytics: string;
  recentAlertsTitle: string;
  viewAllAlerts: string;
  noActiveAlertsTitle: string;
  noActiveAlertsDesc: string;
  systemOverviewTitle: string;

  // Evidence & Metrics Cards
  evidenceHierarchyTitle: string;
  currentReading: string;
  expectedBaseline: string;
  deviation: string;
  persistence: string;
  trend: string;
  estimatedExcess: string;
  verificationRequired: string;
  deterministicBreakdownTitle: string;
  deviationScoreLabel: string;
  persistenceScoreLabel: string;
  trendScoreLabel: string;
  lossScoreLabel: string;
  humanVerificationStatus: string;
  noEvidenceRecorded: string;
  consecutiveIntervals: string;
  litersUnit: string;

  // Alert Modal & Lifecycle Actions
  incidentDetails: string;
  meterIdLabel: string;
  statusLabel: string;
  aiExplanationTitle: string;
  generateExplanation: string;
  sourceGroq: string;
  sourceDeterministic: string;
  languageLabel: string;
  clickToGenerateExplanation: string;
  physicalVerificationGuidanceTitle: string;
  verificationStep1: string;
  verificationStep2: string;
  verificationStep3: string;
  verificationStep4: string;
  authorizedLifecycleActions: string;
  auditNotePlaceholder: string;
  acknowledge: string;
  beginVerification: string;
  confirmAbnormal: string;
  markFalseAlarm: string;
  investigate: string;
  resolveIncident: string;
  incidentResolvedMessage: string;

  // Filter & Search Controls
  filterBySeverity: string;
  allSeverities: string;
  filterByStatus: string;
  allStatuses: string;
  filterByCategory: string;
  allCategories: string;

  // Meters View
  registerNewMeter: string;
  meterId: string;
  meterName: string;
  zone: string;
  category: string;
  initialReading: string;
  registerButton: string;
  activeMetersList: string;
  searchMetersPlaceholder: string;
  loadingMeters: string;
  noMetersFound: string;
  residential: string;
  commercial: string;
  industrial: string;
  agricultural: string;

  // Readings & Import View
  readingsTitle: string;
  readingsSubtitle: string;
  selectMeterPrompt: string;
  uploadCsvTitle: string;
  uploadCsvDesc: string;
  selectCsvFile: string;
  uploadCsvButton: string;
  uploading: string;
  manualReadingTitle: string;
  readingValueLiters: string;
  readingTimestamp: string;
  submitReading: string;
  recentTelemetry: string;
  loadingReadings: string;
  noReadingsFound: string;
  sourceManual: string;
  sourceCsv: string;

  // Verification View
  verificationViewTitle: string;
  verificationViewSubtitle: string;
  pendingVerifications: string;
  noPendingVerifications: string;

  // Scenario Lab View
  scenarioLabTitle: string;
  scenarioLabSubtitle: string;
  selectScenarioPrompt: string;
  runScenarioButton: string;
  runningScenario: string;
  scenarioDescriptionTitle: string;
  simulatedReadingsTitle: string;
  analyticsOutcomeTitle: string;

  // Evaluation View
  evaluationTitle: string;
  evaluationSubtitle: string;
  runEvaluationButton: string;
  runningEvaluation: string;
  evaluationSummaryTitle: string;
  metricPrecision: string;
  metricRecall: string;
  metricF1: string;
  metricFAR: string;
  metricMAE: string;
  metricLatency: string;
  metricGroqSuccess: string;
  metricFallbackCoverage: string;
  metricWorkflowCompletion: string;
  scenariosEvaluated: string;

  // Water Impact View
  waterImpactTitle: string;
  waterImpactSubtitle: string;
  totalEstimatedExcessLoss: string;
  totalPotentialCost: string;
  affectedMetersCount: string;
  waterSavingsMessage: string;
  impactTableTitle: string;
  meterColumn: string;
  zoneColumn: string;
  lossColumn: string;
  estimatedCostColumn: string;

  // Settings View
  settingsTitle: string;
  settingsSubtitle: string;
  languageSettingsTitle: string;
  interfaceLanguageDesc: string;
  authSectionTitle: string;
  userEmail: string;
  userRole: string;
  organization: string;
  tokenStatus: string;
  tokenActive: string;
  systemArchitectureTitle: string;
  backendVersion: string;
  groqModel: string;

  // Additional Audited UI Copy
  alertsSubtitle: string;
  detectedAt: string;
  inspectAndAction: string;
  readingsLogTitle: string;
  requiredCsvFormat: string;
  uploadAndProcessCsv: string;
  evidenceSubtitle: string;
  evidencePrincipleTitle: string;
  evidencePrincipleDesc: string;
  executionParameters: string;
  randomSeedLabel: string;
  deterministicSeedNote: string;
  simulationRunResult: string;
  operationalLatency: string;
  confusionMatrixTitle: string;
  scientificReportingTitle: string;
  scientificReportingDesc: string;
  groundTruthValidationMatrix: string;
  scenarioCol: string;
  expectedGroundTruthCol: string;
  actualAnalyticsOutcomeCol: string;
  resultCol: string;
  groundTruthLabel: string;
  impactAssumptionTitle: string;
  avoidedFractionLabel: string;
  scopeFilterLabel: string;
  scopeAllOption: string;
  scopeFilterHelp: string;
  projectedAvoidedWaterLoss: string;
  equivalencyPerspective: string;
  standard20LCans: string;
  dailyAllowances: string;
  systemConfigSubtitle: string;
  applyToken: string;
  tokenApplied: string;
  aiGuardrailsTitle: string;
}

export const translations: Record<SupportedLanguage, Translations> = {
  'en-IN': {
    appName: 'JalRakshak AI',
    tagline: 'Analytics detects. Evidence supports. AI explains. Humans verify.',
    waterAnomalyDecisionSupport: 'Water Anomaly Decision Support',
    corePrincipleTitle: 'Core Principle:',
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
    openMenu: 'Open navigation menu',
    closeMenu: 'Close navigation menu',
    logout: 'Logout',
    environment: 'Environment:',
    apiConnected: 'Backend API Connected',

    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    submit: 'Submit',
    save: 'Save',
    close: 'Close',
    closeModal: 'Close modal dialog',
    search: 'Search',
    filter: 'Filter',
    refresh: 'Refresh Data',
    actions: 'Actions',
    noData: 'No data available',
    retry: 'Retry',
    clearFilters: 'Clear Filters',
    viewDetails: 'View Details',
    status: 'Status',

    suspectedAnomaly: 'Suspected Anomaly',
    possibleLeak: 'Possible Leak',
    estimatedExcessConsumption: 'Estimated Excess Consumption',
    physicalVerificationRequired: 'Physical Verification Required',
    routineObservation: 'Routine Observation',
    safetyDisclaimer: '* Analytical risk score indicates suspected anomaly / possible leak. Physical verification required.',

    severity: 'Severity',
    riskScore: 'Risk Score',
    severityCritical: 'CRITICAL',
    severityHigh: 'HIGH',
    severityMedium: 'MEDIUM',
    severityLow: 'LOW',
    statusOpen: 'DETECTED',
    statusAcknowledged: 'ACKNOWLEDGED',
    statusVerifying: 'VERIFYING',
    statusConfirmed: 'CONFIRMED',
    statusFalseAlarm: 'FALSE_ALARM',
    statusInvestigating: 'INVESTIGATING',
    statusResolved: 'RESOLVED',

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
    loadingAnalytics: 'Loading authoritative analytics...',
    recentAlertsTitle: 'Recent Suspected Anomalies & Alerts',
    viewAllAlerts: 'View All Alerts',
    noActiveAlertsTitle: 'No Active Alerts',
    noActiveAlertsDesc: 'All authorized meters are operating within normal baseline limits.',
    systemOverviewTitle: 'System Overview',

    evidenceHierarchyTitle: 'Deterministic Canonical Evidence Breakdown',
    currentReading: '1. Current Usage (Observed)',
    expectedBaseline: '2. Expected Baseline',
    deviation: '3. Deviation Percentage',
    persistence: '4. Persistence Intervals',
    trend: '5. Trend Direction',
    estimatedExcess: '6. Estimated Excess Consumption',
    verificationRequired: '7. Human Verification Status',
    deterministicBreakdownTitle: 'Deterministic Risk Component Breakdown (0–100):',
    deviationScoreLabel: 'Deviation Score',
    persistenceScoreLabel: 'Persistence Score',
    trendScoreLabel: 'Trend Score',
    lossScoreLabel: 'Estimated-Loss Score',
    humanVerificationStatus: 'Human Verification Status:',
    noEvidenceRecorded: 'No structured evidence recorded for this incident.',
    consecutiveIntervals: 'consecutive intervals',
    litersUnit: 'Liters',

    incidentDetails: 'Incident Details',
    meterIdLabel: 'Meter ID',
    statusLabel: 'Status',
    aiExplanationTitle: 'Explanation Card',
    generateExplanation: 'Request Explanation',
    sourceGroq: 'Source: Groq AI',
    sourceDeterministic: 'Source: Deterministic Fallback',
    languageLabel: 'Language:',
    clickToGenerateExplanation: 'Click "Request Explanation" to produce an evidence-grounded explanation.',
    physicalVerificationGuidanceTitle: 'On-Site Physical Verification Guidance',
    verificationStep1: 'Check all internal faucets, flush tanks, and garden hose bibs for continuous trickling.',
    verificationStep2: 'Perform a Zero-Consumption Check: ensure all taps are off and observe if the water meter spindle is moving.',
    verificationStep3: 'Inspect exposed supply lines and connection unions for moisture or damp spots.',
    verificationStep4: 'Confirm abnormal usage or report as a false alarm using the authorized workflow below.',
    authorizedLifecycleActions: 'Authorized Lifecycle Actions',
    auditNotePlaceholder: 'Optional workflow audit note...',
    acknowledge: 'Acknowledge Alert',
    beginVerification: 'Begin Verification',
    confirmAbnormal: 'Confirm Abnormal Event',
    markFalseAlarm: 'Mark as False Alarm',
    investigate: 'Mark as Investigating',
    resolveIncident: 'Resolve Incident',
    incidentResolvedMessage: 'Incident is Resolved and Closed.',

    filterBySeverity: 'Filter by Severity',
    allSeverities: 'All Severities',
    filterByStatus: 'Filter by Status',
    allStatuses: 'All Statuses',
    filterByCategory: 'Filter by Category',
    allCategories: 'All Categories',

    registerNewMeter: 'Register New Meter',
    meterId: 'Meter ID',
    meterName: 'Meter Name',
    zone: 'Zone / Location',
    category: 'Category',
    initialReading: 'Initial Reading (L)',
    registerButton: 'Register Meter',
    activeMetersList: 'Authorized Meters Directory',
    searchMetersPlaceholder: 'Search by meter ID, name, or zone...',
    loadingMeters: 'Loading meters...',
    noMetersFound: 'No meters found matching your search.',
    residential: 'Residential',
    commercial: 'Commercial',
    industrial: 'Industrial',
    agricultural: 'Agricultural',

    readingsTitle: 'Meter Readings & Telemetry Import',
    readingsSubtitle: 'Upload time-series CSV data or record manual meter readings.',
    selectMeterPrompt: 'Select a Meter',
    uploadCsvTitle: 'Upload CSV Readings',
    uploadCsvDesc: 'Import time-series telemetry in CSV format (meter_id, timestamp, consumption_liters).',
    selectCsvFile: 'Select CSV File',
    uploadCsvButton: 'Upload & Ingest CSV',
    uploading: 'Ingesting Telemetry...',
    manualReadingTitle: 'Record Manual Reading',
    readingValueLiters: 'Consumption (Liters)',
    readingTimestamp: 'Timestamp',
    submitReading: 'Save Reading',
    recentTelemetry: 'Recent Telemetry Log',
    loadingReadings: 'Loading telemetry readings...',
    noReadingsFound: 'No telemetry records found for this meter.',
    sourceManual: 'Manual',
    sourceCsv: 'CSV Ingestion',

    verificationViewTitle: 'Human-in-the-Loop Verification',
    verificationViewSubtitle: 'Review, physically verify, and validate suspected water anomalies.',
    pendingVerifications: 'Incidents Requiring Field Verification',
    noPendingVerifications: 'No incidents currently pending verification.',

    scenarioLabTitle: 'Municipal Scenario Lab',
    scenarioLabSubtitle: 'Run canonical benchmark scenarios to test analytics and decision support.',
    selectScenarioPrompt: 'Select Benchmark Scenario',
    runScenarioButton: 'Run Scenario Simulation',
    runningScenario: 'Executing Scenario...',
    scenarioDescriptionTitle: 'Scenario Profile & Characteristics',
    simulatedReadingsTitle: 'Simulated Meter Readings',
    analyticsOutcomeTitle: 'Deterministic Analytics Outcome',

    evaluationTitle: 'System Performance & Benchmark Evaluation',
    evaluationSubtitle: 'Empirical benchmark evaluation across canonical municipal scenarios.',
    runEvaluationButton: 'Run Full Benchmark Evaluation',
    runningEvaluation: 'Executing Benchmark Evaluation...',
    evaluationSummaryTitle: 'Measured Benchmark Performance',
    metricPrecision: 'Precision',
    metricRecall: 'Recall',
    metricF1: 'F1 Score',
    metricFAR: 'False Alert Rate',
    metricMAE: 'Mean Absolute Error (MAE)',
    metricLatency: 'Alert Latency',
    metricGroqSuccess: 'AI Structured Success',
    metricFallbackCoverage: 'Fallback Coverage',
    metricWorkflowCompletion: 'Workflow Completion',
    scenariosEvaluated: 'Canonical Scenarios Evaluated',

    waterImpactTitle: 'Water Conservation & Potential Savings Impact',
    waterImpactSubtitle: 'Authoritative data-driven estimates of excess loss and potential savings.',
    totalEstimatedExcessLoss: 'Total Estimated Excess Consumption',
    totalPotentialCost: 'Estimated Potential Financial Loss',
    affectedMetersCount: 'Meters with Suspected Anomalies',
    waterSavingsMessage: 'Physical verification and rapid intervention prevent avoidable municipal water losses.',
    impactTableTitle: 'Estimated Water Impact by Meter',
    meterColumn: 'Meter ID',
    zoneColumn: 'Zone / Location',
    lossColumn: 'Estimated Excess (L)',
    estimatedCostColumn: 'Estimated Cost (₹)',

    settingsTitle: 'System Settings & Security Profile',
    settingsSubtitle: 'Language preferences, session details, and architectural status.',
    languageSettingsTitle: 'Interface Language',
    interfaceLanguageDesc: 'Select your preferred working language (English, Marathi, or Hindi).',
    authSectionTitle: 'Authenticated User Session',
    userEmail: 'Email Address',
    userRole: 'Assigned Role',
    organization: 'Organization ID',
    tokenStatus: 'Session Token Status',
    tokenActive: 'Active (Cryptographically Signed JWT)',
    systemArchitectureTitle: 'Platform Architecture & Status',
    backendVersion: 'Backend API Version',
    groqModel: 'LLM Model (Groq)',

    alertsSubtitle: 'Anomaly alerts requiring human verification or lifecycle resolution',
    detectedAt: 'Detected At',
    inspectAndAction: 'Inspect & Action',
    readingsLogTitle: 'Recorded Time-Series Readings',
    requiredCsvFormat: 'Required CSV Format:',
    uploadAndProcessCsv: 'Upload & Process CSV',
    evidenceSubtitle: 'Structured deterministic evidence packets supporting anomaly decisions',
    evidencePrincipleTitle: 'Immutable Evidence First Principle',
    evidencePrincipleDesc: 'The evidence displayed here is derived directly from backend statistical algorithms (Median, MAD, Robust Z-Score, slope regression). It forms the sole factual basis prior to AI natural language summarization and human verification.',
    executionParameters: 'Execution Parameters',
    randomSeedLabel: 'Random Seed (Reproducibility)',
    deterministicSeedNote: 'Deterministic seed guarantees exact reproducible numbers.',
    simulationRunResult: 'Simulation Run Result',
    operationalLatency: 'Operational Latency',
    confusionMatrixTitle: 'Confusion Matrix & Alert Rate',
    scientificReportingTitle: 'Scientific Ground-Truth Reporting Standards',
    scientificReportingDesc: 'Metrics are reported only when verified against seeded scenarios or empirical runtime measurements. Features lacking longitudinal production telemetry are explicitly reported as Not yet measured.',
    groundTruthValidationMatrix: 'Ground Truth Validation Matrix',
    scenarioCol: 'Scenario',
    expectedGroundTruthCol: 'Expected Ground Truth',
    actualAnalyticsOutcomeCol: 'Actual Analytics Outcome',
    resultCol: 'Benchmark Result',
    groundTruthLabel: 'Ground Truth:',
    impactAssumptionTitle: 'Impact Assumption Parameters',
    avoidedFractionLabel: 'Avoided Fraction Assumption:',
    scopeFilterLabel: 'Scope Filter:',
    scopeAllOption: 'All Authorized Active Anomalies (Aggregate)',
    scopeFilterHelp: 'Filter potential savings calculation to a specific active meter or view aggregate authorized meters.',
    projectedAvoidedWaterLoss: 'Projected Avoided Water Loss',
    equivalencyPerspective: 'Equivalency Perspective:',
    standard20LCans: 'standard 20L water cans saved.',
    dailyAllowances: 'daily drinking/sanitation allowances (at 150L/day/person).',
    systemConfigSubtitle: 'System configurations, security credentials, and AI parameters',
    applyToken: 'Apply Token',
    tokenApplied: 'Token applied',
    aiGuardrailsTitle: 'Enforced AI Guardrails:',
  },
  'mr-IN': {
    appName: 'जल रक्षक AI',
    tagline: 'विश्लेषण शोधते. पुरावा समर्थन करतो. AI स्पष्टीकरण देते. मानव पडताळतो.',
    waterAnomalyDecisionSupport: 'पाणी विसंगती निर्णय समर्थन',
    corePrincipleTitle: 'मार्गदर्शक तत्त्व:',
    dashboard: 'डॅशबोर्ड',
    meters: 'मीटर्स',
    readings: 'वाचन / आयात',
    alerts: 'सतर्कता (Alerts)',
    incidentEvidence: 'घटना / पुरावा',
    verification: 'पडताळणी (Verification)',
    scenarioLab: 'परिदृश्य प्रयोगशाळा',
    evaluation: 'मूल्यांकन',
    waterImpact: 'जल प्रभाव',
    settings: 'सेटिंग्ज',
    openMenu: 'नेव्हिगेशन मेनू उघडा',
    closeMenu: 'नेव्हिगेशन मेनू बंद करा',
    logout: 'बाहेर पडा (Logout)',
    environment: 'पर्यावरण:',
    apiConnected: 'बॅकएंड API जोडले आहे',

    loading: 'लोड होत आहे...',
    error: 'त्रुटी',
    success: 'यशस्वी',
    cancel: 'रद्द करा',
    submit: 'सादर करा',
    save: 'जतन करा',
    close: 'बंद करा',
    closeModal: 'डायलॉग बंद करा',
    search: 'शोधा',
    filter: 'फिल्टर',
    refresh: 'ताजे करा',
    actions: 'कृती',
    noData: 'कोणताही डेटा उपलब्ध नाही',
    retry: 'पुन्हा प्रयत्न करा',
    clearFilters: 'फिल्टर्स हटवा',
    viewDetails: 'तपशील पहा',
    status: 'स्थिती',

    suspectedAnomaly: 'संशयित विसंगती',
    possibleLeak: 'संभाव्य गळती',
    estimatedExcessConsumption: 'अंदाजे संभाव्य अतिरिक्त वापर',
    physicalVerificationRequired: 'भौतिक पडताळणी आवश्यक',
    routineObservation: 'नियमित निरीक्षण',
    safetyDisclaimer: '* विश्लेषणात्मक जोखीम स्कोअर संशयित विसंगती / संभाव्य गळती दर्शवतो. भौतिक पडताळणी आवश्यक आहे.',

    severity: 'तीव्रता',
    riskScore: 'जोखीम स्कोअर',
    severityCritical: 'CRITICAL',
    severityHigh: 'HIGH',
    severityMedium: 'MEDIUM',
    severityLow: 'LOW',
    statusOpen: 'DETECTED',
    statusAcknowledged: 'ACKNOWLEDGED',
    statusVerifying: 'VERIFYING',
    statusConfirmed: 'CONFIRMED',
    statusFalseAlarm: 'FALSE_ALARM',
    statusInvestigating: 'INVESTIGATING',
    statusResolved: 'RESOLVED',

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
    loadingAnalytics: 'अधिकृत विश्लेषणात्मक डेटा लोड होत आहे...',
    recentAlertsTitle: 'अलिकडील संशयित विसंगती आणि सतर्कता',
    viewAllAlerts: 'सर्व सतर्कता पहा',
    noActiveAlertsTitle: 'कोणतीही सक्रिय सतर्कता नाही',
    noActiveAlertsDesc: 'सर्व अधिकृत मीटर सामान्य मर्यादेत कार्य करत आहेत.',
    systemOverviewTitle: 'प्रणाली विहंगावलोकन',

    evidenceHierarchyTitle: 'वस्तुनिष्ठ पुरावा क्रमवारी',
    currentReading: '1. सध्याचा वापर (निरीक्षित)',
    expectedBaseline: '2. अपेक्षित आधारभूत वापर',
    deviation: '3. विचलन टक्केवारी',
    persistence: '4. सातत्य कालावधी',
    trend: '5. वापराचा कल',
    estimatedExcess: '6. अंदाजे संभाव्य अतिरिक्त वापर',
    verificationRequired: '7. मानवी पडताळणी स्थिती',
    deterministicBreakdownTitle: 'वस्तुनिष्ठ जोखीम घटक विभाजन (0–100):',
    deviationScoreLabel: 'विचलन स्कोअर',
    persistenceScoreLabel: 'सातत्य स्कोअर',
    trendScoreLabel: 'कल स्कोअर',
    lossScoreLabel: 'अंदाजे नुकसान स्कोअर',
    humanVerificationStatus: 'मानवी पडताळणी स्थिती:',
    noEvidenceRecorded: 'या घटनेसाठी कोणताही संरचित पुरावा नोंदवलेला नाही.',
    consecutiveIntervals: 'सलग अंतराल',
    litersUnit: 'लिटर',

    incidentDetails: 'घटना तपशील',
    meterIdLabel: 'मीटर आयडी',
    statusLabel: 'स्थिती',
    aiExplanationTitle: 'AI स्पष्टीकरण कार्ड',
    generateExplanation: 'स्पष्टीकरण मिळवा',
    sourceGroq: 'स्रोत: ग्रॉक AI (Groq)',
    sourceDeterministic: 'स्रोत: वस्तुनिष्ठ फॉलबॅक (Deterministic)',
    languageLabel: 'भाषा:',
    clickToGenerateExplanation: 'पुरावा-आधारित स्पष्टीकरण मिळवण्यासाठी बटणावर क्लिक करा.',
    physicalVerificationGuidanceTitle: 'जागेवरील भौतिक पडताळणी मार्गदर्शक',
    verificationStep1: 'सर्व अंतर्गत नळ, फ्लश टँक आणि बागेचे पाईप्स तपासा.',
    verificationStep2: 'शून्य-वापर चाचणी: सर्व नळ बंद असताना मीटर फिरत आहे का ते तपासा.',
    verificationStep3: 'उघड्या पाईप्स आणि जोडणींवर ओलावा किंवा गळती तपासा.',
    verificationStep4: 'असामान्य वापराची पुष्टी करा किंवा खोटा गजर म्हणून नोंदवा.',
    authorizedLifecycleActions: 'अधिकृत जीवनचक्र कृती',
    auditNotePlaceholder: 'ऐच्छिक ऑडिट नोंद...',
    acknowledge: 'सतर्कतेची दखल घ्या',
    beginVerification: 'पडताळणी सुरू करा',
    confirmAbnormal: 'असामान्य वापराची पुष्टी करा',
    markFalseAlarm: 'खोटा गजर म्हणून नोंदवा',
    investigate: 'तपास सुरू करा',
    resolveIncident: 'घटना निकाली काढा',
    incidentResolvedMessage: 'घटना निकाली काढली असून बंद करण्यात आली आहे.',

    filterBySeverity: 'तीव्रतेनुसार फिल्टर',
    allSeverities: 'सर्व तीव्रता',
    filterByStatus: 'स्थितीनुसार फिल्टर',
    allStatuses: 'सर्व स्थिती',
    filterByCategory: 'वर्गवारीनुसार फिल्टर',
    allCategories: 'सर्व वर्ग',

    registerNewMeter: 'नवीन मीटर जोडा',
    meterId: 'मीटर आयडी',
    meterName: 'मीटरचे नाव',
    zone: 'विभाग (Zone)',
    category: 'वर्गवारी',
    initialReading: 'प्रारंभिक वाचन (लिटर)',
    registerButton: 'मीटर नोंदवा',
    activeMetersList: 'अधिकृत मीटर्स निर्देशिका',
    searchMetersPlaceholder: 'मीटर आयडी, नाव किंवा विभागाने शोधा...',
    loadingMeters: 'मीटर्स लोड होत आहेत...',
    noMetersFound: 'कोणताही मीटर आढळला नाही.',
    residential: 'निवासी',
    commercial: 'व्यावसायिक',
    industrial: 'औद्योगिक',
    agricultural: 'कृषी',

    readingsTitle: 'मीटर वाचन आणि डेटा आयात',
    readingsSubtitle: 'CSV फाईल अपलोड करा किंवा मॅन्युअल वाचन नोंदवा.',
    selectMeterPrompt: 'कृपया मीटर निवडा',
    uploadCsvTitle: 'CSV फाईल अपलोड करा',
    uploadCsvDesc: 'मीटरच्या टेलिमेट्रीसाठी CSV फाईल निवडा (meter_id, timestamp, consumption_liters).',
    selectCsvFile: 'फाईल निवडा',
    uploadCsvButton: 'CSV अपलोड करा',
    uploading: 'डेटा आयात होत आहे...',
    manualReadingTitle: 'मॅन्युअल वाचन नोंदवा',
    readingValueLiters: 'वापर (लिटर)',
    readingTimestamp: 'वेळ (Timestamp)',
    submitReading: 'वाचन जतन करा',
    recentTelemetry: 'अलिकडील टेलिमेट्री नोंदी',
    loadingReadings: 'वाचन डेटा लोड होत आहे...',
    noReadingsFound: 'या मीटरसाठी कोणतीही नोंद उपलब्ध नाही.',
    sourceManual: 'मॅन्युअल',
    sourceCsv: 'CSV आयात',

    verificationViewTitle: 'मानवी पडताळणी कार्यप्रवाह',
    verificationViewSubtitle: 'संशयित विसंगती आणि संभाव्य गळतीची भौतिक पडताळणी करा.',
    pendingVerifications: 'पडताळणी प्रलंबित असलेल्या घटना',
    noPendingVerifications: 'सध्या कोणतीही पडताळणी प्रलंबित नाही.',

    scenarioLabTitle: 'महापालिका परिदृश्य प्रयोगशाळा',
    scenarioLabSubtitle: 'मानक पाणी वापराच्या परिदृश्यांचे परीक्षण करा.',
    selectScenarioPrompt: 'परिदृश्य निवडा',
    runScenarioButton: 'परिदृश्य चालवा',
    runningScenario: 'विश्लेषण सुरू आहे...',
    scenarioDescriptionTitle: 'परिदृश्य वर्णन आणि वैशिष्ट्ये',
    simulatedReadingsTitle: 'सिम्युलेटेड मीटर वाचन',
    analyticsOutcomeTitle: 'वस्तुनिष्ठ विश्लेषणात्मक निष्कर्ष',

    evaluationTitle: 'प्रणाली मूल्यांकन आणि बेंचमार्क',
    evaluationSubtitle: 'मानक परिदृश्यांवर आधारित वास्तविक अचूकता आणि कामगिरी मेट्रिक्स.',
    runEvaluationButton: 'संपूर्ण मूल्यांकन चालवा',
    runningEvaluation: 'मूल्यांकन प्रक्रिया सुरू आहे...',
    evaluationSummaryTitle: 'मोजलेले बेंचमार्क निष्कर्ष',
    metricPrecision: 'अचूकता (Precision)',
    metricRecall: 'रिकॉल (Recall)',
    metricF1: 'F1 स्कोअर',
    metricFAR: 'खोटा गजर दर (FAR)',
    metricMAE: 'सरासरी त्रुटी (MAE)',
    metricLatency: 'सतर्कता विलंब',
    metricGroqSuccess: 'AI रचना यश',
    metricFallbackCoverage: 'फॉलबॅक कव्हरेज',
    metricWorkflowCompletion: 'कार्यप्रवाह पूर्णता',
    scenariosEvaluated: 'मूल्यांकन केलेले परिदृश्य',

    waterImpactTitle: 'जल प्रभाव आणि संभाव्य बचत',
    waterImpactSubtitle: 'अधिकृत पुराव्यावर आधारित संभाव्य अतिरिक्त वापर आणि आर्थिक हानी.',
    totalEstimatedExcessLoss: 'एकूण अंदाजे संभाव्य अतिरिक्त हानी',
    totalPotentialCost: 'अंदाजे संभाव्य आर्थिक हानी',
    affectedMetersCount: 'संशयित विसंगती असलेले मीटर्स',
    waterSavingsMessage: 'वेळेवर पडताळणी आणि दुरुस्तीमुळे महापालिकेचे अमूल्य पाणी वाचवता येते.',
    impactTableTitle: 'मीटरनुसार अंदाजे जल प्रभाव',
    meterColumn: 'मीटर आयडी',
    zoneColumn: 'विभाग',
    lossColumn: 'अंदाजे हानी (लिटर)',
    estimatedCostColumn: 'अंदाजे खर्च (₹)',

    settingsTitle: 'प्रणाली सेटिंग्ज आणि सुरक्षा प्रोफाइल',
    settingsSubtitle: 'भाषा आणि प्रमाणीकरण कॉन्फिगरेशन.',
    languageSettingsTitle: 'इंटरफेस भाषा',
    interfaceLanguageDesc: 'तुमची पसंतीची भाषा निवडा (इंग्रजी, मराठी, किंवा हिंदी).',
    authSectionTitle: 'प्रमाणीकृत वापरकर्ता सत्र',
    userEmail: 'ईमेल पत्ता',
    userRole: 'नियुक्त भूमिका',
    organization: 'संस्था आयडी',
    tokenStatus: 'सत्र टोकन स्थिती',
    tokenActive: 'सक्रिय (Cryptographically Signed JWT)',
    systemArchitectureTitle: 'प्लॅटफॉर्म आर्किटेक्चर आणि स्थिती',
    backendVersion: 'बॅकएंड API आवृत्ती',
    groqModel: 'AI मॉडेल (Groq)',

    alertsSubtitle: 'मानवी पडताळणी किंवा जीवनचक्र निकालाची आवश्यकता असलेल्या विसंगती सतर्कता',
    detectedAt: 'नोंदवलेली वेळ',
    inspectAndAction: 'तपासा आणि कृती करा',
    readingsLogTitle: 'नोंदवलेले टाइम-सिरीज वाचन',
    requiredCsvFormat: 'आवश्यक CSV स्वरूप:',
    uploadAndProcessCsv: 'CSV अपलोड करा आणि प्रक्रिया करा',
    evidenceSubtitle: 'विसंगती निर्णयांना समर्थन देणारे वस्तुनिष्ठ पुरावे',
    evidencePrincipleTitle: 'अपरिवर्तनीय पुरावा तत्त्व',
    evidencePrincipleDesc: 'येथे प्रदर्शित केलेला पुरावा थेट बॅकएंड सांख्यिकीय अल्गोरिदमवरून प्राप्त केला आहे. हे AI स्पष्टीकरण आणि मानवी पडताळणीपूर्वीचा एकमेव वस्तुनिष्ठ आधार आहे.',
    executionParameters: 'कार्यकारी घटक',
    randomSeedLabel: 'रँडम सीड (पुनरुत्पादनक्षमता)',
    deterministicSeedNote: 'निश्चित सीड तंतोतंत पुनरुत्पादनक्षम संख्या सुनिश्चित करते.',
    simulationRunResult: 'सिम्युलेशन निकाल',
    operationalLatency: 'प्रक्रिया विलंब',
    confusionMatrixTitle: 'कन्फ्युजन मॅट्रिक्स आणि अलर्ट दर',
    scientificReportingTitle: 'वैज्ञानिक वास्तवता अहवाल मानके',
    scientificReportingDesc: 'मेट्रिक्स केवळ प्रत्यक्ष परिदृश्ये किंवा रनटाइम मोजमापांवरून सत्यापित केल्यावरच नोंदवले जातात. दीर्घकालीन डेटा नसलेली वैशिष्ट्ये अद्याप मोजलेले नाही म्हणून दर्शविली जातात.',
    groundTruthValidationMatrix: 'वास्तवता पडताळणी मॅट्रिक्स',
    scenarioCol: 'परिदृश्य',
    expectedGroundTruthCol: 'अपेक्षित वास्तव',
    actualAnalyticsOutcomeCol: 'प्रत्यक्ष विश्लेषणात्मक निष्कर्ष',
    resultCol: 'बेंचमार्क निकाल',
    groundTruthLabel: 'अपेक्षित वास्तव:',
    impactAssumptionTitle: 'जल प्रभाव गृहीतके',
    avoidedFractionLabel: 'संभाव्य टाळता येणारा भाग:',
    scopeFilterLabel: 'व्याप्ती फिल्टर:',
    scopeAllOption: 'सर्व अधिकृत सक्रिय विसंगती (एकूण)',
    scopeFilterHelp: 'विशिष्ट मीटरनुसार किंवा एकूण अधिकृत मीटरनुसार संभाव्य बचतीचे विश्लेषण करा.',
    projectedAvoidedWaterLoss: 'संभाव्य टाळलेली पाणी हानी',
    equivalencyPerspective: 'तुलनात्मक दृष्टिकोन:',
    standard20LCans: 'मानक २० लिटर पाण्याच्या कॅन्सची बचत.',
    dailyAllowances: 'दैनिक पिण्याचे/स्वच्छतेचे प्रमाण (१५० लि/दिवस/व्यक्ती).',
    systemConfigSubtitle: 'प्रणाली संरचना, सुरक्षा क्रेडेन्शियल्स आणि AI पॅरामीटर्स',
    applyToken: 'टोकन लागू करा',
    tokenApplied: 'टोकन लागू केले',
    aiGuardrailsTitle: 'लागू केलेले AI सुरक्षा नियम:',
  },
  'hi-IN': {
    appName: 'जल रक्षक AI',
    tagline: 'एनालिटिक्स पहचानता है। साक्ष्य समर्थन करता है। AI समझाता है। मानव सत्यापित करता है।',
    waterAnomalyDecisionSupport: 'जल विसंगति निर्णय समर्थन',
    corePrincipleTitle: 'मार्गदर्शक सिद्धांत:',
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
    openMenu: 'नेविगेशन मेनू खोलें',
    closeMenu: 'नेविगेशन मेनू बंद करें',
    logout: 'लॉग आउट (Logout)',
    environment: 'पर्यावरण:',
    apiConnected: 'बैकएंड API जुड़ा हुआ है',

    loading: 'लोड हो रहा है...',
    error: 'त्रुटि',
    success: 'सफल',
    cancel: 'रद्द करें',
    submit: 'जमा करें',
    save: 'सहेजें',
    close: 'बंद करें',
    closeModal: 'डायलॉग बंद करें',
    search: 'खोजें',
    filter: 'फ़िल्टर',
    refresh: 'डेटा रीफ़्रेश करें',
    actions: 'क्रियाएँ',
    noData: 'कोई डेटा उपलब्ध नहीं है',
    retry: 'पुनः प्रयास करें',
    clearFilters: 'फ़िल्टर हटाएं',
    viewDetails: 'विवरण देखें',
    status: 'स्थिति',

    suspectedAnomaly: 'संदिग्ध विसंगति',
    possibleLeak: 'संभावित रिसाव',
    estimatedExcessConsumption: 'अनुमानित अतिरिक्त खपत',
    physicalVerificationRequired: 'भौतिक सत्यापन आवश्यक',
    routineObservation: 'नियमित अवलोकन',
    safetyDisclaimer: '* विश्लेषणात्मक जोखिम स्कोर संदिग्ध विसंगति / संभावित रिसाव दर्शाता है। भौतिक सत्यापन आवश्यक है।',

    severity: 'गंभीरता',
    riskScore: 'जोखिम स्कोर',
    severityCritical: 'CRITICAL',
    severityHigh: 'HIGH',
    severityMedium: 'MEDIUM',
    severityLow: 'LOW',
    statusOpen: 'DETECTED',
    statusAcknowledged: 'ACKNOWLEDGED',
    statusVerifying: 'VERIFYING',
    statusConfirmed: 'CONFIRMED',
    statusFalseAlarm: 'FALSE_ALARM',
    statusInvestigating: 'INVESTIGATING',
    statusResolved: 'RESOLVED',

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
    loadingAnalytics: 'अधिकृत विश्लेषणात्मक डेटा लोड हो रहा है...',
    recentAlertsTitle: 'हालिया संदिग्ध विसंगतियां और अलर्ट',
    viewAllAlerts: 'सभी अलर्ट देखें',
    noActiveAlertsTitle: 'कोई सक्रिय अलर्ट नहीं',
    noActiveAlertsDesc: 'सभी अधिकृत मीटर सामान्य बेसलाइन सीमा के भीतर कार्य कर रहे हैं।',
    systemOverviewTitle: 'सिस्टम अवलोकन',

    evidenceHierarchyTitle: 'विश्लेषणात्मक साक्ष्य पदानुक्रम',
    currentReading: '1. वर्तमान खपत (अवलोकित)',
    expectedBaseline: '2. अपेक्षित बेसलाइन',
    deviation: '3. विचलन प्रतिशत',
    persistence: '4. निरंतरता अंतराल',
    trend: '5. खपत का रुझान',
    estimatedExcess: '6. अनुमानित अतिरिक्त खपत',
    verificationRequired: '7. मानव सत्यापन स्थिति',
    deterministicBreakdownTitle: 'वस्तुनिष्ठ जोखिम घटक विभाजन (0–100):',
    deviationScoreLabel: 'विचलन स्कोर',
    persistenceScoreLabel: 'निरंतरता स्कोर',
    trendScoreLabel: 'रुझान स्कोर',
    lossScoreLabel: 'अनुमानित नुकसान स्कोर',
    humanVerificationStatus: 'मानव सत्यापन स्थिति:',
    noEvidenceRecorded: 'इस घटना के लिए कोई संरचित साक्ष्य दर्ज नहीं है।',
    consecutiveIntervals: 'लगातार अंतराल',
    litersUnit: 'लीटर',

    incidentDetails: 'घटना विवरण',
    meterIdLabel: 'मीटर आईडी',
    statusLabel: 'स्थिति',
    aiExplanationTitle: 'AI स्पष्टीकरण कार्ड',
    generateExplanation: 'स्पष्टीकरण प्राप्त करें',
    sourceGroq: 'स्रोत: ग्रॉक AI (Groq)',
    sourceDeterministic: 'स्रोत: नियतात्मक फॉलबैक (Deterministic)',
    languageLabel: 'भाषा:',
    clickToGenerateExplanation: 'साक्ष्य-आधारित स्पष्टीकरण प्राप्त करने के लिए बटन पर क्लिक करें।',
    physicalVerificationGuidanceTitle: 'साइट पर भौतिक सत्यापन मार्गदर्शन',
    verificationStep1: 'सभी आंतरिक नल, फ्लश टैंक और बाहरी पाइपों की निरंतर जांच करें।',
    verificationStep2: 'शून्य-खपत जांच: सुनिश्चित करें कि सभी नल बंद हैं और देखें कि क्या मीटर घूम रहा है।',
    verificationStep3: 'खुली आपूर्ति लाइनों और जोड़ों पर नमी या रिसाव की जांच करें।',
    verificationStep4: 'असामान्य उपयोग की पुष्टि करें या अधिकृत वर्कफ़्लो का उपयोग करके गलत अलार्म चिह्नित करें।',
    authorizedLifecycleActions: 'अधिकृत जीवनचक्र क्रियाएं',
    auditNotePlaceholder: 'वैकल्पिक ऑडिट नोट...',
    acknowledge: 'अलर्ट स्वीकार करें',
    beginVerification: 'सत्यापन शुरू करें',
    confirmAbnormal: 'असामान्य घटना की पुष्टि करें',
    markFalseAlarm: 'गलत अलार्म चिह्नित करें',
    investigate: 'जांच जारी रखें',
    resolveIncident: 'घटना का समाधान करें',
    incidentResolvedMessage: 'घटना का समाधान हो गया है और यह बंद है।',

    filterBySeverity: 'गंभीरता अनुसार फ़िल्टर',
    allSeverities: 'सभी गंभीरता',
    filterByStatus: 'स्थिति अनुसार फ़िल्टर',
    allStatuses: 'सभी स्थितियां',
    filterByCategory: 'श्रेणी अनुसार फ़िल्टर',
    allCategories: 'सभी श्रेणियां',

    registerNewMeter: 'नया मीटर पंजीकृत करें',
    meterId: 'मीटर आईडी',
    meterName: 'मीटर का नाम',
    zone: 'ज़ोन / स्थान',
    category: 'श्रेणी',
    initialReading: 'प्रारंभिक रीडिंग (लीटर)',
    registerButton: 'मीटर पंजीकृत करें',
    activeMetersList: 'अधिकृत मीटर निर्देशिका',
    searchMetersPlaceholder: 'मीटर आईडी, नाम या ज़ोन से खोजें...',
    loadingMeters: 'मीटर लोड हो रहे हैं...',
    noMetersFound: 'कोई मेल खाता मीटर नहीं मिला।',
    residential: 'आवासीय',
    commercial: 'वाणिज्यिक',
    industrial: 'औद्योगिक',
    agricultural: 'कृषि',

    readingsTitle: 'मीटर रीडिंग और टेलीमेट्री आयात',
    readingsSubtitle: 'समय-श्रृंखला CSV डेटा अपलोड करें या मैन्युअल रीडिंग दर्ज करें।',
    selectMeterPrompt: 'कृपया मीटर चुनें',
    uploadCsvTitle: 'CSV रीडिंग अपलोड करें',
    uploadCsvDesc: 'CSV प्रारूप में टेलीमेट्री आयात करें (meter_id, timestamp, consumption_liters)।',
    selectCsvFile: 'फ़ाइल चुनें',
    uploadCsvButton: 'CSV अपलोड करें',
    uploading: 'टेलीमेट्री डेटा आयात हो रहा है...',
    manualReadingTitle: 'मैन्युअल रीडिंग दर्ज करें',
    readingValueLiters: 'खपत (लीटर)',
    readingTimestamp: 'समय (Timestamp)',
    submitReading: 'रीडिंग सहेजें',
    recentTelemetry: 'हालिया टेलीमेट्री लॉग',
    loadingReadings: 'टेलीमेट्री रीडिंग लोड हो रही है...',
    noReadingsFound: 'इस मीटर के लिए कोई टेलीमेट्री रिकॉर्ड नहीं मिला।',
    sourceManual: 'मैन्युअल',
    sourceCsv: 'CSV आयात',

    verificationViewTitle: 'मानव-इन-द-लूप सत्यापन',
    verificationViewSubtitle: 'संदिग्ध विसंगतियों और संभावित रिसाव का भौतिक सत्यापन करें।',
    pendingVerifications: 'सत्यापन की आवश्यकता वाली घटनाएं',
    noPendingVerifications: 'वर्तमान में कोई सत्यापन लंबित नहीं है।',

    scenarioLabTitle: 'नगरपालिका परिदृश्य प्रयोगशाला (Scenario Lab)',
    scenarioLabSubtitle: 'मानक जल उपयोग परिदृश्यों का परीक्षण करें।',
    selectScenarioPrompt: 'परिदृश्य चुनें',
    runScenarioButton: 'परिदृश्य चलाएं',
    runningScenario: 'विश्लेषण जारी है...',
    scenarioDescriptionTitle: 'परिदृश्य प्रोफ़ाइल और विशेषताएँ',
    simulatedReadingsTitle: 'सिम्युलेटेड मीटर रीडिंग',
    analyticsOutcomeTitle: 'विश्लेषणात्मक परिणाम',

    evaluationTitle: 'सिस्टम प्रदर्शन और बेंचमार्क मूल्यांकन',
    evaluationSubtitle: 'मानक परिदृश्यों पर आधारित वास्तविक सटीकता और प्रदर्शन मेट्रिक्स।',
    runEvaluationButton: 'पूर्ण बेंचमार्क मूल्यांकन चलाएं',
    runningEvaluation: 'बेंचमार्क मूल्यांकन चल रहा है...',
    evaluationSummaryTitle: 'मापे गए बेंचमार्क परिणाम',
    metricPrecision: 'सटीकता (Precision)',
    metricRecall: 'रिकॉल (Recall)',
    metricF1: 'F1 स्कोर',
    metricFAR: 'गलत अलार्म दर (FAR)',
    metricMAE: 'माध्य निरपेक्ष त्रुटि (MAE)',
    metricLatency: 'अलर्ट विलंबता',
    metricGroqSuccess: 'AI संरचित सफलता',
    metricFallbackCoverage: 'फॉलबॅक कवरेज',
    metricWorkflowCompletion: 'वर्कफ़्लो पूर्णता',
    scenariosEvaluated: 'मूल्यांकित मानक परिदृश्य',

    waterImpactTitle: 'जल प्रभाव और संभावित बचत विश्लेषण',
    waterImpactSubtitle: 'अधिकृत साक्ष्य के आधार पर अनुमानित अतिरिक्त खपत और संभावित बचत।',
    totalEstimatedExcessLoss: 'कुल अनुमानित अतिरिक्त खपत',
    totalPotentialCost: 'अनुमानित वित्तीय नुकसान',
    affectedMetersCount: 'संदिग्ध विसंगति वाले मीटर',
    waterSavingsMessage: 'समय पर सत्यापन और मरम्मत से नगरपालिका के पानी की बर्बादी को रोका जा सकता है।',
    impactTableTitle: 'मीटर अनुसार अनुमानित जल प्रभाव',
    meterColumn: 'मीटर आईडी',
    zoneColumn: 'ज़ोन / स्थान',
    lossColumn: 'अनुमानित अतिरिक्त खपत (लीटर)',
    estimatedCostColumn: 'अनुमानित लागत (₹)',

    settingsTitle: 'सिस्टम सेटिंग्स और सुरक्षा प्रोफ़ाइल',
    settingsSubtitle: 'भाषा और प्रमाणीकरण कॉन्फ़िगरेशन।',
    languageSettingsTitle: 'इंटरफ़ेस भाषा',
    interfaceLanguageDesc: 'अपनी पसंदीदा भाषा चुनें (अंग्रेजी, मराठी, या हिंदी)।',
    authSectionTitle: 'प्रमाणित उपयोगकर्ता सत्र',
    userEmail: 'ईमेल पता',
    userRole: 'निर्धारित भूमिका',
    organization: 'संगठन आईडी',
    tokenStatus: 'सत्र टोकन स्थिति',
    tokenActive: 'सक्रिय (Cryptographically Signed JWT)',
    systemArchitectureTitle: 'प्लेटफ़ॉर्म आर्किटेक्चर और स्थिति',
    backendVersion: 'बैकएंड API संस्करण',
    groqModel: 'AI मॉडल (Groq)',

    alertsSubtitle: 'मानव सत्यापन या जीवनचक्र समाधान की आवश्यकता वाले विसंगति अलर्ट',
    detectedAt: 'पहचान का समय',
    inspectAndAction: 'जांचें और कार्रवाई करें',
    readingsLogTitle: 'दर्ज समय-श्रृंखला रीडिंग',
    requiredCsvFormat: 'आवश्यक CSV प्रारूप:',
    uploadAndProcessCsv: 'CSV अपलोड करें और संसाधित करें',
    evidenceSubtitle: 'विसंगति निर्णयों का समर्थन करने वाले संरचित वस्तुनिष्ठ साक्ष्य',
    evidencePrincipleTitle: 'अपरिवर्तनीय साक्ष्य प्रथम सिद्धांत',
    evidencePrincipleDesc: 'यहां प्रदर्शित साक्ष्य सीधे बैकएंड सांख्यिकीय एल्गोरिदम से प्राप्त होते हैं। यह AI स्पष्टीकरण और मानव सत्यापन से पहले एकमात्र तथ्यात्मक आधार है।',
    executionParameters: 'निष्पादन पैरामीटर',
    randomSeedLabel: 'रैंडम सीड (पुनरुत्पादन क्षमता)',
    deterministicSeedNote: 'निश्चित सीड सटीक पुनरुत्पादन योग्य संख्या की गारंटी देता है।',
    simulationRunResult: 'सिम्युलेशन परिणाम',
    operationalLatency: 'परिचालन विलंबता',
    confusionMatrixTitle: 'कन्फ्यूजन मैट्रिक्स और अलर्ट दर',
    scientificReportingTitle: 'वैज्ञानिक सत्यता रिपोर्टिंग मानक',
    scientificReportingDesc: 'मेट्रिक्स केवल तभी रिपोर्ट किए जाते हैं जब मानक परिदृश्यों या अनुभवजन्य रनटाइम मापों के विरुद्ध सत्यापित हों। दीर्घकालिक डेटा की कमी वाली सुविधाओं को स्पष्ट रूप से अभी तक मापा नहीं गया के रूप में रिपोर्ट किया जाता है।',
    groundTruthValidationMatrix: 'सत्यता सत्यापन मैट्रिक्स (Ground Truth)',
    scenarioCol: 'परिदृश्य',
    expectedGroundTruthCol: 'अपेक्षित सत्यता',
    actualAnalyticsOutcomeCol: 'वास्तविक विश्लेषणात्मक परिणाम',
    resultCol: 'बेंचमार्क परिणाम',
    groundTruthLabel: 'अपेक्षित सत्यता:',
    impactAssumptionTitle: 'प्रभाव अनुमान पैरामीटर',
    avoidedFractionLabel: 'बचत योग्य अनुमानित अनुपात:',
    scopeFilterLabel: 'स्कोप फ़िल्टर:',
    scopeAllOption: 'सभी अधिकृत सक्रिय विसंगतियां (कुल योग)',
    scopeFilterHelp: 'किसी विशिष्ट सक्रिय मीटर या सभी अधिकृत मीटरों के कुल योग के अनुसार संभावित बचत फ़िल्टर करें।',
    projectedAvoidedWaterLoss: 'अनुमानित सुरक्षित किया गया जल',
    equivalencyPerspective: 'समतुल्यता परिप्रेक्ष्य:',
    standard20LCans: 'मानक 20 लीटर पानी के डिब्बे बचाए गए।',
    dailyAllowances: 'दैनिक पेयजल/स्वच्छता भत्ता (150 लीटर/दिन/व्यक्ति)।',
    systemConfigSubtitle: 'सिस्टम कॉन्फ़िगरेशन, सुरक्षा क्रेडेंशियल्स और AI पैरामीटर',
    applyToken: 'टोकन लागू करें',
    tokenApplied: 'टोकन लागू किया गया',
    aiGuardrailsTitle: 'लागू AI सुरक्षा नियम (Guardrails):',
  },
};
