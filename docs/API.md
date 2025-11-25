# Certificate Validation System - API Documentation

## Overview
This document describes the REST API endpoints for the Certificate Validation System.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. In a production environment, you would implement JWT tokens or API keys.

## Endpoints

### Certificates

#### Issue Certificate
**POST** `/certificates/issue`

Issues a new certificate and stores it on the blockchain.

**Request Body:**
```json
{
  "student_name": "John Doe",
  "student_id": "STU001",
  "course_name": "Computer Science",
  "grade": "A+",
  "issuer_name": "MIT",
  "issuer_id": "MIT001",
  "course_duration": "4 years"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Certificate issued successfully",
  "certificate_id": "ABC123DEF456",
  "certificate": {
    "certificate_id": "ABC123DEF456",
    "student_name": "John Doe",
    "student_id": "STU001",
    "course_name": "Computer Science",
    "grade": "A+",
    "issuer_name": "MIT",
    "issuer_id": "MIT001",
    "course_duration": "4 years",
    "issue_date": "2024-01-15",
    "timestamp": 1705276800,
    "status": "active"
  },
  "blockchain_info": {
    "block_index": 1,
    "block_hash": "a1b2c3d4e5f6..."
  }
}
```

#### Verify Certificate
**POST** `/certificates/verify`

Verifies a certificate by its ID.

**Request Body:**
```json
{
  "certificate_id": "ABC123DEF456"
}
```

**Response:**
```json
{
  "verified": true,
  "valid": true,
  "certificate": {
    "certificate_id": "ABC123DEF456",
    "student_name": "John Doe",
    "student_id": "STU001",
    "course_name": "Computer Science",
    "grade": "A+",
    "issuer_name": "MIT",
    "issuer_id": "MIT001",
    "course_duration": "4 years",
    "issue_date": "2024-01-15",
    "timestamp": 1705276800,
    "status": "active"
  },
  "blockchain_proof": {
    "block_index": 1,
    "block_hash": "a1b2c3d4e5f6...",
    "timestamp": 1705276800
  }
}
```

#### Get Student Certificates
**GET** `/certificates/student/{student_id}`

Retrieves all certificates for a specific student.

**Response:**
```json
{
  "student_id": "STU001",
  "certificates": [
    {
      "certificate_id": "ABC123DEF456",
      "student_name": "John Doe",
      "student_id": "STU001",
      "course_name": "Computer Science",
      "grade": "A+",
      "issuer_name": "MIT",
      "issuer_id": "MIT001",
      "course_duration": "4 years",
      "issue_date": "2024-01-15",
      "timestamp": 1705276800,
      "status": "active"
    }
  ],
  "count": 1
}
```

#### Get Issuer Certificates
**GET** `/certificates/issuer/{issuer_id}`

Retrieves all certificates issued by a specific institution.

#### Revoke Certificate
**POST** `/certificates/revoke`

Revokes a certificate.

**Request Body:**
```json
{
  "certificate_id": "ABC123DEF456",
  "reason": "Academic misconduct"
}
```

#### Get All Certificates
**GET** `/certificates/all`

Retrieves all certificates in the system (for demo purposes).

### Blockchain

#### Get Blockchain Info
**GET** `/blockchain/info`

Returns blockchain statistics and information.

**Response:**
```json
{
  "success": true,
  "blockchain_info": {
    "total_blocks": 5,
    "total_certificates": 10,
    "active_certificates": 9,
    "revoked_certificates": 1,
    "latest_block_hash": "a1b2c3d4e5f6...",
    "chain_length": 5
  }
}
```

#### Validate Blockchain
**GET** `/blockchain/validate`

Validates the integrity of the blockchain.

**Response:**
```json
{
  "success": true,
  "valid": true,
  "message": "Blockchain is valid"
}
```

#### Get All Blocks
**GET** `/blockchain/blocks`

Returns all blocks in the blockchain (for demo purposes).

#### Get Latest Block
**GET** `/blockchain/latest-block`

Returns the latest block in the blockchain.

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. In production, you would implement rate limiting to prevent abuse.

## CORS

The API supports CORS for cross-origin requests from web browsers. All origins are currently allowed (`*`). In production, you should restrict this to specific domains.
