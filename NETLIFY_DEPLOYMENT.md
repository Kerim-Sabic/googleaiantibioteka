# Netlify Deployment Guide for BAA-2025

This guide explains how to deploy the Bosnia & Herzegovina Antibiotic Advisor (BAA-2025) to Netlify.

## Architecture Overview

The BAA-2025 system on Netlify uses a **hybrid architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Netlify Deployment                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Static Frontend (public/)                       │   │
│  │  - HTML, CSS, JavaScript                        │   │
│  │  - Served via Netlify CDN                       │   │
│  │  - Global distribution                          │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Netlify Functions (Python)                      │   │
│  │  - Serverless API endpoints                     │   │
│  │  - Auto-scaling                                 │   │
│  │  - /recommend, /search, /health, etc.          │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Drug Registry Database (JSON)                   │   │
│  │  - Bundled with functions                       │   │
│  │  - Loaded into memory on cold start             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Quick Deploy

### Option 1: Deploy via Netlify UI (Recommended)

1. **Fork or Push this Repository to GitHub**

2. **Login to Netlify**
   - Go to https://app.netlify.com
   - Sign up or login with GitHub

3. **Create New Site**
   - Click "Add new site" → "Import an existing project"
   - Choose "GitHub" and authorize Netlify
   - Select your `googleaiantibioteka` repository

4. **Configure Build Settings**
   - **Build command**: Leave empty (or `echo "Building BAA-2025"`)
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`

5. **Deploy**
   - Click "Deploy site"
   - Netlify will automatically build and deploy
   - Your site will be live at `https://[random-name].netlify.app`

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site (from project root)
cd /path/to/googleaiantibioteka
netlify init

# Deploy
netlify deploy --prod
```

## Configuration Files

### netlify.toml

The `netlify.toml` file configures the deployment:

```toml
[build]
  command = "echo 'Building BAA-2025 for Netlify'"
  publish = "public"
  functions = "netlify/functions"

[build.environment]
  PYTHON_VERSION = "3.9"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

This configuration:
- Sets `public/` as the static site directory
- Sets `netlify/functions/` as the serverless functions directory
- Redirects `/api/*` to Netlify Functions for cleaner URLs
- Specifies Python 3.9 for the functions runtime

## Netlify Functions

The following serverless functions are available:

### 1. **POST /.netlify/functions/recommend**
Generate antibiotic recommendation

**Request:**
```json
{
  "patient": {
    "demographics": {"age_years": 35, "gender": "male", "weight_kg": 75},
    "physiology": {"serum_creatinine_mg_dl": 1.0}
  },
  "infection": {
    "site": "community_acquired_pneumonia",
    "severity": "moderate"
  }
}
```

### 2. **GET /.netlify/functions/search?generic={name}**
Search drugs by generic name

**Example:** `/.netlify/functions/search?generic=amoksicilin`

### 3. **GET /.netlify/functions/antipseudomonal**
List all antipseudomonal drugs

### 4. **GET /.netlify/functions/anti-mrsa**
List all anti-MRSA drugs

### 5. **GET /.netlify/functions/health**
Health check endpoint

## Testing Locally

### Using Netlify Dev CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Start local development server
netlify dev

# Access at http://localhost:8888
```

The Netlify Dev CLI will:
- Serve static files from `public/`
- Run functions locally
- Simulate redirects and headers
- Hot-reload on changes

### Testing Functions Directly

```bash
# Test health check
curl http://localhost:8888/.netlify/functions/health

# Test drug search
curl http://localhost:8888/.netlify/functions/search?generic=ceftriakson

# Test recommendation (POST)
curl -X POST http://localhost:8888/.netlify/functions/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "demographics": {"age_years": 35, "gender": "male", "weight_kg": 75}
    },
    "infection": {
      "site": "community_acquired_pneumonia",
      "severity": "moderate"
    }
  }'
```

## Environment Variables

If you need to add environment variables:

1. **Via Netlify UI:**
   - Go to Site settings → Build & deploy → Environment
   - Add variables

2. **Via netlify.toml:**
   ```toml
   [build.environment]
     PYTHON_VERSION = "3.9"
     CUSTOM_VAR = "value"
   ```

## Deployment Checklist

- [x] `netlify.toml` configured
- [x] `public/` directory with static files
- [x] `netlify/functions/` directory with Python functions
- [x] `netlify/functions/requirements.txt` for Python dependencies
- [x] All app code accessible to functions via relative imports
- [x] Drug registry JSON files in `data/registry/`
- [x] Frontend updated to call `/.netlify/functions/*` endpoints

## Performance Optimization

### Cold Starts
Netlify Functions have cold starts (first request after idle). To minimize:
- Keep functions lightweight
- Cache drug registry in memory
- Use function bundling (Netlify does this automatically)

### CDN Caching
Static files are automatically cached on Netlify's global CDN.

### Function Timeouts
- Default: 10 seconds
- Maximum: 26 seconds (upgrade plan for longer)
- BAA-2025 functions typically respond in < 2 seconds

## Monitoring

### Netlify Dashboard
- View function logs at: Site → Functions → [Function Name] → Logs
- Monitor bandwidth and build minutes
- Check deploy status and history

### Function Analytics
Available in Netlify dashboard:
- Request count
- Error rate
- Execution time
- Bandwidth usage

## Troubleshooting

### Function Errors

**Error: "Module not found"**
- Ensure `netlify/functions/requirements.txt` includes all dependencies
- Check that relative imports point to correct paths

**Error: "Function timeout"**
- Optimize code to run faster
- Consider caching drug registry globally

### Build Failures

**Error: "Publish directory not found"**
- Ensure `public/` directory exists
- Check `netlify.toml` publish path

### CORS Issues

CORS headers are already configured in all functions:
```python
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
}
```

## Custom Domain

To use a custom domain:

1. Go to Site settings → Domain management
2. Add custom domain
3. Configure DNS (Netlify provides instructions)
4. HTTPS is automatic (Let's Encrypt)

## Cost

**Netlify Free Tier includes:**
- 100 GB bandwidth/month
- 125,000 serverless function requests/month
- Automatic HTTPS
- Global CDN
- Continuous deployment

For BAA-2025, the free tier is typically sufficient for:
- 10,000+ recommendation requests/month
- Unlimited static page views
- Complete API functionality

## Production Considerations

1. **Rate Limiting**: Consider adding rate limiting for production
2. **Authentication**: Add API key authentication if needed
3. **Logging**: Integrate with external logging service (e.g., Sentry)
4. **Monitoring**: Set up uptime monitoring (e.g., UptimeRobot)
5. **Backups**: Git repository serves as backup for code and data

## Additional Resources

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Netlify Python Functions](https://docs.netlify.com/functions/languages/python/)
- [Netlify CLI Documentation](https://cli.netlify.com/)

## Support

For deployment issues:
- Check Netlify deploy logs in dashboard
- Review function logs for runtime errors
- Test locally with `netlify dev` first
- Contact support at https://github.com/Kerim-Sabic/googleaiantibioteka/issues

---

**Deployed on Netlify**: Your site will be live at `https://[your-site-name].netlify.app`

**Status Badge**: Add to README:
```markdown
[![Netlify Status](https://api.netlify.com/api/v1/badges/YOUR-SITE-ID/deploy-status)](https://app.netlify.com/sites/YOUR-SITE-NAME/deploys)
```
