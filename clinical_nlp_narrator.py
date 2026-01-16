"""
Clinical NLP Narration System
An advanced Clinical Natural Language Processing and Pharmacovigilance Analysis Model
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime
from enum import Enum


class SeverityLevel(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    LIFE_THREATENING = "Life-Threatening"


class RiskLevel(Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskCategory(Enum):
    ORGAN_TOXICITY = "Organ Toxicity"
    CARDIAC_RISK = "Cardiac Risk"
    NEUROLOGICAL_RISK = "Neurological Risk"
    RESPIRATORY_RISK = "Respiratory Risk"
    METABOLIC_RISK = "Metabolic Risk"


@dataclass
class PatientData:
    """Structure for patient clinical data"""
    record_id: str
    age: int
    gender: str
    drug_name: str
    health_issue: str
    drug_start_date: str
    drug_stop_date: str
    days_taken: int
    stop_reason: str


@dataclass
class Symptom:
    """Structure for extracted symptoms"""
    raw_text: str
    normalized_term: str
    severity: SeverityLevel
    cause: str
    risk_categories: List[RiskCategory]


class ClinicalNLPNarrator:
    """
    Advanced Clinical NLP and Pharmacovigilance Analysis Model
    """
    
    def __init__(self):
        # Symptom dictionaries for NLP extraction and normalization
        self.symptom_keywords = {
            # Gastrointestinal
            'nausea': 'Nausea',
            'vomiting': 'Vomiting',
            'diarrhea': 'Diarrhea',
            'constipation': 'Constipation',
            'abdominal pain': 'Abdominal Pain',
            'stomach pain': 'Abdominal Pain',
            'stomach upset': 'Gastric Distress',
            'indigestion': 'Dyspepsia',
            
            # Neurological
            'headache': 'Headache',
            'dizziness': 'Dizziness',
            'vertigo': 'Vertigo',
            'confusion': 'Confusion',
            'drowsiness': 'Somnolence',
            'fatigue': 'Fatigue',
            'tremor': 'Tremor',
            'seizure': 'Seizure',
            'numbness': 'Paresthesia',
            'tingling': 'Paresthesia',
            
            # Cardiovascular
            'chest pain': 'Chest Pain',
            'palpitation': 'Palpitations',
            'rapid heart': 'Tachycardia',
            'irregular heartbeat': 'Arrhythmia',
            'high blood pressure': 'Hypertension',
            'low blood pressure': 'Hypotension',
            
            # Respiratory
            'shortness of breath': 'Dyspnea',
            'breathing difficulty': 'Dyspnea',
            'cough': 'Cough',
            'wheezing': 'Wheezing',
            
            # Dermatological
            'rash': 'Rash',
            'itching': 'Pruritus',
            'hives': 'Urticaria',
            'swelling': 'Edema',
            
            # Hepatic
            'jaundice': 'Jaundice',
            'yellow skin': 'Jaundice',
            'liver pain': 'Hepatic Pain',
            
            # Renal
            'decreased urination': 'Oliguria',
            'kidney pain': 'Renal Pain',
            
            # Musculoskeletal
            'muscle pain': 'Myalgia',
            'joint pain': 'Arthralgia',
            'weakness': 'Asthenia',
            
            # Psychiatric
            'anxiety': 'Anxiety',
            'depression': 'Depression',
            'insomnia': 'Insomnia',
            'nightmares': 'Nightmares',
            
            # Metabolic
            'weight gain': 'Weight Gain',
            'weight loss': 'Weight Loss',
            'increased appetite': 'Increased Appetite',
            'decreased appetite': 'Decreased Appetite',
        }
        
        # Severity indicators
        self.severity_keywords = {
            SeverityLevel.LIFE_THREATENING: ['collapse', 'unconscious', 'severe bleeding', 'unable to breathe', 
                                             'chest crushing', 'seizure', 'anaphylaxis'],
            SeverityLevel.SEVERE: ['severe', 'extreme', 'unbearable', 'intense', 'hospitalized', 'emergency'],
            SeverityLevel.MODERATE: ['moderate', 'significant', 'concerning', 'persistent', 'worsening'],
            SeverityLevel.MILD: ['mild', 'slight', 'minor', 'occasional', 'tolerable']
        }
        
        # Risk category mapping
        self.risk_mapping = {
            'Jaundice': [RiskCategory.ORGAN_TOXICITY],
            'Hepatic Pain': [RiskCategory.ORGAN_TOXICITY],
            'Renal Pain': [RiskCategory.ORGAN_TOXICITY],
            'Oliguria': [RiskCategory.ORGAN_TOXICITY],
            'Chest Pain': [RiskCategory.CARDIAC_RISK],
            'Palpitations': [RiskCategory.CARDIAC_RISK],
            'Tachycardia': [RiskCategory.CARDIAC_RISK],
            'Arrhythmia': [RiskCategory.CARDIAC_RISK],
            'Seizure': [RiskCategory.NEUROLOGICAL_RISK],
            'Confusion': [RiskCategory.NEUROLOGICAL_RISK],
            'Tremor': [RiskCategory.NEUROLOGICAL_RISK],
            'Vertigo': [RiskCategory.NEUROLOGICAL_RISK],
            'Dyspnea': [RiskCategory.RESPIRATORY_RISK],
            'Wheezing': [RiskCategory.RESPIRATORY_RISK],
            'Weight Gain': [RiskCategory.METABOLIC_RISK],
            'Weight Loss': [RiskCategory.METABOLIC_RISK],
        }
    
    def extract_symptoms(self, stop_reason: str) -> List[str]:
        """Extract symptoms from unstructured text using NLP"""
        stop_reason_lower = stop_reason.lower()
        extracted = []
        
        for keyword, normalized_term in self.symptom_keywords.items():
            if keyword in stop_reason_lower:
                if normalized_term not in extracted:
                    extracted.append(normalized_term)
        
        return extracted
    
    def classify_severity(self, stop_reason: str, symptom: str, age: int, 
                         days_taken: int, health_issue: str) -> SeverityLevel:
        """Classify severity of a symptom"""
        stop_reason_lower = stop_reason.lower()
        
        # Check for life-threatening indicators
        for keyword in self.severity_keywords[SeverityLevel.LIFE_THREATENING]:
            if keyword in stop_reason_lower:
                return SeverityLevel.LIFE_THREATENING
        
        # Age-based severity escalation
        severity_modifier = 0
        if age > 65 or age < 12:
            severity_modifier += 1
        
        # Duration-based severity
        if days_taken > 90:
            severity_modifier += 1
        
        # Check explicit severity keywords
        for keyword in self.severity_keywords[SeverityLevel.SEVERE]:
            if keyword in stop_reason_lower:
                return SeverityLevel.SEVERE
        
        for keyword in self.severity_keywords[SeverityLevel.MODERATE]:
            if keyword in stop_reason_lower:
                return SeverityLevel.MODERATE if severity_modifier == 0 else SeverityLevel.SEVERE
        
        # Default classification
        if severity_modifier >= 2:
            return SeverityLevel.SEVERE
        elif severity_modifier == 1:
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.MILD
    
    def determine_cause(self, symptom: str, drug_name: str) -> str:
        """Determine pharmacological cause of symptom"""
        # This is a simplified version - in production, this would query a drug database
        cause_templates = {
            'Nausea': f"{drug_name} may irritate gastric mucosa or affect the chemoreceptor trigger zone in the medulla",
            'Vomiting': f"{drug_name} stimulates the vomiting center via dopaminergic or serotonergic pathways",
            'Diarrhea': f"{drug_name} may alter gut motility or disrupt intestinal microbiome balance",
            'Headache': f"{drug_name} may cause cerebral vasodilation or affect neurotransmitter balance",
            'Dizziness': f"{drug_name} may affect vestibular function or cause orthostatic hypotension",
            'Fatigue': f"{drug_name} may interfere with cellular energy metabolism or neurotransmitter regulation",
            'Rash': f"{drug_name} triggered a Type IV hypersensitivity reaction or direct skin irritation",
            'Tachycardia': f"{drug_name} may have sympathomimetic effects or interfere with cardiac conduction",
            'Dyspnea': f"{drug_name} may cause bronchospasm or pulmonary edema through various mechanisms",
            'Jaundice': f"{drug_name} likely caused hepatocellular injury or cholestasis affecting bilirubin metabolism",
        }
        
        return cause_templates.get(symptom, 
            f"{drug_name} caused {symptom} through drug-specific pharmacological mechanisms")
    
    def identify_risk_categories(self, symptom: str) -> List[RiskCategory]:
        """Identify serious health risk categories"""
        return self.risk_mapping.get(symptom, [])
    
    def analyze_duration_impact(self, days_taken: int, symptoms: List[str]) -> str:
        """Analyze how duration contributed to symptoms"""
        if days_taken < 7:
            return "Acute adverse reaction occurred within the first week, suggesting immediate drug sensitivity or allergic response."
        elif days_taken < 30:
            return "Subacute reaction developed within the first month, indicating early drug accumulation or sensitization."
        elif days_taken < 90:
            return "Symptoms emerged after chronic exposure, suggesting cumulative drug effects or gradual organ stress."
        else:
            return "Long-term chronic exposure led to delayed adverse reactions, possibly indicating cumulative toxicity, organ dysfunction, or metabolic adaptation failure."
    
    def calculate_overall_risk(self, symptoms: List[Symptom], age: int, 
                              health_issue: str, days_taken: int) -> RiskLevel:
        """Calculate overall risk level"""
        risk_score = 0
        
        # Severity-based scoring
        for symptom in symptoms:
            if symptom.severity == SeverityLevel.LIFE_THREATENING:
                risk_score += 10
            elif symptom.severity == SeverityLevel.SEVERE:
                risk_score += 5
            elif symptom.severity == SeverityLevel.MODERATE:
                risk_score += 2
            else:
                risk_score += 1
        
        # Risk category penalties
        all_risks = []
        for symptom in symptoms:
            all_risks.extend(symptom.risk_categories)
        
        if RiskCategory.ORGAN_TOXICITY in all_risks:
            risk_score += 5
        if RiskCategory.CARDIAC_RISK in all_risks:
            risk_score += 4
        if RiskCategory.NEUROLOGICAL_RISK in all_risks:
            risk_score += 3
        
        # Age and comorbidity modifiers
        if age > 65 or age < 12:
            risk_score += 2
        
        if any(term in health_issue.lower() for term in ['heart', 'cardiac', 'liver', 'kidney', 'renal']):
            risk_score += 3
        
        # Duration modifier
        if days_taken > 180:
            risk_score += 2
        
        # Calculate final risk level
        if risk_score >= 15:
            return RiskLevel.CRITICAL
        elif risk_score >= 10:
            return RiskLevel.HIGH
        elif risk_score >= 5:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def generate_clinical_narration(self, patient: PatientData) -> Dict[str, str]:
        """
        Main function to generate complete clinical narration
        """
        # Extract symptoms
        extracted_symptom_names = self.extract_symptoms(patient.stop_reason)
        
        # Create detailed symptom objects
        symptoms: List[Symptom] = []
        for symptom_name in extracted_symptom_names:
            severity = self.classify_severity(
                patient.stop_reason, 
                symptom_name, 
                patient.age, 
                patient.days_taken, 
                patient.health_issue
            )
            cause = self.determine_cause(symptom_name, patient.drug_name)
            risk_cats = self.identify_risk_categories(symptom_name)
            
            symptoms.append(Symptom(
                raw_text=symptom_name,
                normalized_term=symptom_name,
                severity=severity,
                cause=cause,
                risk_categories=risk_cats
            ))
        
        # Duration impact
        duration_analysis = self.analyze_duration_impact(patient.days_taken, extracted_symptom_names)
        
        # Calculate overall risk
        overall_risk = self.calculate_overall_risk(symptoms, patient.age, patient.health_issue, patient.days_taken)
        
        # Generate narrative sections
        output = {}
        
        # 1. Patient Overview
        output['Patient Overview'] = (
            f"Record ID: {patient.record_id}\n"
            f"Demographics: {patient.age}-year-old {patient.gender}\n"
            f"Diagnosis/Comorbidities: {patient.health_issue}\n"
            f"Medication: {patient.drug_name}\n"
            f"Treatment Duration: {patient.days_taken} days (from {patient.drug_start_date} to {patient.drug_stop_date})\n"
            f"Discontinuation Reason: {patient.stop_reason}"
        )
        
        # 2. Extracted Symptoms
        if symptoms:
            symptom_list = "\n".join([f"- {s.normalized_term} ({s.severity.value})" for s in symptoms])
            output['Extracted Symptoms'] = symptom_list
        else:
            output['Extracted Symptoms'] = "No specific clinical symptoms detected in the stop reason text."
        
        # 3. Cause & Mechanism
        if symptoms:
            causes = "\n\n".join([f"• {s.normalized_term}:\n  {s.cause}" for s in symptoms])
            output['Cause & Mechanism'] = causes
        else:
            output['Cause & Mechanism'] = "Insufficient symptom data for mechanistic analysis."
        
        # 4. Severity & Risk Assessment
        severity_assessment = ""
        if symptoms:
            for s in symptoms:
                severity_assessment += f"\n• {s.normalized_term}: {s.severity.value}"
                if s.risk_categories:
                    risks = ", ".join([r.value for r in s.risk_categories])
                    severity_assessment += f"\n  Risk Categories: {risks}"
                
                # Justification
                justification = f"\n  Justification: "
                factors = []
                if patient.age > 65:
                    factors.append("elderly age group")
                elif patient.age < 12:
                    factors.append("pediatric age group")
                if patient.days_taken > 90:
                    factors.append(f"prolonged exposure ({patient.days_taken} days)")
                if patient.health_issue.lower() != 'none':
                    factors.append(f"existing comorbidity ({patient.health_issue})")
                
                if factors:
                    justification += "; ".join(factors)
                else:
                    justification += "Based on symptom presentation and clinical context"
                
                severity_assessment += justification + "\n"
        
        output['Severity & Risk Assessment'] = severity_assessment if severity_assessment else "No severity assessment available."
        
        # 5. Underlying Health Impact
        health_impact = ""
        if patient.health_issue.lower() != 'none':
            health_impact = (
                f"The patient's underlying condition ({patient.health_issue}) significantly interacts with "
                f"the observed adverse effects. "
            )
            
            # Add specific interactions based on symptoms
            if any(s.normalized_term in ['Jaundice', 'Hepatic Pain'] for s in symptoms):
                health_impact += "Hepatic dysfunction poses elevated risk given the existing health condition. "
            
            if any(r == RiskCategory.CARDIAC_RISK for s in symptoms for r in s.risk_categories):
                health_impact += "Cardiovascular symptoms are particularly concerning given the patient's medical history. "
            
            health_impact += (
                f"Drug metabolism and clearance may be impaired, potentially contributing to adverse event severity. "
                f"Polypharmacy interactions should be considered if the patient is on concurrent medications for {patient.health_issue}."
            )
        else:
            health_impact = "Patient had no significant pre-existing conditions reported. Adverse events appear to be primarily drug-induced."
        
        output['Underlying Health Impact'] = health_impact
        
        # 6. Duration Impact Analysis
        output['Duration Impact Analysis'] = duration_analysis
        
        # 7. Final Clinical Narration
        narration = self._generate_professional_narration(patient, symptoms, duration_analysis, overall_risk)
        output['Final Clinical Narration'] = narration
        
        # 8. Overall Risk Level
        output['Overall Risk Level'] = overall_risk.value
        
        return output
    
    def _generate_professional_narration(self, patient: PatientData, 
                                        symptoms: List[Symptom], 
                                        duration_analysis: str,
                                        overall_risk: RiskLevel) -> str:
        """Generate final professional clinical narrative"""
        
        # Part 1: Observations
        observations = (
            f"A {patient.age}-year-old {patient.gender} patient with {patient.health_issue} "
            f"was prescribed {patient.drug_name} and maintained on therapy for {patient.days_taken} days. "
        )
        
        if symptoms:
            symptom_names = ", ".join([s.normalized_term for s in symptoms])
            observations += f"The patient developed {symptom_names}, leading to treatment discontinuation. "
        else:
            observations += f"Treatment was discontinued due to: {patient.stop_reason}. "
        
        # Part 2: Medical Interpretation
        interpretation = ""
        if symptoms:
            severe_symptoms = [s for s in symptoms if s.severity in [SeverityLevel.SEVERE, SeverityLevel.LIFE_THREATENING]]
            
            if severe_symptoms:
                severe_names = ", ".join([s.normalized_term for s in severe_symptoms])
                interpretation += (
                    f"The presentation of {severe_names} indicates significant drug-related toxicity. "
                )
            
            interpretation += duration_analysis + " "
            
            # Mechanism summary
            all_risks = set()
            for s in symptoms:
                all_risks.update(s.risk_categories)
            
            if all_risks:
                risk_names = ", ".join([r.value for r in all_risks])
                interpretation += f"The clinical picture suggests {risk_names.lower()}. "
            
            interpretation += (
                f"Pharmacologically, {patient.drug_name} likely triggered these adverse effects through "
                f"mechanisms including receptor modulation, metabolic interference, or direct tissue toxicity. "
            )
        
        # Part 3: Risk & Recommendation
        risk_and_rec = f"The overall risk level is assessed as {overall_risk.value}. "
        
        if overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            risk_and_rec += (
                "Immediate medical evaluation is warranted. Consider alternative therapeutic agents. "
                "Monitor for persistent or worsening symptoms. "
                "Document this adverse drug reaction in the patient's medical record and report to pharmacovigilance authorities. "
            )
        elif overall_risk == RiskLevel.MODERATE:
            risk_and_rec += (
                "Clinical monitoring is recommended. Assess for symptom resolution post-discontinuation. "
                "Consider dose adjustment or alternative therapy if treatment must be resumed. "
            )
        else:
            risk_and_rec += (
                "Symptoms are likely to resolve upon discontinuation. "
                "Patient education regarding symptom recognition is advised. "
            )
        
        # Combine all parts
        final_narration = f"{observations}\n\n{interpretation}\n\n{risk_and_rec}"
        return final_narration
    
    def format_output(self, analysis: Dict[str, str]) -> str:
        """Format the analysis output for display"""
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("CLINICAL NLP PHARMACOVIGILANCE ANALYSIS REPORT")
        output_lines.append("=" * 80)
        output_lines.append("")
        
        for section, content in analysis.items():
            output_lines.append(f"{'=' * 80}")
            output_lines.append(f"{section.upper()}")
            output_lines.append(f"{'=' * 80}")
            output_lines.append(content)
            output_lines.append("")
        
        return "\n".join(output_lines)


def main():
    """Example usage"""
    # Create analyzer instance
    analyzer = ClinicalNLPNarrator()
    
    # Example patient data
    patient = PatientData(
        record_id="PT-2026-001",
        age=68,
        gender="Female",
        drug_name="Atorvastatin",
        health_issue="Type 2 Diabetes Mellitus, Hypertension",
        drug_start_date="2025-09-15",
        drug_stop_date="2026-01-10",
        days_taken=117,
        stop_reason="Patient experienced severe muscle pain, weakness, and dark urine. Also reported persistent fatigue and confusion."
    )
    
    # Generate analysis
    print("Analyzing patient data...\n")
    analysis = analyzer.generate_clinical_narration(patient)
    
    # Display formatted output
    formatted_output = analyzer.format_output(analysis)
    print(formatted_output)
    
    # Example 2: Acute reaction
    print("\n" + "=" * 80)
    print("SECOND EXAMPLE - ACUTE ALLERGIC REACTION")
    print("=" * 80 + "\n")
    
    patient2 = PatientData(
        record_id="PT-2026-002",
        age=34,
        gender="Male",
        drug_name="Amoxicillin",
        health_issue="None",
        drug_start_date="2026-01-08",
        drug_stop_date="2026-01-11",
        days_taken=3,
        stop_reason="Severe rash all over body with intense itching and swelling of face. Patient also experienced shortness of breath."
    )
    
    analysis2 = analyzer.generate_clinical_narration(patient2)
    formatted_output2 = analyzer.format_output(analysis2)
    print(formatted_output2)


if __name__ == "__main__":
    main()
