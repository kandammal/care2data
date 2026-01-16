# Deployment Guide
# AI-Powered Adverse Drug Reaction Clinical Narrative Generator

## 🚀 Deployment Options

### Option 1: Local Development

**Step 1: Setup Environment**
```bash
cd d:\VKS\caredata
pip install -r requirements.txt
```

**Step 2: Configure Environment Variables**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key"
$env:MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
$env:GROQ_API_KEY="gsk_your-key"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key"
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
export GROQ_API_KEY="gsk_your-key"
```

**Step 3: Ingest Knowledge Base**
```bash
python vector_ingestion.py
```

**Step 4: Create MongoDB Atlas Vector Index**
- Go to Atlas → Search → Create Search Index
- Use JSON from vector_ingestion.py output
- Name: `vector_index`

**Step 5: Launch Application**

Streamlit UI:
```bash
streamlit run app_streamlit.py --server.port 8501
```

FastAPI:
```bash
python api_server.py
```

---

### Option 2: Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Default command (can override)
CMD ["python", "api_server.py"]
```

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGO_URI=${MONGO_URI}
      - GROQ_API_KEY=${GROQ_API_KEY}
    command: python api_server.py
    volumes:
      - ./reports:/app/reports

  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGO_URI=${MONGO_URI}
      - GROQ_API_KEY=${GROQ_API_KEY}
    command: streamlit run app_streamlit.py --server.port 8501 --server.address 0.0.0.0
    volumes:
      - ./reports:/app/reports
```

**Deploy with Docker Compose:**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Option 3: Cloud Deployment (Azure)

**Azure App Service Deployment:**

```bash
# Login to Azure
az login

# Create resource group
az group create --name adr-narrative-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name adr-narrative-plan \
  --resource-group adr-narrative-rg \
  --sku B1 \
  --is-linux

# Create web app for API
az webapp create \
  --resource-group adr-narrative-rg \
  --plan adr-narrative-plan \
  --name adr-narrative-api \
  --runtime "PYTHON:3.11" \
  --deployment-local-git

# Configure app settings
az webapp config appsettings set \
  --resource-group adr-narrative-rg \
  --name adr-narrative-api \
  --settings OPENAI_API_KEY="sk-..." MONGO_URI="mongodb+srv://..." GROQ_API_KEY="gsk_..."

# Deploy code
git remote add azure <deployment-url>
git push azure main
```

---

### Option 4: Streamlit Cloud

**Deploy Streamlit App:**

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Add secrets in Streamlit dashboard:
   ```toml
   OPENAI_API_KEY = "sk-..."
   MONGO_URI = "mongodb+srv://..."
   GROQ_API_KEY = "gsk_..."
   ```
5. Deploy

---

## 🔐 Security Checklist

- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/TLS for production
- [ ] Implement authentication (OAuth2/JWT)
- [ ] Set up CORS policies appropriately
- [ ] Use MongoDB Atlas IP whitelist
- [ ] Enable MongoDB encryption at rest
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Regular security audits
- [ ] HIPAA compliance review (if applicable)

---

## 📊 Monitoring & Logging

**Application Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

**MongoDB Monitoring:**
- Use MongoDB Atlas built-in monitoring
- Set up alerts for:
  - High query latency
  - Connection pool exhaustion
  - Disk usage

**API Metrics:**
- Response time
- Error rates
- API key usage
- Token consumption (OpenAI, Groq)

---

## 🔄 Backup & Recovery

**MongoDB Backup:**
- Use MongoDB Atlas automated backups
- Schedule: Daily
- Retention: 7 days minimum

**Knowledge Base Version Control:**
```bash
git add drug_knowledge/ syndrome_knowledge/
git commit -m "Update medical knowledge base"
git push
```

**Report Archival:**
```bash
# Archive old reports
tar -czf reports_backup_$(date +%Y%m%d).tar.gz reports/
```

---

## 📈 Scaling Considerations

**Horizontal Scaling:**
- Deploy multiple API instances behind load balancer
- Use MongoDB Atlas auto-scaling
- Implement Redis for caching embeddings

**Performance Optimization:**
- Cache frequently accessed knowledge chunks
- Batch embedding generation
- Use connection pooling for MongoDB
- Implement async API endpoints

**Cost Optimization:**
- Monitor OpenAI API usage (embeddings)
- Monitor Groq API usage (LLM calls)
- Use MongoDB Atlas M10+ for production
- Implement request caching

---

## 🧪 Production Testing

**Load Testing:**
```bash
# Install Apache Bench
# Windows: choco install apache-httpd
# Linux: apt-get install apache2-utils

# Test API endpoint
ab -n 100 -c 10 -p test_case.json -T application/json \
  http://localhost:8000/generate-narrative
```

**Health Checks:**
```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-16T10:00:00",
  "components": {
    "openai_api": true,
    "mongodb_atlas": true,
    "groq_api": true
  }
}
```

---

## 📋 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] MongoDB Atlas vector index created
- [ ] Knowledge base ingested
- [ ] API documentation reviewed
- [ ] Security audit completed
- [ ] Backup strategy in place

**Deployment:**
- [ ] Deploy to staging environment
- [ ] Smoke test all endpoints
- [ ] Load test critical paths
- [ ] Monitor error logs
- [ ] Deploy to production
- [ ] Verify production health checks

**Post-Deployment:**
- [ ] Monitor application metrics
- [ ] Check error rates
- [ ] Verify API response times
- [ ] Test end-to-end workflow
- [ ] Update documentation
- [ ] Notify stakeholders

---

## 🚨 Incident Response

**Error Handling:**

MongoDB Connection Failure:
```
1. Check MongoDB Atlas status
2. Verify network connectivity
3. Check IP whitelist
4. Review connection string
5. Failover to backup if available
```

OpenAI API Rate Limit:
```
1. Implement exponential backoff
2. Cache embeddings where possible
3. Upgrade API tier if needed
4. Queue requests during peak times
```

Groq API Timeout:
```
1. Reduce max_tokens parameter
2. Implement retry logic
3. Add request timeout handling
4. Fall back to cached responses
```

---

## 📞 Support & Maintenance

**Monitoring Schedule:**
- Daily: Error logs review
- Weekly: Performance metrics review
- Monthly: Security audit
- Quarterly: Knowledge base update

**Update Procedure:**
1. Test updates in staging
2. Create backup
3. Deploy during maintenance window
4. Verify functionality
5. Monitor for 24 hours
6. Document changes

---

**Deployment Contact:**
- Technical Lead: [Your Contact]
- DevOps: [DevOps Contact]
- MongoDB Support: support.mongodb.com
- OpenAI Support: help.openai.com
- Groq Support: support.groq.com
