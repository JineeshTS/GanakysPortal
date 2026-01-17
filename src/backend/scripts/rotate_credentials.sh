#!/bin/bash
# =============================================================================
# GanaPortal Credential Rotation Script
# =============================================================================
#
# IMPORTANT: Credentials were exposed and must be rotated immediately!
#
# This script helps you rotate all exposed credentials.
# Run each section based on your access to the respective services.
#
# =============================================================================

set -e

echo "=========================================="
echo "GanaPortal Credential Rotation Guide"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# 1. DATABASE PASSWORD ROTATION
# -----------------------------------------------------------------------------
echo -e "${YELLOW}1. DATABASE PASSWORD ROTATION${NC}"
echo "   Current: ganaportal123 (EXPOSED - ROTATE IMMEDIATELY)"
echo ""
echo "   Steps:"
echo "   a) Connect to PostgreSQL as superuser:"
echo "      sudo -u postgres psql"
echo ""
echo "   b) Generate a new secure password:"
NEW_DB_PASS=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
echo "      Suggested new password: ${NEW_DB_PASS}"
echo ""
echo "   c) Change the password in PostgreSQL:"
echo "      ALTER USER ganaportal_user WITH PASSWORD '${NEW_DB_PASS}';"
echo "      \\q"
echo ""
echo "   d) Update .env file:"
echo "      DATABASE_URL=postgresql+asyncpg://ganaportal_user:${NEW_DB_PASS}@127.0.0.1:5432/ganaportal_db"
echo ""
echo "   e) Restart the backend service"
echo ""
read -p "Press Enter to continue to next credential..."
echo ""

# -----------------------------------------------------------------------------
# 2. ANTHROPIC API KEY ROTATION
# -----------------------------------------------------------------------------
echo -e "${YELLOW}2. ANTHROPIC API KEY ROTATION${NC}"
echo "   Current: sk-ant-api03-KW4Zilw9... (EXPOSED - ROTATE IMMEDIATELY)"
echo ""
echo "   Steps:"
echo "   a) Go to: https://console.anthropic.com/settings/keys"
echo "   b) Click 'Create Key' to generate a new API key"
echo "   c) Copy the new key (it won't be shown again)"
echo "   d) IMPORTANT: Delete the old exposed key from the console"
echo "   e) Update .env file:"
echo "      ANTHROPIC_API_KEY=<your-new-key>"
echo ""
read -p "Press Enter to continue to next credential..."
echo ""

# -----------------------------------------------------------------------------
# 3. SMTP PASSWORD ROTATION (Hostinger)
# -----------------------------------------------------------------------------
echo -e "${YELLOW}3. SMTP PASSWORD ROTATION (Hostinger)${NC}"
echo "   Current: Jeenu@2025 for snehalatha@ganakys.com (EXPOSED - ROTATE IMMEDIATELY)"
echo ""
echo "   Steps:"
echo "   a) Log in to Hostinger control panel: https://hpanel.hostinger.com/"
echo "   b) Go to: Emails > Email Accounts"
echo "   c) Find snehalatha@ganakys.com and click 'Manage'"
echo "   d) Click 'Change Password'"
echo "   e) Generate a strong password:"
NEW_SMTP_PASS=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)
echo "      Suggested new password: ${NEW_SMTP_PASS}"
echo "   f) Update .env file:"
echo "      SMTP_PASSWORD=${NEW_SMTP_PASS}"
echo ""
read -p "Press Enter to continue to next credential..."
echo ""

# -----------------------------------------------------------------------------
# 4. JWT SECRET KEY (Already rotated)
# -----------------------------------------------------------------------------
echo -e "${GREEN}4. JWT SECRET KEY${NC}"
echo "   Status: Already rotated in previous fix"
echo "   Current length: 88 characters (secure)"
echo ""

# -----------------------------------------------------------------------------
# 5. NEXTAUTH SECRET (Already rotated)
# -----------------------------------------------------------------------------
echo -e "${GREEN}5. NEXTAUTH SECRET${NC}"
echo "   Status: Already rotated in previous fix"
echo "   Current length: 88 characters (secure)"
echo ""

# -----------------------------------------------------------------------------
# VERIFICATION CHECKLIST
# -----------------------------------------------------------------------------
echo "=========================================="
echo -e "${YELLOW}VERIFICATION CHECKLIST${NC}"
echo "=========================================="
echo ""
echo "After rotating all credentials, verify:"
echo ""
echo "[ ] Database connection works:"
echo "    cd /var/ganaportal/src/backend && source .venv/bin/activate"
echo "    python -c \"from app.db.session import engine; print('DB OK')\""
echo ""
echo "[ ] Anthropic API works:"
echo "    curl https://api.anthropic.com/v1/messages -H 'x-api-key: YOUR_NEW_KEY' -H 'anthropic-version: 2023-06-01'"
echo ""
echo "[ ] SMTP works:"
echo "    python -c \"import smtplib; s=smtplib.SMTP_SSL('smtp.hostinger.com', 465); s.login('snehalatha@ganakys.com', 'NEW_PASS'); print('SMTP OK')\""
echo ""
echo "[ ] Backend starts without errors:"
echo "    cd /var/ganaportal/src/backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "[ ] Frontend starts without errors:"
echo "    cd /var/ganaportal/src/frontend && npm run dev"
echo ""
echo "=========================================="
echo -e "${RED}IMPORTANT: Delete this script after use!${NC}"
echo "=========================================="
