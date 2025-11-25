# Certificate Validation System - Backend

## Overview
This is the backend API for the Certificate Validation System, built with FastAPI and a custom blockchain implementation.

## Features
- Issue academic certificates
- Verify certificate authenticity
- Revoke certificates
- View student and issuer certificate portfolios
- Blockchain integrity validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Certificates
- `POST /certificates/issue` - Issue a new certificate
- `POST /certificates/verify` - Verify a certificate
- `GET /certificates/student/{student_id}` - Get student certificates
- `GET /certificates/issuer/{issuer_id}` - Get issuer certificates
- `POST /certificates/revoke` - Revoke a certificate
- `GET /certificates/all` - Get all certificates

### Blockchain
- `GET /blockchain/info` - Get blockchain statistics
- `GET /blockchain/validate` - Validate blockchain integrity
- `GET /blockchain/blocks` - Get all blocks
- `GET /blockchain/latest-block` - Get latest block

## Project Structure
```
backend/
├── app/
│   ├── models/          # Data models
│   ├── api/            # API routes
│   ├── utils/          # Utility functions
│   └── main.py         # FastAPI application
├── requirements.txt    # Dependencies
└── README.md          # This file
```
