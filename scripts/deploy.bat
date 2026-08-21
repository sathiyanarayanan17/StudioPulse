@echo off
REM StudioPulse AI - Deploy to Google Cloud Run
echo ============================================
echo   Deploying StudioPulse AI to Cloud Run
echo ============================================
echo.

set /p PROJECT_ID="Enter your Google Cloud Project ID: "
set REGION=us-central1

echo.
echo [1/4] Authenticating with Google Cloud...
call gcloud auth login
call gcloud config set project %PROJECT_ID%

echo [2/4] Enabling required APIs...
call gcloud services enable aiplatform.googleapis.com
call gcloud services enable monitoring.googleapis.com
call gcloud services enable run.googleapis.com
call gcloud services enable cloudbuild.googleapis.com
call gcloud services enable artifactregistry.googleapis.com

echo [3/4] Creating Artifact Registry repository...
call gcloud artifacts repositories create studiopulse --repository-format=docker --location=%REGION% 2>NUL

echo [4/4] Building and deploying to Cloud Run...
call gcloud run deploy studiopulse-ai ^
    --source . ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --set-env-vars "GOOGLE_CLOUD_PROJECT=%PROJECT_ID%,GOOGLE_CLOUD_REGION=%REGION%"

echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
echo Your StudioPulse AI agent is now running on Cloud Run.
