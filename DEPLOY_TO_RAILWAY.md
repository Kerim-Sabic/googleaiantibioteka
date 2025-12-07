# Deploy BAA-2025 to Railway

Railway is the easiest way to deploy the full BAA-2025 Flask application with all functionality.

## Why Railway?

- ✅ **Automatic Python detection** - Just push and it works
- ✅ **Free tier** - $5/month free credit (covers small-medium apps)
- ✅ **Auto-deploy from Git** - Push to GitHub, auto-deploys
- ✅ **Built-in environment variables** - Easy configuration
- ✅ **Zero config** - Detects `requirements.txt` and `run.py` automatically

## Quick Deploy (5 Minutes)

### Option 1: Railway CLI

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project (from project root)
cd /path/to/googleaiantibioteka
railway init

# 4. Deploy!
railway up

# 5. Get your deployment URL
railway domain

# Done! Your app is live at https://your-app.up.railway.app
```

### Option 2: Railway Dashboard (No CLI)

1. **Go to https://railway.app**
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select `googleaiantibioteka` repository
5. Railway auto-detects:
   - ✅ Python project
   - ✅ `requirements.txt` dependencies
   - ✅ `run.py` as entry point
6. Click "Deploy Now"
7. Get your URL from the dashboard

**That's it!** Railway handles everything automatically.

## What Railway Does Automatically

```bash
# Railway automatically runs:
pip install -r requirements.txt
python run.py
```

The app will be accessible at: `https://your-project-name.up.railway.app`

## Configuration

### Set Environment Variables (if needed)

In Railway dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key-here`

Railway will auto-restart the app.

### Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as shown

## Testing Your Deployment

Once deployed, test the API:

```bash
# Replace with your Railway URL
API_URL="https://your-app.up.railway.app"

# Test health check
curl $API_URL/api/health

# Test drug search
curl "$API_URL/api/drugs/search?generic=amoksicilin"

# Test recommendation
curl -X POST $API_URL/api/recommend \
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

## Connecting Netlify Frontend to Railway Backend

Once Railway is deployed, update the Netlify frontend:

1. Edit `public/app.js`
2. Change the API_BASE:

```javascript
// Old (Netlify Functions - not working):
const API_BASE = '/.netlify/functions';

// New (Railway backend):
const API_BASE = 'https://your-app.up.railway.app/api';
```

3. Commit and push:
```bash
git add public/app.js
git commit -m "chore: Point frontend to Railway backend API"
git push
```

4. Netlify will auto-redeploy with the new API URL

## Architecture After Hybrid Deployment

```
User Browser
     │
     ├──→ Static Assets (HTML/CSS/JS)
     │    └── Netlify CDN (global, fast)
     │
     └──→ API Calls (/api/*)
          └── Railway (Flask app with full BAA-2025 logic)
               ├── Drug Registry
               ├── Clinical Decision Engine
               └── All API endpoints
```

**Best of both worlds:**
- Frontend: Netlify's global CDN (ultra-fast)
- Backend: Railway's Python environment (full functionality)

## Monitoring

Railway provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Deployments**: History of all deployments
- **Alerts**: Email notifications for issues

Access in Railway dashboard → Your Project → Metrics

## Costs

**Free Tier:**
- $5/month free credit
- Covers ~500 MB RAM apps
- Perfect for BAA-2025

**Paid Plans** (if you exceed free tier):
- Pay-as-you-go: ~$0.000231/GB-second
- Typical cost: $5-20/month for production apps

## Troubleshooting

### Build Fails

Check Railway logs. Common issues:
- Missing dependencies → Add to `requirements.txt`
- Python version mismatch → Specify in `runtime.txt`

### App Crashes

Check logs in Railway dashboard:
```bash
# Or via CLI:
railway logs
```

### Port Issues

Railway expects apps to use the `PORT` environment variable:

```python
# Already handled in run.py:
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

## Alternative: Render

If Railway doesn't work for you, try Render (similar process):

1. Go to https://render.com
2. Create "New Web Service"
3. Connect GitHub
4. Configure:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `gunicorn run:app`
5. Add to requirements.txt:
   ```
   gunicorn==21.2.0
   ```

## Comparison

| Feature | Railway | Render | Heroku |
|---------|---------|--------|--------|
| Free Tier | $5/month credit | 750 hours/month | Paid only |
| Auto-detect Python | ✅ | ✅ | ✅ |
| CLI | ✅ | ✅ | ✅ |
| Custom Domains | ✅ Free | ✅ Free | ✅ Paid |
| PostgreSQL | ✅ Built-in | ✅ Built-in | ✅ Add-on |

**Recommendation:** Start with Railway (easiest setup).

---

**Ready?** Run `railway login` and deploy in 5 minutes! 🚀
