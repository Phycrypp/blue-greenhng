# Blue-Green Deployment using NGINX and Docker Compose
   
This project demonstrates a **Blue-Green deployment strategy** using Docker Compose and NGINX as a reverse proxy to route traffic between two application environments — **Blue** (active) and **Green** (s$
   
---
   
##  Quick Start
   
```bash
# 1. Copy environment example file
cp .env.example .env
   
# 2. Edit .env file to include your own image and release IDs
# Example:
# BLUE_IMAGE=yimikaade/wonderful:devops-stage-two
# GREEN_IMAGE=yimikaade/wonderful:devops-stage-two
# ACTIVE_POOL=blue
# RELEASE_ID_BLUE=blue-1.0.0
# RELEASE_ID_GREEN=green-1.0.0
# PORT=3000
   
# 3. Start containers
docker compose up -d
   
---

##  Application Entrypoints

- **Nginx Gateway:** http://localhost:8080
- **Blue App (direct):** http://localhost:8081 
- **Green App (direct):** http://localhost:8082
   
---

##  How It Works

- The active environment (`ACTIVE_POOL`) receives all traffic.   
- The standby environment is configured as a **backup** in NGINX.
- Failover automatically switches to the healthy pool if the active one fails.
- Health checks are performed via `/healthz` endpoints.
   
---
## Project Stricture
.
├──    docker-compose.yml
├──    nginx/
│    └──    nginx.conf.template
├──    .env.example
├──    README.md
├──    DECISION.md
└──    .github/workflows/verify.yml
   
---    ---
   
## 🧪 Verification

To simulate a failure and test automatic failover:

```bash
bash ./verify_failover.sh
   
👤 Author

Name:Ogunsola Victor Olaoluwa
GitHub: https://github.com/phycrypp

