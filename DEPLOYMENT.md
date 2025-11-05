# Deployment Guide

## Overview

This guide covers deploying the AI Agent Maker demo to Streamlit Community Cloud. The application is designed for simple, one-click deployment.

---

## Prerequisites

1. **GitHub Account**: Repository must be public or you need Streamlit Teams
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/)
3. **OpenAI API Key**: Required for LLM functionality (or use MOCK=1 for demo)

---

## Deployment Steps

### Step 1: Prepare Repository

#### 1.1 Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: AI Agent Maker Demo"

# Create GitHub repository
# Go to github.com/new
# Repository name: ai-agent-maker-demo
# Public repository
# Do NOT initialize with README (already exists)

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/ai-agent-maker-demo.git
git branch -M main
git push -u origin main
```

#### 1.2 Verify Files

Ensure these files exist in your repository:
- ✅ `requirements.txt` - Python dependencies
- ✅ `ui/app.py` - Streamlit entry point
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.env.example` - Environment variable template
- ✅ `.gitignore` - Excludes .env and venv

---

### Step 2: Streamlit Cloud Setup

#### 2.1 Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your repositories

#### 2.2 Create New App

1. Click "New app" button
2. Fill in deployment settings:

**Repository**: `YOUR_USERNAME/ai-agent-maker-demo`
**Branch**: `main`
**Main file path**: `ui/app.py`

3. Click "Advanced settings"

#### 2.3 Configure Secrets

In the "Secrets" section, add:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key"
MOCK = "0"
ENV = "production"
```

**For Demo Mode** (no API key needed):
```toml
MOCK = "1"
ENV = "demo"
```

#### 2.4 Configure Python Version

In "Advanced settings":
- **Python version**: 3.11

---

### Step 3: Deploy

1. Click "Deploy!"
2. Wait 2-5 minutes for build
3. Monitor build logs for errors
4. Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Post-Deployment

### Verify Deployment

1. **Health Check**: App loads without errors
2. **ADK Status**: Check sidebar shows "✅ ADK Enabled" or "⚠️ Mock Mode"
3. **Load Example**: Try "Load Example" button
4. **Execute Workflow**: Run a test workflow
5. **Check Output**: Verify final output renders correctly

### Update App URL in README

Once deployed, update the README.md:

```markdown
## ⚡ 10-Second Quick Start

**Live Demo**: [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)
```

Push the change:
```bash
git add README.md
git commit -m "Update live demo URL"
git push
```

---

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key for LLM |
| `MOCK` | No | 0 | Set to "1" for mock mode (no API calls) |
| `ENV` | No | production | Environment name |
| `LOG_LEVEL` | No | INFO | Logging level |
| `DATABASE_URL` | No | sqlite:///... | Database connection |

\* Not required if `MOCK=1`

### Streamlit Secrets Management

**Option 1**: Web Interface (Recommended)
- Go to App Settings → Secrets
- Add key-value pairs in TOML format

**Option 2**: `.streamlit/secrets.toml` (Local Only)
```toml
OPENAI_API_KEY = "sk-..."
MOCK = "0"
```

**⚠️ Warning**: Never commit `secrets.toml` to GitHub!

---

## Troubleshooting

### Build Fails

**Symptom**: Deployment fails during build

**Common Causes**:
1. **Missing requirements**: Check `requirements.txt` is complete
2. **Python version**: Ensure 3.11+ specified
3. **Import errors**: Verify all imports are correct

**Solution**:
```bash
# Test locally first
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run ui/app.py
```

### App Crashes on Startup

**Symptom**: "Oh no" error page

**Check**:
1. View logs in Streamlit Cloud dashboard
2. Look for import errors or missing dependencies
3. Verify file paths are correct (should be relative)

**Common Fix**:
```python
# Bad
import src.core.schemas  # Fails on Streamlit Cloud

