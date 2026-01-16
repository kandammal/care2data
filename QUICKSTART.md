# 🚀 Quick Start Guide
# AI-Powered Adverse Drug Reaction Clinical Narrative Generator

## ⚡ 5-Minute Setup

### Step 1: Get API Keys (5 minutes)

1. **OpenAI API Key** (for embeddings)
   - Go to: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy: `sk-...`

2. **MongoDB Atlas** (free tier)
   - Go to: https://www.mongodb.com/cloud/atlas/register
   - Create free cluster (M0)
   - Get connection string: `mongodb+srv://...`
   - Whitelist your IP: Network Access → Add IP Address → Allow Access from Anywhere (for testing)

3. **Groq API Key** (free tier)
   - Go to: https://console.groq.com/
   - Create account
   - Get API key: `gsk_...`

### Step 2: Install Dependencies (1 minute)

```bash
cd d:\VKS\caredata
pip install -r requirements.txt
```

### Step 3: Configure Environment (1 minute)

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-key-here"
$env:MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
$env:GROQ_API_KEY="gsk_your-actual-key-here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
export GROQ_API_KEY="gsk_your-actual-key-here"
```

### Step 4: Ingest Knowledge Base (2-3 minutes)

```bash
python vector_ingestion.py
```

**Output should show:**
```
📂 Processing 5 drug files...
📂 Processing 8 syndrome files...
💾 Inserting chunks into MongoDB...
✅ Insertion complete!
```

**Copy the JSON index definition from output**

### Step 5: Create MongoDB Vector Index (2 minutes)

1. Open MongoDB Atlas → Your Cluster
2. Click **"Search"** tab
3. Click **"Create Search Index"**
4. Select **"JSON Editor"**
5. Paste the JSON from Step 4 output
6. Set Index Name: `vector_index`
7. Click **"Create"**
8. Wait ~1 minute for index to build

### Step 6: Launch Application (30 seconds)

**Option A: Streamlit UI (Recommended)**
```bash
streamlit run app_streamlit.py
```
Open browser: http://localhost:8501

**Option B: FastAPI**
```bash
python api_server.py
```
API docs: http://localhost:8000/docs

---

## 📝 Using the System

### Streamlit Web Interface

1. **Fill in patient details:**
   - Patient ID: `PT-2024-001`
   - Age: `68`
   - Gender: `Male`
   - Drug: `Atorvastatin` (dropdown)
   - Start Date: Select date
   - Stop Date: Select date
   - Stop Reason: `Muscle pain` (dropdown)

2. **Click "Generate Clinical Narrative"**

3. **Wait 15-30 seconds** for:
   - Vector search to retrieve knowledge
   - Groq LLM to generate narrative

4. **View results:**
   - Full narrative
   - Probable syndrome
   - Seriousness level
   - Causality assessment
   - Clinical recommendations

5. **Download report** as TXT file

### API Usage

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/generate-narrative" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT-2024-001",
    "age": 68,
    "gender": "Male",
    "drug_name": "Atorvastatin",
    "start_date": "2024-10-01",
    "stop_date": "2024-11-15",
    "duration_days": 45,
    "stop_reason": "Muscle pain"
  }'
```

**Python example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/generate-narrative",
    json={
        "patient_id": "PT-2024-002",
        "age": 72,
        "gender": "Female",
        "drug_name": "Warfarin",
        "start_date": "2024-09-01",
        "stop_date": "2024-10-20",
        "duration_days": 49,
        "stop_reason": "Bleeding"
    }
)

narrative = response.json()
print(narrative["narrative"])
```

---

## 🧪 Test the System

```bash
python test_suite.py
```

**Expected output:**
```
✅ PASS - Configuration
✅ PASS - Vector Ingestion
✅ PASS - RAG Retrieval
✅ PASS - Narrative Generator
✅ PASS - API Server
✅ PASS - Streamlit App
✅ PASS - Knowledge Base

