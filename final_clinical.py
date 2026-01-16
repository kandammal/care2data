


import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set
from enum import Enum
import json

# Core NLP Libraries
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")

try:
    import scispacy
    import en_core_sci_md
    SCISPACY_AVAILABLE = True
except ImportError:
    SCISPACY_AVAILABLE = False
    print("Warning: scispaCy not available. Install with: pip install scispacy")
    print("Then: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_md-0.5.1.tar.gz")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: Transformers not available. Install with: pip install transformers torch")

# Medical Entity Recognition
try:
    from medcat.cat import CAT
    MEDCAT_AVAILABLE = True
except ImportError:
    MEDCAT_AVAILABLE = False
    print("Warning: MedCAT not available. Install with: pip install medcat")


class Severity(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    LIFE_THREATENING = "Life-Threatening"


class RiskLevel(Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class MedicalEntity:
    """Represents a medical entity extracted via NLP"""
    text: str
    label: str  # DISEASE, SYMPTOM, DRUG, ANATOMY
    start: int
    end: int
    confidence: float
    cui: str = ""  # Concept Unique Identifier (UMLS)
    semantic_type: str = ""


@dataclass
class ExtractedSymptom:
    raw_text: str
    clinical_term: str
    severity: Severity
    mechanism: str
    confidence: float
    negated: bool = False
    temporal: str = ""  # onset timing
    frequency: str = ""  # how often


@dataclass
class PatientData:
    record_id: str
    age: int
    gender: str
    drug_name: str
    health_issues: str
    start_date: str
    stop_date: str
    days_taken: int
    stop_reason: str


class AdvancedClinicalNLP:
    """Advanced NLP processor using medical-domain models"""
    
    def __init__(self):
        self.nlp = None
        self.ner_pipeline = None
        self.sentiment_analyzer = None
        self.medical_entities_cache = {}
        
        # Initialize models
        self._initialize_models()
        
        # Enhanced medical knowledge base
        self.symptom_severity_indicators = {
            'severe': 3,
            'extreme': 3,
            'unbearable': 3,
            'intense': 3,
            'excruciating': 3,
            'moderate': 2,
            'significant': 2,
            'persistent': 2,
            'constant': 2,
            'mild': 1,
            'slight': 1,
            'occasional': 1,
            'intermittent': 1
        }
        
        self.temporal_patterns = {
            r'\b(for\s+(?:the\s+)?past\s+(\d+)\s+(day|week|month)s?)\b': 'chronic',
            r'\b(since|started|began)\b': 'onset',
            r'\b(sudden|suddenly|acute)\b': 'acute',
            r'\b(gradual|gradually|progressive)\b': 'gradual',
            r'\b(multiple times|several times|(\d+)\s+times)\s+(daily|per day|a day)\b': 'frequent'
        }
        
        self.negation_patterns = [
            r'\bno\s+',
            r'\bnot\s+',
            r'\bwithout\s+',
            r'\bdenies\s+',
            r'\babsence\s+of\s+',
            r'\bnever\s+'
        ]
        
        # Drug-specific knowledge base with mechanisms
        self.drug_knowledge = {
            'metformin': {
                'class': 'Biguanide',
                'common_side_effects': [
                    'nausea', 'diarrhea', 'abdominal pain', 'flatulence', 
                    'vitamin B12 deficiency', 'metallic taste'
                ],
                'serious_risks': [
                    'lactic acidosis', 'hypoglycemia', 'renal failure'
                ],
                'mechanism': {
                    'primary': 'Inhibits mitochondrial respiratory chain complex I, reducing hepatic gluconeogenesis',
                    'gi_effects': 'Increases intestinal serotonin secretion and alters gut microbiome',
                    'lactic_acidosis': 'Inhibits lactate clearance in liver and kidneys, increases lactate production in intestines'
                },
                'risk_factors': [
                    'renal impairment (eGFR <45)', 'elderly (>65 years)', 
                    'hepatic dysfunction', 'dehydration', 'contrast agents', 
                    'alcohol abuse', 'heart failure'
                ],
                'contraindications': ['severe renal impairment', 'metabolic acidosis', 'acute heart failure']
            },
            'atorvastatin': {
                'class': 'HMG-CoA Reductase Inhibitor (Statin)',
                'common_side_effects': [
                    'myalgia', 'arthralgia', 'headache', 'dyspepsia', 
                    'nasopharyngitis', 'elevated transaminases'
                ],
                'serious_risks': [
                    'rhabdomyolysis', 'myopathy', 'hepatotoxicity', 
                    'new-onset diabetes', 'hemorrhagic stroke'
                ],
                'mechanism': {
                    'primary': 'Competitive inhibition of HMG-CoA reductase, rate-limiting enzyme in cholesterol biosynthesis',
                    'muscle_effects': 'Depletes coenzyme Q10 and impairs mitochondrial function in myocytes',
                    'hepatic_effects': 'Increases hepatic LDL receptors; rare idiosyncratic hepatotoxicity'
                },
                'risk_factors': [
                    'elderly', 'female gender', 'low BMI', 'multisystem disease',
                    'drug interactions (fibrates, azoles, macrolides)', 
                    'hypothyroidism', 'renal impairment'
                ],
                'monitoring': ['CK levels', 'liver enzymes', 'lipid panel']
            },
            'sertraline': {
                'class': 'Selective Serotonin Reuptake Inhibitor (SSRI)',
                'common_side_effects': [
                    'nausea', 'diarrhea', 'insomnia', 'somnolence', 
                    'dizziness', 'tremor', 'sexual dysfunction', 
                    'dry mouth', 'increased sweating'
                ],
                'serious_risks': [
                    'serotonin syndrome', 'suicidal ideation', 'bleeding', 
                    'hyponatremia', 'seizures', 'QT prolongation'
                ],
                'mechanism': {
                    'primary': 'Selectively inhibits presynaptic serotonin reuptake, increasing synaptic 5-HT',
                    'gi_effects': 'Activates 5-HT3 and 5-HT4 receptors in GI tract causing nausea',
                    'cns_effects': 'Modulates multiple 5-HT receptor subtypes affecting mood, sleep, anxiety'
                },
                'risk_factors': [
                    'concurrent MAOIs', 'bleeding disorders', 'seizure history',
                    'bipolar disorder', 'hyponatremia risk', 'elderly'
                ],
                'interactions': ['MAOIs', 'NSAIDs', 'anticoagulants', 'triptans', 'tramadol']
            },
            'lisinopril': {
                'class': 'ACE Inhibitor',
                'common_side_effects': [
                    'cough', 'hypotension', 'dizziness', 'headache',
                    'fatigue', 'nausea', 'hyperkalemia'
                ],
                'serious_risks': [
                    'angioedema', 'acute renal failure', 'hyperkalemia',
                    'hepatotoxicity', 'neutropenia'
                ],
                'mechanism': {
                    'primary': 'Inhibits angiotensin-converting enzyme, reducing angiotensin II formation',
                    'cough': 'Accumulation of bradykinin and substance P in respiratory tract',
                    'renal_effects': 'Dilates efferent arteriole reducing intraglomerular pressure'
                },
                'risk_factors': [
                    'renal artery stenosis', 'volume depletion', 'elderly',
                    'concurrent NSAIDs', 'potassium supplements'
                ]
            },
            'warfarin': {
                'class': 'Vitamin K Antagonist',
                'common_side_effects': [
                    'bleeding', 'bruising', 'hemorrhage', 'hematoma'
                ],
                'serious_risks': [
                    'major hemorrhage', 'intracranial bleeding', 
                    'warfarin necrosis', 'purple toe syndrome'
                ],
                'mechanism': {
                    'primary': 'Inhibits vitamin K epoxide reductase, preventing activation of clotting factors II, VII, IX, X',
                    'bleeding': 'Impairs coagulation cascade leading to prolonged clotting times'
                },
                'risk_factors': [
                    'elderly', 'falls risk', 'concurrent antiplatelet agents',
                    'liver disease', 'malignancy', 'poor INR control'
                ],
                'monitoring': ['INR', 'signs of bleeding']
            }
        }
        
        # UMLS semantic types for medical concepts
        self.semantic_types = {
            'T047': 'Disease or Syndrome',
            'T184': 'Sign or Symptom',
            'T121': 'Pharmacologic Substance',
            'T023': 'Body Part, Organ, or Organ Component',
            'T033': 'Finding',
            'T037': 'Injury or Poisoning'
        }
    
    def _initialize_models(self):
        """Initialize NLP models"""
        print("Initializing NLP models...")
        
        # Initialize scispaCy for medical NER
        if SCISPACY_AVAILABLE:
            try:
                self.nlp = en_core_sci_md.load()
                print("✓ Loaded en_core_sci_md (scispaCy)")
            except Exception as e:
                print(f"✗ Failed to load scispaCy: {e}")
                self.nlp = None
        
        # Initialize Transformers for medical NER
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use BioBERT-based NER model
                self.ner_pipeline = pipeline(
                    "ner",
                    model="alvaroalon2/biobert_diseases_ner",
                    aggregation_strategy="simple"
                )
                print("✓ Loaded BioBERT NER pipeline")
            except Exception as e:
                print(f"✗ Failed to load BioBERT: {e}")
                self.ner_pipeline = None
        
        if not self.nlp and not self.ner_pipeline:
            print("⚠ No medical NLP models available. Using rule-based approach.")
    
    def extract_medical_entities(self, text: str) -> List[MedicalEntity]:
        """Extract medical entities using multiple NLP approaches"""
        entities = []
        
        # Method 1: scispaCy
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append(MedicalEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.85,
                    semantic_type=ent.label_
                ))
        
        # Method 2: BioBERT NER
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text)
                for result in ner_results:
                    entities.append(MedicalEntity(
                        text=result['word'],
                        label=result['entity_group'],
                        start=result['start'],
                        end=result['end'],
                        confidence=result['score']
                    ))
            except Exception as e:
                print(f"BioBERT NER error: {e}")
        
        # Deduplicate and merge overlapping entities
        entities = self._merge_entities(entities)
        
        return entities
    
    def _merge_entities(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Merge overlapping entities, keeping highest confidence"""
        if not entities:
            return []
        
        # Sort by start position
        entities.sort(key=lambda x: (x.start, -x.confidence))
        
        merged = []
        current = entities[0]
        
        for entity in entities[1:]:
            # Check for overlap
            if entity.start <= current.end:
                # Keep higher confidence entity
                if entity.confidence > current.confidence:
                    current = entity
            else:
                merged.append(current)
                current = entity
        
        merged.append(current)
        return merged
    
    def extract_symptoms_nlp(self, text: str) -> List[ExtractedSymptom]:
        """Extract symptoms using NLP with context analysis"""
        symptoms = []
        
        # Extract medical entities
        entities = self.extract_medical_entities(text)
        
        # Filter for symptoms and signs
        symptom_entities = [
            e for e in entities 
            if any(label in e.label for label in ['SYMPTOM', 'SIGN', 'DISEASE'])
        ]
        
        # Process each symptom with context
        for entity in symptom_entities:
            # Extract context window
            context_start = max(0, entity.start - 100)
            context_end = min(len(text), entity.end + 100)
            context = text[context_start:context_end]
            
            # Analyze context
            severity = self._analyze_severity_context(context)
            negated = self._check_negation(context, entity.text)
            temporal = self._extract_temporal_info(context)
            frequency = self._extract_frequency(context)
            
            if not negated:  # Only add non-negated symptoms
                symptoms.append(ExtractedSymptom(
                    raw_text=entity.text,
                    clinical_term=self._normalize_term(entity.text),
                    severity=severity,
                    mechanism="",
                    confidence=entity.confidence,
                    negated=negated,
                    temporal=temporal,
                    frequency=frequency
                ))
        
        # Fallback: rule-based extraction for common symptoms
        rule_based_symptoms = self._extract_symptoms_rules(text)
        
        # Merge NLP and rule-based results
        all_symptoms = self._merge_symptoms(symptoms, rule_based_symptoms)
        
        return all_symptoms
    
    def _extract_symptoms_rules(self, text: str) -> List[ExtractedSymptom]:
        """Rule-based symptom extraction (fallback)"""
        symptom_patterns = {
            r'\b(nausea|nauseous|queasy)\b': 'Nausea',
            r'\b(vomit|vomiting|emesis)\b': 'Emesis',
            r'\b(weakness|weak|fatigue|tired|exhausted|asthenia)\b': 'Asthenia',
            r'\b(loss of appetite|anorexia|not eating)\b': 'Anorexia',
            r'\b(stomach pain|abdominal pain|belly pain|cramping)\b': 'Abdominal Pain',
            r'\b(dizz(y|iness)|lightheaded|vertigo)\b': 'Dizziness',
            r'\b(muscle (pain|ache)|myalgia|body aches)\b': 'Myalgia',
            r'\b(shortness of breath|difficulty breathing|dyspnea|breathless)\b': 'Dyspnea',
            r'\b(diarrhea|loose stools)\b': 'Diarrhea',
            r'\b(headache|cephalgia)\b': 'Cephalgia',
            r'\b(rash|hives|urticaria|itching|pruritus)\b': 'Dermatologic Reaction',
            r'\b(chest pain|angina)\b': 'Chest Pain',
            r'\b(palpitations|racing heart|tachycardia)\b': 'Palpitations',
            r'\b(confusion|disoriented|delirium)\b': 'Confusion',
            r'\b(tremor|shaking|trembling)\b': 'Tremor',
            r'\b(insomnia|can\'?t sleep|sleeplessness)\b': 'Insomnia',
            r'\b(constipation|hard stools)\b': 'Constipation',
            r'\b(sweat|perspiration|diaphoresis)\b': 'Diaphoresis',
            r'\b(cough|coughing)\b': 'Cough',
            r'\b(dark.{0,10}urine|brown.{0,10}urine)\b': 'Dark Urine',
            r'\b(edema|swelling)\b': 'Edema',
        }
        
        symptoms = []
        text_lower = text.lower()
        
        for pattern, term in symptom_patterns.items():
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                severity = self._analyze_severity_context(context)
                negated = self._check_negation(context, match.group())
                
                if not negated:
                    symptoms.append(ExtractedSymptom(
                        raw_text=match.group(),
                        clinical_term=term,
                        severity=severity,
                        mechanism="",
                        confidence=0.7,
                        negated=False,
                        temporal=self._extract_temporal_info(context),
                        frequency=self._extract_frequency(context)
                    ))
        
        return symptoms
    
    def _merge_symptoms(self, nlp_symptoms: List[ExtractedSymptom], 
                       rule_symptoms: List[ExtractedSymptom]) -> List[ExtractedSymptom]:
        """Merge symptoms from different extraction methods"""
        # Create a dictionary keyed by clinical term
        symptom_dict = {}
        
        for symptom in nlp_symptoms + rule_symptoms:
            term = symptom.clinical_term
            if term not in symptom_dict:
                symptom_dict[term] = symptom
            else:
                # Keep the one with higher confidence
                if symptom.confidence > symptom_dict[term].confidence:
                    symptom_dict[term] = symptom
        
        return list(symptom_dict.values())
    
    def _normalize_term(self, text: str) -> str:
        """Normalize medical term to standard clinical terminology"""
        normalization_map = {
            'throw up': 'Emesis',
            'threw up': 'Emesis',
            'sick to stomach': 'Nausea',
            'can\'t breathe': 'Dyspnea',
            'tired': 'Fatigue',
            'exhausted': 'Fatigue',
            'belly pain': 'Abdominal Pain',
            'stomach ache': 'Abdominal Pain',
        }
        
        text_lower = text.lower().strip()
        return normalization_map.get(text_lower, text.title())
    
    def _analyze_severity_context(self, context: str) -> Severity:
        """Analyze severity from context"""
        context_lower = context.lower()
        
        severe_score = 0
        for indicator, score in self.symptom_severity_indicators.items():
            if indicator in context_lower:
                severe_score = max(severe_score, score)
        
        # Check for frequency indicators
        if any(word in context_lower for word in ['multiple times', 'constant', 'continuous', 'all day']):
            severe_score += 1
        
        # Map score to severity
        if severe_score >= 4:
            return Severity.LIFE_THREATENING
        elif severe_score >= 3:
            return Severity.SEVERE
        elif severe_score >= 2:
            return Severity.MODERATE
        else:
            return Severity.MILD
    
    def _check_negation(self, context: str, symptom: str) -> bool:
        """Check if symptom is negated in context"""
        # Find symptom position in context
        symptom_pos = context.lower().find(symptom.lower())
        if symptom_pos == -1:
            return False
        
        # Check for negation patterns before the symptom
        preceding_text = context[:symptom_pos].lower()
        
        for pattern in self.negation_patterns:
            if re.search(pattern + r'\w*\s*$', preceding_text):
                return True
        
        return False
    
    def _extract_temporal_info(self, context: str) -> str:
        """Extract temporal information about symptom onset"""
        for pattern, temporal_type in self.temporal_patterns.items():
            match = re.search(pattern, context.lower())
            if match:
                return f"{temporal_type}: {match.group()}"
        return ""
    
    def _extract_frequency(self, context: str) -> str:
        """Extract frequency information"""
        frequency_patterns = {
            r'(\d+)\s*times?\s*(daily|per day|a day)': 'times_per_day',
            r'multiple times': 'multiple_daily',
            r'constant|continuous|ongoing': 'continuous',
            r'intermittent|occasional': 'intermittent'
        }
        
        for pattern, freq_type in frequency_patterns.items():
            match = re.search(pattern, context.lower())
            if match:
                return f"{freq_type}: {match.group()}"
        return ""


class ClinicalNLPNarrator:
    """Main narrator using advanced NLP"""
    
    def __init__(self):
        self.nlp_processor = AdvancedClinicalNLP()
        self.drug_knowledge = self.nlp_processor.drug_knowledge
    
    def analyze_drug_mechanism(self, drug_name: str, symptoms: List[ExtractedSymptom],
                               patient: PatientData) -> Dict[str, str]:
        """Generate detailed mechanistic analysis"""
        drug_lower = drug_name.lower()
        
        # Find matching drug in knowledge base
        drug_info = None
        for key in self.drug_knowledge:
            if key in drug_lower:
                drug_info = self.drug_knowledge[key]
                break
        
        if not drug_info:
            return {
                'primary': 'Mechanism requires further investigation',
                'symptom_correlation': 'Unknown',
                'risk_assessment': 'Unable to assess without drug information'
            }
        
        mechanisms = {}
        
        # Primary mechanism
        mechanisms['drug_class'] = drug_info['class']
        mechanisms['primary_mechanism'] = drug_info['mechanism']['primary']
        
        # Symptom-specific mechanisms
        symptom_mechanisms = []
        symptom_names = [s.clinical_term.lower() for s in symptoms]
        
        for key, mech_text in drug_info['mechanism'].items():
            if key != 'primary':
                symptom_mechanisms.append(f"{key.replace('_', ' ').title()}: {mech_text}")
        
        mechanisms['symptom_specific'] = symptom_mechanisms
        
        # Risk factor analysis
        risk_factors_present = []
        health_lower = patient.health_issues.lower()
        
        for risk in drug_info.get('risk_factors', []):
            if any(term in health_lower for term in risk.lower().split()):
                risk_factors_present.append(risk)
        
        if patient.age > 65 and 'elderly' in [r.lower() for r in drug_info.get('risk_factors', [])]:
            risk_factors_present.append(f'Advanced age ({patient.age} years)')
        
        mechanisms['risk_factors_present'] = risk_factors_present
        
        # Serious risk correlation
        serious_risks = []
        for risk in drug_info.get('serious_risks', []):
            for symptom in symptoms:
                if any(word in symptom.clinical_term.lower() for word in risk.lower().split()):
                    serious_risks.append(risk)
        
        mechanisms['serious_risks_detected'] = list(set(serious_risks))
        
        return mechanisms
    
    def detect_serious_risks(self, patient: PatientData, 
                            symptoms: List[ExtractedSymptom],
                            mechanisms: Dict) -> Dict[str, Dict]:
        """Advanced risk detection with clinical reasoning"""
        risks = {}
        
        symptom_terms = {s.clinical_term.lower() for s in symptoms}
        health_lower = patient.health_issues.lower()
        drug_lower = patient.drug_name.lower()
        
        # Metabolic risks
        metabolic_indicators = {'dyspnea', 'myalgia', 'nausea', 'vomiting', 'confusion', 'weakness'}
        if len(symptom_terms & metabolic_indicators) >= 3:
            if 'kidney' in health_lower or 'renal' in health_lower:
                if 'metformin' in drug_lower:
                    risks['Metabolic'] = {
                        'level': 'CRITICAL',
                        'condition': 'Metformin-Associated Lactic Acidosis (MALA)',
                        'reasoning': 'Triad of GI symptoms, muscle pain, and respiratory distress in patient with renal impairment',
                        'action': 'IMMEDIATE: Check serum lactate, ABG, renal function. Discontinue metformin.',
                        'mortality': 'High (30-50% if untreated)'
                    }
        
        # Rhabdomyolysis risk (statins)
        if 'myalgia' in symptom_terms and 'dark urine' in ' '.join(symptom_terms):
            if 'statin' in drug_lower or 'atorvastatin' in drug_lower or 'simvastatin' in drug_lower:
                risks['Musculoskeletal'] = {
                    'level': 'HIGH',
                    'condition': 'Statin-Induced Rhabdomyolysis',
                    'reasoning': 'Muscle pain with dark urine (myoglobinuria) indicates muscle breakdown',
                    'action': 'URGENT: Check CK, creatinine, myoglobin. Discontinue statin. IV fluids.',
                    'complications': 'Acute kidney injury, compartment syndrome, DIC'
                }
        
        # Cardiac risks
        cardiac_symptoms = {'chest pain', 'palpitations', 'dyspnea', 'edema'}
        if len(symptom_terms & cardiac_symptoms) >= 2:
            risks['Cardiac'] = {
                'level': 'HIGH',
                'condition': 'Cardiac adverse event',
                'reasoning': 'Multiple cardiac symptoms suggesting myocardial or arrhythmic event',
                'action': 'URGENT: ECG, troponin, BNP. Cardiology consultation.',
                'differential': ['Drug-induced arrhythmia', 'ACS', 'Heart failure exacerbation']
            }
        
        # Renal risks
        if 'kidney' in health_lower or 'renal' in health_lower:
            if patient.days_taken > 60:
                risks['Renal'] = {
                    'level': 'HIGH',
                    'condition': 'Drug accumulation with renal impairment',
                    'reasoning': f'Pre-existing renal disease with prolonged exposure ({patient.days_taken} days)',
                    'action': 'Check eGFR, drug levels if available. Dose adjustment or discontinuation.',
                    'note': 'Many drugs require renal dose adjustment or are contraindicated in CKD'
                }
        
        # Hepatotoxicity
        if 'abdominal pain' in symptom_terms and patient.days_taken > 30:
            risks['Hepatic'] = {
                'level': 'MODERATE',
                'condition': 'Potential hepatotoxicity',
                'reasoning': 'Abdominal pain with chronic drug exposure',
                'action': 'Check LFTs (AST, ALT, alkaline phosphatase, bilirubin)',
                'note': 'Many drugs can cause idiosyncratic liver injury'
            }
        
        # Neurological risks
        neuro_symptoms = {'confusion', 'tremor', 'dizziness', 'headache'}
        if len(symptom_terms & neuro_symptoms) >= 2:
            risks['Neurological'] = {
                'level': 'MODERATE',
                'condition': 'Central nervous system effects',
                'reasoning': 'Multiple neurological symptoms',
                'action': 'Assess mental status, consider drug-induced delirium or metabolic encephalopathy',
                'differential': ['Drug toxicity', 'Metabolic derangement', 'Cerebrovascular event']
            }
        
        # Bleeding risk
        if any(term in symptom_terms for term in ['bleeding', 'bruising', 'hemorrhage']):
            if 'warfarin' in drug_lower or 'anticoagulant' in health_lower:
                risks['Hematologic'] = {
                    'level': 'HIGH',
                    'condition': 'Anticoagulation-related bleeding',
                    'reasoning': 'Bleeding symptoms in patient on anticoagulation',
                    'action': 'URGENT: Check INR/PT, CBC. Consider reversal agents.',
                    'reversal': 'Vitamin K, PCC, or specific reversal agent depending on anticoagulant'
                }
        
        # Serotonin syndrome
        if 'ssri' in drug_lower or 'sertraline' in drug_lower or 'fluoxetine' in drug_lower:
            serotonin_symptoms = {'tremor', 'diaphoresis', 'confusion', 'agitation', 'myalgia', 'tachycardia'}
            if len(symptom_terms & serotonin_symptoms) >= 3:
                risks['Serotonin Syndrome'] = {
                    'level': 'CRITICAL',
                    'condition': 'Serotonin Syndrome',
                    'reasoning': 'Multiple symptoms suggesting serotonin excess',
                    'action': 'IMMEDIATE: Discontinue SSRI, supportive care, consider cyproheptadine',
                    'triad': 'Neuromuscular hyperactivity, autonomic hyperactivity, altered mental status'
                }
        
        return risks
    
    def calculate_overall_risk(self, symptoms: List[ExtractedSymptom], 
                              serious_risks: Dict, 
                              patient: PatientData) -> RiskLevel:
        """Calculate overall risk level"""
        # Count severity levels
        severe_count = sum(1 for s in symptoms if s.severity in [Severity.SEVERE, Severity.LIFE_THREATENING])
        moderate_count = sum(1 for s in symptoms if s.severity == Severity.MODERATE)
        
        # Check for serious risks
        critical_risks = sum(1 for r in serious_risks.values() if r.get('level') == 'CRITICAL')
        high_risks = sum(1 for r in serious_risks.values() if r.get('level') == 'HIGH')
        
        # Age factor
        age_risk = 1 if patient.age > 75 else 0
        
        # Duration factor
        duration_risk = 1 if patient.days_taken > 90 else 0
        
        # Calculate total risk score
        risk_score = (
            critical_risks * 10 +
            high_risks * 5 +
            severe_count * 3 +
            moderate_count * 1 +
            age_risk +
            duration_risk
        )
        
        if risk_score >= 10 or critical_risks > 0:
            return RiskLevel.CRITICAL
        elif risk_score >= 6 or high_risks > 0:
            return RiskLevel.HIGH
        elif risk_score >= 3 or severe_count > 0:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def generate_clinical_narration(self, patient: PatientData) -> Dict[str, any]:
        """Main analysis function - generates complete clinical narration"""
        
        # Extract symptoms using advanced NLP
        symptoms = self.nlp_processor.extract_symptoms_nlp(patient.stop_reason)
        
        # Analyze drug mechanisms
        mechanisms = self.analyze_drug_mechanism(patient.drug_name, symptoms, patient)
        
        # Detect serious risks
        serious_risks = self.detect_serious_risks(patient, symptoms, mechanisms)
        
        # Calculate overall risk
        overall_risk = self.calculate_overall_risk(symptoms, serious_risks, patient)
        
        # Generate narration components
        narration = self._generate_narrative_text(patient, symptoms, mechanisms, serious_risks, overall_risk)
        
        return {
            'patient_overview': narration['overview'],
            'extracted_symptoms': [
                {
                    'clinical_term': s.clinical_term,
                    'severity': s.severity.value,
                    'confidence': round(s.confidence, 2),
                    'temporal': s.temporal,
                    'frequency': s.frequency
                } for s in symptoms
            ],
            'cause_and_mechanism': narration['mechanism'],
            'severity_and_risk': narration['severity'],
            'serious_health_risks': serious_risks,
            'underlying_health_impact': narration['health_impact'],
            'clinical_narration': narration['full_narrative'],
            'overall_risk_level': overall_risk.value,
            'recommendations': narration['recommendations']
        }
    
    def _generate_narrative_text(self, patient: PatientData, symptoms: List[ExtractedSymptom],
                                 mechanisms: Dict, serious_risks: Dict, 
                                 overall_risk: RiskLevel) -> Dict[str, str]:
        """Generate comprehensive narrative text"""
        
        # Patient Overview
        overview = (
            f"Patient ID {patient.record_id}: {patient.age}-year-old {patient.gender} "
            f"with history of {patient.health_issues}. "
            f"Initiated {patient.drug_name} on {patient.start_date}, discontinued on {patient.stop_date} "
            f"after {patient.days_taken} days due to adverse effects."
        )
        
        # Extracted Symptoms Summary
        symptom_list = ", ".join([s.clinical_term for s in symptoms])
        severe_symptoms = [s for s in symptoms if s.severity in [Severity.SEVERE, Severity.LIFE_THREATENING]]
        
        # Mechanism Explanation
        if mechanisms.get('drug_class'):
            mech_text = (
                f"{patient.drug_name} is a {mechanisms['drug_class']}. "
                f"Mechanism of action: {mechanisms['primary_mechanism']}. "
            )
            if mechanisms.get('symptom_specific'):
                mech_text += "Symptom-specific mechanisms: " + "; ".join(mechanisms['symptom_specific'][:2]) + ". "
        else:
            mech_text = f"The pharmacological mechanism of {patient.drug_name} requires further investigation. "
        
        # Severity Assessment
        severity_text = f"Analysis revealed {len(symptoms)} distinct adverse effects: {symptom_list}. "
        if severe_symptoms:
            severe_terms = ", ".join([s.clinical_term for s in severe_symptoms])
            severity_text += f"Notably, severe manifestations include: {severe_terms}. "
        
        # Serious Risks
        if serious_risks:
            risk_conditions = [r['condition'] for r in serious_risks.values()]
            severity_text += f"Critical findings suggest possible {', '.join(risk_conditions)}. "
        
        # Health Impact
        health_impact = (
            f"Patient's pre-existing condition ({patient.health_issues}) likely exacerbated drug toxicity. "
        )
        
        if mechanisms.get('risk_factors_present'):
            health_impact += (
                f"Risk factors identified: {', '.join(mechanisms['risk_factors_present'])}. "
                f"These comorbidities increase susceptibility to adverse drug reactions through "
                f"altered pharmacokinetics and pharmacodynamics. "
            )
        
        if patient.age > 65:
            health_impact += (
                f"Advanced age ({patient.age} years) contributes to reduced drug clearance, "
                f"polypharmacy risks, and heightened sensitivity to adverse effects. "
            )
        
        # Duration Impact
        if patient.days_taken > 60:
            health_impact += (
                f"Extended exposure duration ({patient.days_taken} days) suggests cumulative "
                f"toxicity or delayed-onset adverse reaction. "
            )
        
        # Full Clinical Narrative
        full_narrative = (
            f"This {patient.age}-year-old {patient.gender} with {patient.health_issues} "
            f"experienced {len(symptoms)} clinically significant adverse effects following "
            f"{patient.days_taken} days of {patient.drug_name} therapy. "
        )
        
        if severe_symptoms:
            full_narrative += (
                f"The presentation includes severe manifestations ({', '.join([s.clinical_term for s in severe_symptoms])}), "
                f"warranting immediate clinical attention. "
            )
        
        full_narrative += mech_text
        
        if serious_risks:
            critical_risks = [r for r in serious_risks.values() if r.get('level') == 'CRITICAL']
            high_risks = [r for r in serious_risks.values() if r.get('level') == 'HIGH']
            
            if critical_risks:
                full_narrative += (
                    f"CRITICAL: {critical_risks[0]['condition']} suspected. "
                    f"{critical_risks[0]['reasoning']}. "
                )
            elif high_risks:
                full_narrative += (
                    f"HIGH RISK: {high_risks[0]['condition']} possible. "
                    f"{high_risks[0]['reasoning']}. "
                )
        
        full_narrative += (
            f"The patient's baseline comorbidities and age ({patient.age} years) "
            f"significantly compound the adverse event severity. "
        )
        
        # Recommendations
        recommendations = []
        
        if overall_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append("IMMEDIATE DISCONTINUATION of medication required")
            recommendations.append("Emergency medical evaluation recommended")
        else:
            recommendations.append("Consider medication discontinuation or dose adjustment")
            recommendations.append("Close clinical monitoring advised")
        
        if serious_risks:
            for risk_name, risk_data in serious_risks.items():
                if risk_data.get('action'):
                    recommendations.append(f"{risk_name}: {risk_data['action']}")
        
        recommendations.append("Document adverse event in patient record")
        recommendations.append("Report to pharmacovigilance database (FDA MedWatch or equivalent)")
        recommendations.append("Consider alternative therapeutic options")
        
        if mechanisms.get('risk_factors_present'):
            recommendations.append(
                "Future prescribing should account for identified risk factors: " + 
                ", ".join(mechanisms['risk_factors_present'])
            )
        
        return {
            'overview': overview,
            'mechanism': mech_text,
            'severity': severity_text,
            'health_impact': health_impact,
            'full_narrative': full_narrative,
            'recommendations': recommendations
        }


# ==================== MAIN EXECUTION ====================

def format_output(result: Dict) -> str:
    """Format the analysis result for display"""
    output = []
    output.append("\n" + "="*80)
    output.append("CLINICAL PHARMACOVIGILANCE ANALYSIS REPORT")
    output.append("="*80)
    
    # Patient Overview
    output.append("\n📋 PATIENT OVERVIEW:")
    output.append("-" * 80)
    output.append(result['patient_overview'])
    
    # Extracted Symptoms
    output.append("\n\n🔍 EXTRACTED SYMPTOMS (NLP Analysis):")
    output.append("-" * 80)
    for i, symptom in enumerate(result['extracted_symptoms'], 1):
        output.append(f"\n{i}. {symptom['clinical_term']}")
        output.append(f"   Severity: {symptom['severity']}")
        output.append(f"   Confidence: {symptom['confidence']:.0%}")
        if symptom['temporal']:
            output.append(f"   Temporal: {symptom['temporal']}")
        if symptom['frequency']:
            output.append(f"   Frequency: {symptom['frequency']}")
    
    # Cause & Mechanism
    output.append("\n\n⚗️  CAUSE & MECHANISM:")
    output.append("-" * 80)
    output.append(result['cause_and_mechanism'])
    
    # Severity & Risk Assessment
    output.append("\n\n⚠️  SEVERITY & RISK ASSESSMENT:")
    output.append("-" * 80)
    output.append(result['severity_and_risk'])
    
    # Serious Health Risks
    if result['serious_health_risks']:
        output.append("\n\n🚨 SERIOUS HEALTH RISKS DETECTED:")
        output.append("-" * 80)
        for risk_name, risk_data in result['serious_health_risks'].items():
            output.append(f"\n⚠️  {risk_name.upper()} [{risk_data['level']}]")
            output.append(f"   Condition: {risk_data['condition']}")
            output.append(f"   Reasoning: {risk_data['reasoning']}")
            output.append(f"   Action: {risk_data['action']}")
            if 'mortality' in risk_data:
                output.append(f"   Mortality Risk: {risk_data['mortality']}")
            if 'complications' in risk_data:
                output.append(f"   Complications: {risk_data['complications']}")
    
    # Underlying Health Impact
    output.append("\n\n🏥 UNDERLYING HEALTH IMPACT:")
    output.append("-" * 80)
    output.append(result['underlying_health_impact'])
    
    # Final Clinical Narration
    output.append("\n\n📝 FINAL CLINICAL NARRATION:")
    output.append("-" * 80)
    output.append(result['clinical_narration'])
    
    # Overall Risk Level
    output.append("\n\n🎯 OVERALL RISK LEVEL:")
    output.append("-" * 80)
    risk_emoji = {
        'Low': '🟢',
        'Moderate': '🟡',
        'High': '🟠',
        'Critical': '🔴'
    }
    output.append(f"{risk_emoji.get(result['overall_risk_level'], '⚪')} {result['overall_risk_level'].upper()}")
    
    # Recommendations
    output.append("\n\n💊 RECOMMENDATIONS:")
    output.append("-" * 80)
    for i, rec in enumerate(result['recommendations'], 1):
        output.append(f"{i}. {rec}")
    
    output.append("\n" + "="*80)
    output.append("End of Report")
    output.append("="*80 + "\n")
    
    return "\n".join(output)


def main():
    """Main execution function with example cases"""
    
    print("Initializing Clinical NLP Narration System...")
    narrator = ClinicalNLPNarrator()
    print("✓ System ready\n")
    
    # Example Case 1: Metformin with severe GI symptoms and lactic acidosis risk
    patient1 = PatientData(
        record_id="PT-2024-001",
        age=72,
        gender="Male",
        drug_name="Metformin 1000mg",
        health_issues="Type 2 Diabetes Mellitus, Chronic Kidney Disease Stage 3, Hypertension",
        start_date="2024-10-01",
        stop_date="2024-12-15",
        days_taken=75,
        stop_reason="Severe nausea and vomiting for past 5 days, extreme weakness, shortness of breath, muscle pain, confusion. Can't keep food down. Multiple episodes of vomiting daily."
    )
    
    # Example Case 2: Statin-induced myopathy
    patient2 = PatientData(
        record_id="PT-2024-002",
        age=68,
        gender="Female",
        drug_name="Atorvastatin 40mg",
        health_issues="Hyperlipidemia, Coronary Artery Disease",
        start_date="2024-09-15",
        stop_date="2024-11-20",
        days_taken=66,
        stop_reason="Severe muscle pain in thighs and calves, extreme weakness, dark colored urine noticed yesterday. Pain is constant and unbearable."
    )
    
    # Example Case 3: SSRI side effects
    patient3 = PatientData(
        record_id="PT-2024-003",
        age=45,
        gender="Female",
        drug_name="Sertraline 100mg",
        health_issues="Major Depressive Disorder, Anxiety",
        start_date="2024-11-01",
        stop_date="2024-12-10",
        days_taken=39,
        stop_reason="Persistent nausea, can't sleep at night, trembling hands, excessive sweating, dizziness. Symptoms getting worse over the last week."
    )
    
    # Analyze all cases
    cases = [patient1, patient2, patient3]
    
    for patient in cases:
        print(f"\nAnalyzing {patient.record_id}...")
        result = narrator.generate_clinical_narration(patient)
        formatted_output = format_output(result)
        print(formatted_output)
        
        # Optional: Save to file
        filename = f"clinical_report_{patient.record_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        print(f"📄 Report saved to: {filename}")


if __name__ == "__main__":
    main()