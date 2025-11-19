# Deploying Carissa School Website to Vercel

## Important Considerations for Vercel

### ⚠️ Serverless Architecture
Vercel uses serverless functions, which means:
1. **No Persistent File Storage**: Uploaded files (images, PDFs) won't persist between deployments
2. **No SQLite Persistence**: The SQLite database will reset on each deployment
3. **Stateless Functions**: Each request runs in a new, isolated environment

## Quick Deployment Steps

### 1. Push to GitHub (Already Done!)
Your code is now on GitHub at: https://github.com/Lera2able/carissa.git

### 2. Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with your GitHub account
3. Click "New Project"
4. Import your `carissa` repository
5. Vercel will auto-detect the configuration
6. Click "Deploy"

That's it! Vercel will deploy your site automatically.

### 3. Access Your Site
Once deployed, Vercel gives you a URL like: `https://carissa.vercel.app`

## Solutions for Serverless Limitations

### Option 1: Use Vercel Postgres (Recommended)

Vercel offers a free Postgres database that persists data:

1. In Vercel Dashboard, go to your project
2. Click "Storage" tab
3. Create a new Postgres database
4. Install the Vercel Postgres SDK:
   ```bash
   pip install vercel-postgres
   ```

5. Update `app.py` to use Postgres instead of SQLite:
   ```python
   import os
   from vercel_postgres import connect
   
   # Get database URL from environment
   DATABASE_URL = os.environ.get('POSTGRES_URL')
   ```

### Option 2: Use Cloudinary for File Uploads

For persistent image/file storage:

1. Sign up at [cloudinary.com](https://cloudinary.com) (free tier available)
2. Install Cloudinary SDK:
   ```bash
   pip install cloudinary
   ```
3. Add Cloudinary credentials to Vercel environment variables
4. Update file upload code to use Cloudinary

### Option 3: Use Supabase (Free Alternative)

Supabase provides both database and storage:

1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Use their PostgreSQL database
4. Use their storage buckets for files
5. Install Supabase client:
   ```bash
   pip install supabase
   ```

## Environment Variables in Vercel

Add these in Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
CLOUDINARY_URL=your-cloudinary-url (if using Cloudinary)
```

## Testing Locally Before Deployment

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Run locally:
   ```bash
   vercel dev
   ```

## Current Limitations (Out of the Box)

### What Works:
✅ All pages display correctly
✅ Login system works
✅ Navigation works
✅ Forms work
✅ CSS and images work

### What Needs External Service:
❌ Database resets on each deploy (need Postgres/Supabase)
❌ Uploaded files disappear (need Cloudinary/S3/Supabase Storage)
❌ User sessions may not persist (need Redis/Vercel KV)

## Alternative: Traditional Hosting

If you need everything to work immediately without external services, consider:

1. **cPanel Hosting** (most shared hosting providers)
   - Everything works out of the box
   - SQLite works fine
   - File uploads persist
   - More affordable long-term

2. **VPS/DigitalOcean**
   - Full control
   - No limitations
   - See DEPLOYMENT_GUIDE.md for details

## Recommended Approach for Vercel

### Phase 1: Deploy As-Is (for testing)
- Deploy to Vercel to see the site live
- Test all pages and navigation
- Shows you how it looks

### Phase 2: Add Persistence (for production)
- Set up Vercel Postgres for database
- Set up Cloudinary for file uploads
- Update code to use external services
- This makes it production-ready

## Quick Fix: Hybrid Approach

Deploy to Vercel for the public-facing site (homepage, about, contact), but host the admin panel and educational platform on traditional hosting where SQLite and file uploads work perfectly.

## Need Help?

### Vercel Postgres Setup:
https://vercel.com/docs/storage/vercel-postgres

### Cloudinary Setup:
https://cloudinary.com/documentation/python_integration

### Supabase Setup:
https://supabase.com/docs/guides/getting-started/quickstarts/python

## What I Recommend

For Carissa School, I suggest:

1. **Short Term**: Deploy to Vercel to get the public site online quickly
2. **Long Term**: 
   - Either move to cPanel/traditional hosting (simpler, everything works)
   - Or integrate Vercel Postgres + Cloudinary (more scalable, but more setup)

The code is ready for both approaches! Just choose what works best for your needs.

## Quick Vercel Postgres Integration

If you want to quickly switch to Postgres, I can help you update the code. Just let me know!

```python
# Example modification needed in app.py
# Instead of SQLite:
# DATABASE = 'database/school.db'

# Use Postgres:
import os
DATABASE_URL = os.environ.get('POSTGRES_URL')
# Then update all database connections to use PostgreSQL
```

## Questions?

Feel free to ask if you need help with:
- Setting up Vercel Postgres
- Integrating Cloudinary for images
- Alternative deployment options
- Migrating to traditional hosting

The website is beautifully built and ready to go - we just need to choose the right deployment strategy for your needs!