# Good
from src.core.schemas import Workflow  # Works everywhere
```

### API Key Issues

**Symptom**: LLM calls fail

**Solutions**:
1. Verify `OPENAI_API_KEY` in secrets
2. Check API key is valid and has credits
3. Enable mock mode: `MOCK=1` in secrets

### ADK Not Detected

**Symptom**: Shows "Mock Mode" even with google-adk installed

**Expected**: ADK detection may fail on Streamlit Cloud
**Solution**: This is normal - ADK integration is optional for demo

### Performance Issues

**Symptom**: App is slow or times out

**Solutions**:
1. Enable `MOCK=1` for faster demo mode
2. Reduce timeout in API calls
3. Cache LLM responses (add @st.cache_data)

---

## Advanced Configuration

### Custom Domain

Streamlit Community Cloud doesn't support custom domains on free tier.

**For Custom Domain**:
1. Upgrade to Streamlit Teams
2. Follow [custom domain guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

### Resource Limits

**Streamlit Community Cloud Limits**:
- 1 GB RAM
- 2 CPU cores
- 2 GB storage
- Apps sleep after 7 days of inactivity

**If you hit limits**:
1. Optimize memory usage (clear caches)
2. Reduce concurrent requests
3. Consider Streamlit Teams for higher limits

### Environment-Specific Settings

Create different branches for different environments:

```bash
# Production
git checkout main
# Set MOCK=0 in Streamlit secrets

# Demo/Staging
git checkout -b demo
# Set MOCK=1 in Streamlit secrets
# Deploy from 'demo' branch
```

---

## Continuous Deployment

### Auto-Deploy on Push

Streamlit Cloud automatically redeploys when you push to the configured branch.

```bash
git add .
git commit -m "Update feature X"
git push
# App will automatically redeploy
```

### Manual Reboot

If app gets stuck:
1. Go to App Settings
2. Click "Reboot app"
3. Wait for restart

### Rollback

To rollback to previous version:
1. Find last good commit: `git log`
2. Revert: `git revert <commit-hash>`
3. Push: `git push`
4. Or reset branch in Streamlit settings

---

## Monitoring

### View Logs

1. Open app in Streamlit Cloud
2. Click hamburger menu (☰) → "Manage app"
3. Click "Logs" tab
4. View real-time logs

### Error Tracking

Add error tracking (optional):
```python
# In ui/app.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

### Usage Analytics

Streamlit provides basic analytics:
- Page views
- Unique visitors
- App uptime

Access via Streamlit Cloud dashboard.

---

## Local Development Best Practices

### Before Pushing to Production

```bash
# 1. Test locally
make dev

# 2. Run tests
pytest

# 3. Check linting
ruff check src tests

# 4. Verify imports
python -c "import src.core.schemas; import api.main; import ui.app"

# 5. Test with mock mode
MOCK=1 streamlit run ui/app.py

# 6. Test with real API
MOCK=0 streamlit run ui/app.py

# 7. Push
git push
```

### Hot Reload Development

Streamlit auto-reloads on file changes:
```bash
streamlit run ui/app.py
# Edit files → Auto-reload
```

---

## Cost Considerations

### Streamlit Cloud
- **Free Tier**: Unlimited public apps
- **Teams Tier**: $250/month (private apps, custom domains)

### OpenAI API
- **gpt-4o-mini**: ~$0.15-0.60 per 1M tokens
- Estimated cost per execution: $0.01-0.05
- Use `MOCK=1` for unlimited free demo mode

---

## Security Checklist

- [ ] `.env` and `secrets.toml` in `.gitignore`
- [ ] API keys stored in Streamlit secrets (not code)
- [ ] No hardcoded credentials
- [ ] Input validation with Pydantic
- [ ] HTTPS enabled (automatic on Streamlit Cloud)
- [ ] No sensitive data in logs

---

## Support

### Streamlit Issues
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Docs](https://docs.streamlit.io/)

### App-Specific Issues
- Check GitHub Issues
- Review application logs
- Test locally first

---

## Production Checklist

Before marking deployment as complete:

- [ ] App deployed and accessible
- [ ] All features work (load example, execute, view results)
- [ ] ADK status displays correctly
- [ ] No console errors
- [ ] README updated with live demo URL
- [ ] GitHub repository is public
- [ ] Secrets configured correctly
- [ ] Logs show no errors
- [ ] Test with multiple scenarios
- [ ] Performance is acceptable

---

**Deployment Complete!** 🎉

Your AI Agent Maker demo is now live and showcasing your agent builder capabilities.
