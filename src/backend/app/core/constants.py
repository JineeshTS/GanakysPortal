"""
Application Constants
Centralized configuration values and magic numbers for maintainability
"""

# ============================================================================
# Time Constants (in seconds)
# ============================================================================
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

# Default timeouts
DEFAULT_HTTP_TIMEOUT = 30.0
AI_SERVICE_TIMEOUT = 120.0
PAYMENT_SERVICE_TIMEOUT = 30.0

# Task time limits
TASK_TIME_LIMIT_SHORT = 300     # 5 minutes
TASK_TIME_LIMIT_MEDIUM = 1800   # 30 minutes
TASK_TIME_LIMIT_LONG = 3600     # 1 hour
TASK_SOFT_TIME_LIMIT = 3000     # 50 minutes

# ============================================================================
# Pagination Defaults
# ============================================================================
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
BULK_LIMIT = 1000
EXPORT_LIMIT = 10000

# ============================================================================
# Security Constants
# ============================================================================
MFA_BACKUP_CODES_COUNT = 10
TOKEN_BYTES = 4  # For backup codes (hex = 8 chars)
PASSWORD_MIN_LENGTH = 8
SESSION_TOKEN_BYTES = 32

# ============================================================================
# Indian Statutory Constants
# ============================================================================
GSTIN_LENGTH = 15
PAN_LENGTH = 10
TAN_LENGTH = 10
AADHAAR_LENGTH = 12
IFSC_LENGTH = 11

# State codes for GSTIN validation
INDIAN_STATE_CODES = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "26": "Dadra & Nagar Haveli and Daman & Diu",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (old)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}

# ============================================================================
# Financial Defaults
# ============================================================================
FINANCIAL_YEAR_START_MONTH = 4  # April (India)
DEFAULT_CURRENCY = "INR"
DEFAULT_DECIMAL_PLACES = 2
PRICE_DECIMAL_PLACES = 2
QUANTITY_DECIMAL_PLACES = 3

# GST Rates (percentages)
GST_RATES = [0, 5, 12, 18, 28]
DEFAULT_GST_RATE = 18

# TDS Rates (percentages) by section
TDS_RATES = {
    "194C": 1.0,   # Contractors
    "194H": 5.0,   # Commission
    "194I": 10.0,  # Rent
    "194J": 10.0,  # Professional fees
}

# ============================================================================
# Document & File Constants
# ============================================================================
MAX_UPLOAD_SIZE_MB = 50
MAX_DOCUMENT_SIZE_MB = 25
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt"}

# ============================================================================
# Email Constants
# ============================================================================
SMTP_PORT_TLS = 587
SMTP_PORT_SSL = 465

# ============================================================================
# Manufacturing Constants
# ============================================================================
MAX_SHIFTS_PER_DAY = 4
MAX_HOURS_PER_SHIFT = 12
DEFAULT_EFFICIENCY_PERCENTAGE = 100

# OEE (Overall Equipment Effectiveness) targets
OEE_TARGET_AVAILABILITY = 90.0
OEE_TARGET_PERFORMANCE = 95.0
OEE_TARGET_QUALITY = 99.0

# ============================================================================
# HR Constants
# ============================================================================
MAX_LEAVE_DAYS_PER_YEAR = 365
DEFAULT_NOTICE_PERIOD_DAYS = 30
DEFAULT_PROBATION_DAYS = 90
WORKING_DAYS_PER_WEEK = 5
HOURS_PER_DAY = 8

# ============================================================================
# Environmental Constants (for ESG calculations)
# ============================================================================
CH4_GWP = 28   # Global Warming Potential of Methane
N2O_GWP = 265  # Global Warming Potential of Nitrous Oxide
CO2_GWP = 1    # Global Warming Potential of CO2 (reference)
