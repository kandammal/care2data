import os

output_dir = "drug_knowledge"
os.makedirs(output_dir, exist_ok=True)
drug_knowledge = {
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

def create_drug_documents(drug_knowledge):
    for drug, details in drug_knowledge.items():
        filename = os.path.join(output_dir, f"{drug}.md")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"DRUG NAME: {drug.title()}\n")
            f.write(f"DRUG CLASS: {details.get('class', 'Unknown')}\n\n")
            
            f.write("MECHANISM OF ACTION:\n")
            for k, v in details.get('mechanism', {}).items():
                f.write(f"- {k.replace('_',' ').title()}: {v}\n")
            f.write("\n")
            
            f.write("COMMON ADVERSE EFFECTS:\n")
            for se in details.get('common_side_effects', []):
                f.write(f"- {se}\n")
            f.write("\n")
            
            f.write("SERIOUS ADVERSE EFFECTS:\n")
            for risk in details.get('serious_risks', []):
                f.write(f"- {risk}\n")
            f.write("\n")
            
            f.write("RISK FACTORS:\n")
            for rf in details.get('risk_factors', []):
                f.write(f"- {rf}\n")
            f.write("\n")
            
            if 'contraindications' in details:
                f.write("CONTRAINDICATIONS:\n")
                for c in details['contraindications']:
                    f.write(f"- {c}\n")
                f.write("\n")
            
            if 'monitoring' in details:
                f.write("MONITORING:\n")
                for m in details['monitoring']:
                    f.write(f"- {m}\n")
                f.write("\n")
        
        print(f"Created: {filename}")

create_drug_documents(drug_knowledge)
