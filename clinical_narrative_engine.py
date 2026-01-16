"""
Clinical Narrative Generator using Groq LLM
Generates pharmacovigilance-style adverse event narratives
"""

import os
from typing import Dict
from datetime import datetime
from dataclasses import dataclass
from groq import Groq


@dataclass
class ClinicalNarrative:
    """Structure for generated clinical narrative"""
    patient_id: str
    drug_name: str
    duration_days: int
    stop_reason: str
    narrative: str
    probable_syndrome: str
    mechanism: str
    seriousness_level: str
    causality_category: str
    clinical_advice: str
    generated_at: str


class ClinicalNarrativeGenerator:
    """
    Generates pharmacovigilance-grade clinical narratives using Groq LLM
    """
    
    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize narrative generator
        
        Args:
            groq_api_key: Groq API key
            model: Groq model to use
        """
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = model
    
    def build_prompt(
        self,
        patient_id: str,
        age: int,
        gender: str,
        drug_name: str,
        days: int,
        stop_reason: str,
        retrieved_context: str
    ) -> str:
        """
        Build pharmacovigilance prompt for Groq LLM
        
        Args:
            patient_id: Patient ID
            age: Patient age
            gender: Patient gender
            drug_name: Drug name
            days: Duration in days
            stop_reason: Reason for stopping
            retrieved_context: RAG retrieved medical knowledge
            
        Returns:
            Complete prompt
        """
        prompt = f"""You are a Senior Pharmacovigilance Physician AI with expertise in adverse drug reaction analysis.

ROLE:
You MUST analyze this adverse drug reaction case using ONLY the retrieved medical knowledge provided below.
Generate a structured, evidence-based clinical safety narrative following ICH E2B pharmacovigilance standards.

