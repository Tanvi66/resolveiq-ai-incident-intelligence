#!/bin/bash
set -e
PROJECT_ID="$1"
REGION="${2:-asia-south1}"
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
gcloud run deploy resolveiq-api --source ./backend --region "$REGION" --allow-unauthenticated
echo "API deployed. Update frontend/index.html API URL with the Cloud Run URL."