Results: 7/7 tests passed
🎉 ALL TESTS PASSED!
```

---

## 🎯 Sample Test Cases

### Case 1: Statin Rhabdomyolysis
```
Patient: PT-2024-001
Age: 68, Gender: Male
Drug: Atorvastatin
Duration: 45 days
Stop Reason: Muscle pain
Expected Syndrome: Statin-Induced Rhabdomyolysis
```

### Case 2: Warfarin Bleeding
```
Patient: PT-2024-002
Age: 75, Gender: Female
Drug: Warfarin
Duration: 60 days
Stop Reason: Bleeding
Expected Syndrome: Anticoagulant Bleeding
```

### Case 3: Serotonin Syndrome
```
Patient: PT-2024-003
Age: 42, Gender: Female
Drug: Sertraline
Duration: 14 days
Stop Reason: Confusion
Expected Syndrome: Serotonin Syndrome
```

### Case 4: Metformin Lactic Acidosis
```
Patient: PT-2024-004
Age: 71, Gender: Male
Drug: Metformin
Duration: 90 days
Stop Reason: Severe nausea
Expected Syndrome: Metformin Lactic Acidosis
```

---

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt --upgrade
```

### "MongoDB connection timeout"
```
1. Check MongoDB Atlas cluster is running
2. Verify connection string is correct
3. Check Network Access in Atlas (whitelist IP)
4. Test connection: python -c "from pymongo import MongoClient; MongoClient('your-uri').admin.command('ping')"
```

### "OpenAI API error"
```
1. Verify API key is valid
2. Check account has credits
3. Try: curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### "Groq API error"
```
1. Verify API key is valid
2. Check rate limits (free tier has limits)
3. Wait a few minutes and retry
```

### "Vector index not found"
```
1. Ensure index is created in MongoDB Atlas
2. Wait 1-2 minutes for index to build
3. Verify index name is exactly: vector_index
4. Check Search tab in Atlas shows the index
```

---

## 📊 System Performance

**First-time setup:** ~10-15 minutes  
**Subsequent runs:** Instant

**Per case generation:**
- Vector search: ~200ms
- LLM generation: ~15-25 seconds
- Total: ~20-30 seconds

**Costs (approximate):**
- OpenAI embeddings: ~$0.01 per ingestion
- Groq LLM: Free tier (limited requests/day)
- MongoDB Atlas: Free M0 tier

---

## 🎓 Understanding the Output

### Narrative Sections

1. **Case Summary**: Timeline and presentation
2. **Mechanistic Explanation**: How the drug caused the event
3. **Syndrome Correlation**: Which known syndrome fits
4. **Risk Stratification**: Patient-specific risks
5. **Seriousness Assessment**: Severity classification
6. **Causality Assessment**: WHO-UMC scale (Certain/Probable/Possible/Unlikely)
7. **Clinical Recommendations**: Next steps

### Causality Categories (WHO-UMC)

- **Certain**: Event clearly caused by drug
- **Probable**: Likely caused by drug, few other explanations
- **Possible**: Could be drug, could be other factors
- **Unlikely**: Timing or evidence doesn't support drug causation

### Seriousness Levels

- **Mild**: Minor discomfort, no intervention needed
- **Moderate**: Requires monitoring or minor intervention
- **Severe**: Significant intervention, possible hospitalization
- **Life-Threatening**: Risk of death or permanent disability

---

## 🔒 Important Reminders

⚠️ **This is a CLINICAL DECISION SUPPORT tool, NOT:**
- A medical diagnosis system
- A replacement for physician judgment
- Approved for direct clinical use
- A substitute for proper medical evaluation

✅ **Always:**
- Review AI-generated narratives with qualified healthcare professionals
- Verify against original clinical data
- Follow institutional protocols
- Report serious events to regulatory authorities (FDA, EMA, etc.)

---

## 📞 Getting Help

1. **Check documentation:** `README.md`
2. **Review deployment guide:** `DEPLOYMENT.md`
3. **Run tests:** `python test_suite.py`
4. **Check logs:** Look for error messages in console
5. **API documentation:** http://localhost:8000/docs

---

## 🎉 Success Checklist

- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] MongoDB Atlas cluster created
- [ ] Vector ingestion completed
- [ ] Vector index created in Atlas
- [ ] Test suite passes (7/7)
- [ ] Streamlit app launches successfully
- [ ] Sample case generates narrative
- [ ] Report downloads correctly

**If all checked → You're ready to go! 🚀**

---

**Built for clinical AI excellence and patient safety** ❤️