CASE DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient ID: {patient_id}
Age: {age} years
Gender: {gender}
Drug: {drug_name}
Treatment Duration: {days} days
Stop Reason: {stop_reason}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RETRIEVED MEDICAL KNOWLEDGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{retrieved_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTRUCTIONS:
Generate a comprehensive pharmacovigilance narrative with the following sections:

1. CASE SUMMARY
   - Describe the temporal association between drug exposure and symptom onset
   - Include patient demographics and relevant risk factors
   - State the clinical presentation clearly

2. MECHANISTIC EXPLANATION
   - Explain the pharmacological mechanism linking the drug to the adverse event
   - Reference specific pathways (e.g., enzyme inhibition, receptor effects, metabolic pathways)
   - Discuss dose-duration relationship if relevant

3. SYNDROME CORRELATION
   - Identify the most probable adverse drug reaction syndrome
   - Explain why this syndrome best fits the clinical picture
   - Reference diagnostic criteria or clinical markers from retrieved knowledge

4. RISK STRATIFICATION
   - Analyze age-related risk factors
   - Discuss organ function implications (hepatic, renal, cardiac)
   - Assess drug accumulation or interaction potential
   - Identify patient-specific vulnerabilities

5. SERIOUSNESS ASSESSMENT
   - Classify severity: Mild / Moderate / Severe / Life-Threatening
   - Assess hospitalization requirement likelihood
   - Evaluate potential for permanent disability or mortality
   - Justify your classification with medical reasoning

6. REGULATORY CAUSALITY ASSESSMENT
   - Apply WHO-UMC causality categories:
     * Certain: Event follows plausible temporal sequence, cannot be explained by other factors
     * Probable/Likely: Event follows reasonable temporal sequence, unlikely due to other factors
     * Possible: Event follows reasonable temporal sequence, could be explained by other factors
     * Unlikely: Temporal relationship makes causality improbable
   - Provide justification for your category selection

7. CLINICAL RECOMMENDATIONS
   - Specify monitoring parameters and frequency
   - Recommend drug discontinuation or dose adjustment
   - Suggest alternative therapy options if appropriate
   - Outline follow-up requirements

CRITICAL REQUIREMENTS:
• Use ONLY information from the retrieved medical knowledge above
• NO hallucinations or unsupported claims
• Use cautious, medically conservative language
• Phrase conclusions as "probable", "suggestive of", "consistent with"
• Do NOT provide definitive diagnosis
• Do NOT replace clinical judgment
• Follow pharmacovigilance terminology
• Be thorough but concise
• Use medical terminology appropriately

OUTPUT FORMAT:
Generate the narrative as structured paragraphs under each section heading.
Be specific, evidence-based, and clinically relevant.

Begin your response now:"""
        
        return prompt
    
    def generate_narrative(
        self,
        patient_id: str,
        age: int,
        gender: str,
        drug_name: str,
        days: int,
        stop_reason: str,
        retrieved_context: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> ClinicalNarrative:
        """
        Generate clinical narrative using Groq LLM
        
        Args:
            patient_id: Patient ID
            age: Patient age
            gender: Patient gender
            drug_name: Drug name
            days: Duration
            stop_reason: Stop reason
            retrieved_context: RAG context
            temperature: LLM temperature
            max_tokens: Max tokens
            
        Returns:
            ClinicalNarrative object
        """
        print(f"\n🤖 Generating clinical narrative using {self.model}...")
        
        # Build prompt
        prompt = self.build_prompt(
            patient_id, age, gender, drug_name, days, stop_reason, retrieved_context
        )
        
        # Call Groq LLM
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior Pharmacovigilance Physician AI specializing in adverse drug reaction analysis. You provide evidence-based, conservative clinical assessments following ICH E2B standards."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        narrative_text = response.choices[0].message.content
        
        print("✅ Narrative generated successfully!\n")
        
        # Extract structured fields (simple parsing)
        syndrome = self._extract_field(narrative_text, ["SYNDROME CORRELATION", "Probable Syndrome"])
        mechanism = self._extract_field(narrative_text, ["MECHANISTIC EXPLANATION", "Mechanism"])
        seriousness = self._extract_field(narrative_text, ["SERIOUSNESS ASSESSMENT", "Severity"])
        causality = self._extract_field(narrative_text, ["CAUSALITY ASSESSMENT", "Causality"])
        advice = self._extract_field(narrative_text, ["CLINICAL RECOMMENDATIONS", "Recommendations"])
        
        # Create structured narrative object
        narrative = ClinicalNarrative(
            patient_id=patient_id,
            drug_name=drug_name,
            duration_days=days,
            stop_reason=stop_reason,
            narrative=narrative_text,
            probable_syndrome=syndrome,
            mechanism=mechanism,
            seriousness_level=seriousness,
            causality_category=causality,
            clinical_advice=advice,
            generated_at=datetime.now().isoformat()
        )
        
        return narrative
    
    def _extract_field(self, text: str, keywords: list) -> str:
        """Extract field from narrative text"""
        for keyword in keywords:
            if keyword in text:
                # Simple extraction - get first sentence after keyword
                start = text.find(keyword)
                if start != -1:
                    section = text[start:start+500]
                    sentences = section.split('.')
                    if len(sentences) > 1:
                        return sentences[1].strip()[:200]
        return "See full narrative"
    
    def format_report(self, narrative: ClinicalNarrative) -> str:
        """
        Format narrative as downloadable text report
        
        Args:
            narrative: ClinicalNarrative object
            
        Returns:
            Formatted report string
        """
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          ADVERSE DRUG REACTION CLINICAL ASSESSMENT REPORT                  ║
║                 AI-Generated Pharmacovigilance Narrative                   ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

REPORT METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {narrative.generated_at}
System: AI-Powered RAG Clinical Narrative Generator
Model: Groq Llama3-70B with Medical Knowledge Retrieval


CASE IDENTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient ID:        {narrative.patient_id}
Drug Implicated:   {narrative.drug_name}
Treatment Duration: {narrative.duration_days} days
Adverse Event:     {narrative.stop_reason}


CLINICAL NARRATIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{narrative.narrative}


SUMMARY ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Probable Syndrome:
{narrative.probable_syndrome}

Mechanistic Pathway:
{narrative.mechanism}

Seriousness Level:
{narrative.seriousness_level}

Causality Category (WHO-UMC):
{narrative.causality_category}

Clinical Recommendations:
{narrative.clinical_advice}


DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This AI-generated narrative is a clinical decision support tool and does NOT
constitute medical diagnosis or treatment advice. All cases should be reviewed
by qualified healthcare professionals. This system uses retrieval-augmented
generation with evidence-based medical knowledge but cannot replace clinical
judgment.

Follow institutional protocols for adverse event reporting and patient management.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


End of Report
"""
        return report
    
    def save_report(self, narrative: ClinicalNarrative, output_dir: str = "reports") -> str:
        """
        Save report to file
        
        Args:
            narrative: ClinicalNarrative object
            output_dir: Output directory
            
        Returns:
            File path
        """
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"clinical_report_{narrative.patient_id}.txt"
        filepath = os.path.join(output_dir, filename)
        
        report = self.format_report(narrative)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"💾 Report saved: {filepath}")
        
        return filepath


def test_generator():
    """Test the narrative generator"""
    
    print("=" * 70)
    print("🧪 TESTING CLINICAL NARRATIVE GENERATOR")
    print("=" * 70)
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")
    
    if GROQ_API_KEY == "your-groq-api-key":
        print("\n⚠️  Set GROQ_API_KEY environment variable")
        return
    
    generator = ClinicalNarrativeGenerator(groq_api_key=GROQ_API_KEY)
    
    # Mock retrieved context
    mock_context = """
[Drug Knowledge 1] Atorvastatin - MECHANISM OF ACTION
Competitive inhibition of HMG-CoA reductase, depletes coenzyme Q10 and 
impairs mitochondrial function in myocytes.

[Drug Knowledge 2] Atorvastatin - SERIOUS ADVERSE EFFECTS
Rhabdomyolysis, myopathy, elevated CK levels

[Syndrome Knowledge 1] Statin-Induced Rhabdomyolysis
Severe muscle pain, muscle weakness, dark urine. CK > 10x ULN.
Risk factors: elderly, renal impairment.
"""
    
    narrative = generator.generate_narrative(
        patient_id="PT-2024-TEST",
        age=68,
        gender="Male",
        drug_name="Atorvastatin",
        days=45,
        stop_reason="Severe muscle pain",
        retrieved_context=mock_context
    )
    
    # Display and save
    report = generator.format_report(narrative)
    print(report)
    
    generator.save_report(narrative)
    
    print("\n✅ Narrative generation test complete!")


if __name__ == "__main__":
    test_generator()
