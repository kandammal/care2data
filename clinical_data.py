"""
Advanced Clinical NLP Narration System with Medical NLP Models
Uses spaCy, scispaCy, Transformers for sophisticated medical text analysis
"""

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
            serotonin_symptoms = {'tremor', 'diaphoresis',