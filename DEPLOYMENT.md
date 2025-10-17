# CurioStack Deployment Guide

This guide covers deployment instructions for both the CurioStack Python package and the associated website.

## Python Package Deployment

### 1. Package Setup

Ensure your `pyproject.toml` and `requirements.txt` are up to date:
```bash
# Install build dependencies
python -m pip install --upgrade pip build twine

# Build the package
python -m build
```

### 2. Testing the Package

```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the package locally
pip install dist/curiostack-0.1.0.tar.gz

# Run tests
python -m pytest
```

### 3. Deploying to PyPI

```bash
# Create PyPI account if you haven't already
# Visit: https://pypi.org/account/register/

# Deploy to Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Once tested, deploy to production PyPI
python -m twine upload dist/*
```

### 4. CI/CD Setup with GitHub Actions

Create `.github/workflows/python-publish.yml`:

```yaml
name: Publish Python Package

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish package
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Website Deployment

The website is configured for deployment using Docker and can be deployed to various platforms.

### 1. Environment Setup

```bash
cd website
cp env.example .env
# Edit .env with your production values
```

Required environment variables:
- `DATABASE_URL`: Your production database URL
- `NEXTAUTH_SECRET`: A secure random string
- `NEXTAUTH_URL`: Your production domain
- `NEXT_PUBLIC_GA_ID`: Google Analytics ID (if used)
- `NEXT_PUBLIC_ADSENSE_CLIENT_ID`: AdSense ID (if used)

### 2. Production Deployment Options

#### Option 1: Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically with git push

#### Option 2: Docker Deployment
```bash
# Build the Docker image
docker build -t curiostack-website .

# Run the container
docker run -p 3000:3000 --env-file .env curiostack-website
```

#### Option 3: Manual Deployment
```bash
# Install dependencies
npm install

# Build the application
npm run build

# Start the production server
npm start
```

### 3. Database Setup

```bash
# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate deploy
```

## Monitoring and Maintenance

### Python Package
- Monitor PyPI downloads and issues
- Set up automated testing with GitHub Actions
- Use GitHub releases for version management

### Website
- Set up monitoring (e.g., Vercel Analytics, Google Analytics)
- Configure error tracking (e.g., Sentry)
- Set up automated backups for the database

## Security Considerations

1. Never commit sensitive data or credentials
2. Use environment variables for all secrets
3. Keep dependencies updated
4. Regularly update security patches
5. Enable security headers
6. Set up CORS properly
7. Use HTTPS everywhere