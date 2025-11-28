"""
Certificate Management API Endpoints Module

This module provides REST API endpoints for certificate operations:
- Certificate issuance (with authentication, ECDSA signing, privacy)
- Certificate verification (public, with signature and Merkle proof verification)
- Certificate querying (by student, by issuer)
- Certificate revocation (with authentication)

Key Features:
- JWT authentication for protected endpoints
- ECDSA digital signatures for certificate authenticity
- Privacy-preserving blockchain storage (PII hashes only)
- Merkle tree verification for efficient certificate validation
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models.db_models import CertificateDB, InstitutionKey, CertificateSignature
from ..services.blockchain_service import BlockchainService
from ..utils.auth import get_current_institution, get_current_user
from ..utils.ecdsa_utils import sign_data, verify_signature, create_certificate_hash_for_signing
from ..utils.merkle_tree import hash_data
import hashlib
import json
import time
from datetime import datetime

# ============================================================================
# API Router Setup
# ============================================================================

router = APIRouter(prefix="/certificates", tags=["certificates"])

# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class CertificateRequest(BaseModel):
    """
    Request model for certificate issuance.
    
    Note: issuer_name and issuer_id are NOT included here because they
    come from the authenticated user (current_user). This prevents
    institutions from issuing certificates as other institutions.
    
    Fields:
        student_name: Student's full name (PII)
        student_id: Student identifier
        course_name: Name of the course
        grade: Student's grade (PII)
        course_duration: Optional course duration
    """
    student_name: str
    student_id: str
    course_name: str
    grade: str
    course_duration: str = None

class VerificationRequest(BaseModel):
    """
    Request model for certificate verification.
    
    Fields:
        certificate_id: Unique certificate identifier to verify
    """
    certificate_id: str

class RevocationRequest(BaseModel):
    """
    Request model for certificate revocation.
    
    Fields:
        certificate_id: Certificate identifier to revoke
        reason: Optional reason for revocation
    """
    certificate_id: str
    reason: str = None

# ============================================================================
# Privacy-Preserving Hash Function
# ============================================================================

def create_pii_hash(certificate_data: dict) -> str:
    """
    Create SHA-256 hash of PII (Personally Identifiable Information) data.
    
    This function extracts only PII fields and creates a hash for blockchain storage.
    The actual PII data is stored in the private database (CertificateDB).
    
    PII Fields Hashed:
        - student_name: Student's full name
        - student_id: Student identifier
        - grade: Student's grade
    
    Args:
        certificate_data: Dictionary containing certificate data
    
    Returns:
        str: SHA-256 hash of PII data (64 character hex string)
    
    Note:
        Keys are sorted to ensure consistent hashing regardless of input order
    """
    # Extract only PII fields
    pii_data = {
        'student_name': certificate_data.get('student_name'),
        'student_id': certificate_data.get('student_id'),
        'grade': certificate_data.get('grade')
    }
    
    # Convert to JSON string with sorted keys for consistency
    pii_string = json.dumps(pii_data, sort_keys=True)
    
    # Return SHA-256 hash
    return hash_data(pii_string)

# ============================================================================
# Certificate Issuance Endpoint
# ============================================================================

@router.post("/issue")
async def issue_certificate(
    cert_request: CertificateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_institution)
):
    """
    Issue a new certificate (requires institution/admin authentication).
    
    This endpoint creates a new certificate with the following process:
    1. Validates user has institution/admin role
    2. Retrieves institution's ECDSA key pair
    3. Creates certificate record in private database (with PII)
    4. Creates hash of PII for blockchain storage (privacy)
    5. Signs certificate with institution's private key (ECDSA)
    6. Stores signature in database
    7. Adds certificate hash to blockchain (not actual PII)
    8. Commits all changes atomically
    
    Security:
        - Requires JWT authentication
        - Only institutions and admins can issue
        - Certificate is digitally signed
        - PII is not stored on blockchain
    
    Args:
        cert_request: Certificate data (student info, course, grade)
        db: Database session (injected by FastAPI)
        current_user: Authenticated institution/admin user (from dependency)
    
    Returns:
        dict: Certificate information including:
            - success: Operation success status
            - certificate_id: Unique certificate identifier
            - certificate: Full certificate data
            - blockchain_info: Block information
            - signature: Digital signature information
    
    Raises:
        HTTPException: 500 if institution key not found
        HTTPException: 500 if blockchain addition fails
        HTTPException: 400 for other errors
    """
    try:
        # ================================================================
        # Get Institution ECDSA Key Pair
        # ================================================================
        # Institutions need their key pair to sign certificates
        institution_key = db.query(InstitutionKey).filter(
            InstitutionKey.issuer_id == current_user.issuer_id
        ).first()
        
        if not institution_key:
            raise HTTPException(
                status_code=500,
                detail="Institution key not found. Please contact administrator."
            )
        
        # ================================================================
        # Generate Certificate Metadata
        # ================================================================
        issue_date = datetime.now().strftime("%Y-%m-%d")
        timestamp = time.time()
        
        # Generate unique certificate ID using SHA-256
        # Format: hash(student_id + course_name + timestamp)
        cert_string = f"{cert_request.student_id}_{cert_request.course_name}_{timestamp}"
        certificate_id = hashlib.sha256(cert_string.encode()).hexdigest()[:16].upper()
        
        # ================================================================
        # Create Certificate in Private Database (with PII)
        # ================================================================
        # Full certificate data including PII is stored in private database
        # This is NOT stored on blockchain for privacy compliance
        certificate = CertificateDB(
            certificate_id=certificate_id,
            student_name=cert_request.student_name,  # PII
            student_id=cert_request.student_id,
            course_name=cert_request.course_name,
            grade=cert_request.grade,  # PII
            issuer_name=current_user.issuer_name or "Unknown",
            issuer_id=current_user.issuer_id,
            issuer_user_id=current_user.id,  # Link to issuing user
            course_duration=cert_request.course_duration or "N/A",
            issue_date=issue_date,
            timestamp=timestamp,
            status="active"
        )
        
        db.add(certificate)
        db.flush()  # Flush to get certificate.id
        
        # ================================================================
        # Create PII Hash for Blockchain (Privacy Feature)
        # ================================================================
        # Only hash of PII is stored on blockchain, not the actual data
        # This allows verification without exposing personal information
        pii_hash = create_pii_hash({
            'student_name': cert_request.student_name,
            'student_id': cert_request.student_id,
            'grade': cert_request.grade
        })
        
        # ================================================================
        # Prepare Data for Digital Signing
        # ================================================================
        # Create standardized data structure for signing
        # Excludes signature fields and PII to avoid circular dependencies
        signing_data = create_certificate_hash_for_signing({
            'certificate_id': certificate_id,
            'student_id': cert_request.student_id,
            'course_name': cert_request.course_name,
            'grade': cert_request.grade,
            'issuer_id': current_user.issuer_id,
            'issue_date': issue_date,
            'timestamp': timestamp
        })
        
        # ================================================================
        # Sign Certificate with ECDSA
        # ================================================================
        # Digital signature proves certificate was issued by legitimate institution
        signature = sign_data(institution_key.private_key_encrypted, signing_data)
        
        # ================================================================
        # Store Digital Signature
        # ================================================================
        cert_signature = CertificateSignature(
            certificate_id=certificate_id,
            institution_key_id=institution_key.id,
            signature=signature,  # Base64-encoded ECDSA signature
            public_key=institution_key.public_key  # For verification
        )
        db.add(cert_signature)
        
        # ================================================================
        # Add Certificate to Blockchain (Hash Only, Not PII)
        # ================================================================
        # Blockchain service adds certificate hash to blockchain
        # This does NOT commit - transaction is managed by this function
        blockchain_service = BlockchainService(db)
        result = blockchain_service.add_certificate_to_blockchain(certificate, pii_hash)
        
        # If blockchain addition failed, rollback everything
        if not result['success']:
            db.rollback()
            raise HTTPException(status_code=500, detail=result['message'])
        
        # ================================================================
        # Commit Transaction
        # ================================================================
        # All changes (certificate, signature, blockchain entry) are committed atomically
        # If any part fails, entire transaction is rolled back
        db.commit()
        db.refresh(certificate)  # Refresh to get database-generated fields
        
        # ================================================================
        # Return Success Response
        # ================================================================
        return {
            "success": True,
            "message": "Certificate issued successfully",
            "certificate_id": certificate_id,
            "certificate": {
                "certificate_id": certificate_id,
                "student_name": certificate.student_name,
                "student_id": certificate.student_id,
                "course_name": certificate.course_name,
                "grade": certificate.grade,
                "issuer_name": certificate.issuer_name,
                "issuer_id": certificate.issuer_id,
                "course_duration": certificate.course_duration,
                "issue_date": certificate.issue_date,
                "timestamp": certificate.timestamp,
                "status": certificate.status
            },
                    "blockchain_info": {
                        "block_index": result['block_index'],
                        "block_hash": result['block_hash'],
                        "merkle_root": result.get('merkle_root'),
                        "genesis_created": result.get('genesis_created', False)
                    },
            "signature": {
                "signed": True,
                "public_key": institution_key.public_key[:50] + "..."  # Truncated for display
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        # Rollback on any other error
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Certificate Verification Endpoint
# ============================================================================

@router.post("/verify")
async def verify_certificate(
    verification_request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify a certificate (public endpoint, no authentication required).
    
    This endpoint verifies a certificate by:
    1. Checking certificate exists in blockchain
    2. Retrieving full certificate data from private database
    3. Verifying Merkle proof (certificate is in the block)
    4. Verifying ECDSA signature (certificate was signed by institution)
    5. Checking certificate status (not revoked)
    
    This is a PUBLIC endpoint - anyone can verify certificates without
    authentication. This enables employers and others to verify credentials.
    
    Args:
        verification_request: Contains certificate_id to verify
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Verification result with:
            - verified: Boolean indicating if certificate was found
            - valid: Boolean indicating if certificate is valid (not revoked, signature valid)
            - certificate: Full certificate data
            - blockchain_proof: Merkle proof and block information
            - signature_verified: Boolean indicating if signature is valid
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        # ================================================================
        # Verify Certificate in Blockchain
        # ================================================================
        blockchain_service = BlockchainService(db)
        result = blockchain_service.verify_certificate(verification_request.certificate_id)
        
        # If certificate not found, return early
        if not result['found']:
            return {
                "verified": False,
                "valid": False,
                "message": "Certificate not found"
            }
        
        # ================================================================
        # Verify ECDSA Digital Signature
        # ================================================================
        # Get certificate from database
        certificate = db.query(CertificateDB).filter(
            CertificateDB.certificate_id == verification_request.certificate_id
        ).first()
        
        # Safety check: If certificate not found in database (data inconsistency)
        if not certificate:
            return {
                "verified": True,
                "valid": False,
                "message": "Certificate found in blockchain but missing from database"
            }
        
        # Get signature record
        signature_record = db.query(CertificateSignature).filter(
            CertificateSignature.certificate_id == verification_request.certificate_id
        ).first()
        
        # Verify signature if it exists
        signature_valid = False
        if signature_record:
            # Recreate signing data (must match format used during signing)
            signing_data = create_certificate_hash_for_signing({
                'certificate_id': certificate.certificate_id,
                'student_id': certificate.student_id,
                'course_name': certificate.course_name,
                'grade': certificate.grade,
                'issuer_id': certificate.issuer_id,
                'issue_date': certificate.issue_date,
                'timestamp': certificate.timestamp
            })
            
            # Verify signature using public key
            signature_valid = verify_signature(
                signature_record.public_key,
                signing_data,
                signature_record.signature
            )
        
        # ================================================================
        # Return Verification Result
        # ================================================================
        # Certificate is valid only if:
        # 1. Found in blockchain
        # 2. Merkle proof is valid (from blockchain_service)
        # 3. Status is active
        # 4. Digital signature is valid
        return {
            "verified": True,
            "valid": result['valid'] and signature_valid,
            "certificate": result['certificate'],
            "blockchain_proof": result['blockchain_proof'],
            "signature_verified": signature_valid
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Certificate Querying Endpoints
# ============================================================================

@router.get("/student/{student_id}")
async def get_student_certificates(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all certificates for a specific student.
    
    This endpoint retrieves all certificates issued to a student.
    Useful for students to view their complete academic portfolio.
    
    This is a PUBLIC endpoint (no authentication required).
    
    Args:
        student_id: Student identifier to search for
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Student certificates with:
            - student_id: The student identifier
            - certificates: List of certificate dictionaries
            - count: Number of certificates found
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        blockchain_service = BlockchainService(db)
        certificates = blockchain_service.get_certificates_by_student(student_id)
        return {
            "student_id": student_id,
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/issuer/{issuer_id}")
async def get_issuer_certificates(
    issuer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all certificates issued by a specific institution.
    
    This endpoint retrieves all certificates issued by an institution.
    Useful for institutions to view their certificate issuance history.
    
    This is a PUBLIC endpoint (no authentication required).
    
    Args:
        issuer_id: Institution identifier to search for
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Institution certificates with:
            - issuer_id: The institution identifier
            - certificates: List of certificate dictionaries
            - count: Number of certificates found
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        blockchain_service = BlockchainService(db)
        certificates = blockchain_service.get_certificates_by_issuer(issuer_id)
        return {
            "issuer_id": issuer_id,
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Certificate Revocation Endpoint
# ============================================================================

@router.post("/revoke")
async def revoke_certificate(
    revocation_request: RevocationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_institution)
):
    """
    Revoke a certificate (requires institution/admin authentication).
    
    This endpoint revokes a certificate by marking it as 'revoked' in the database.
    The certificate remains in the blockchain (immutable), but verification
    will return valid=False for revoked certificates.
    
    Security:
        - Requires JWT authentication
        - Only the issuing institution or admin can revoke
        - Prevents institutions from revoking other institutions' certificates
    
    Args:
        revocation_request: Contains certificate_id and optional reason
        db: Database session (injected by FastAPI)
        current_user: Authenticated institution/admin user (from dependency)
    
    Returns:
        dict: Revocation result with:
            - success: Boolean indicating operation success
            - message: Status message
            - certificate_id: Revoked certificate identifier
            - reason: Revocation reason (if provided)
    
    Raises:
        HTTPException: 404 if certificate not found
        HTTPException: 403 if user doesn't have permission to revoke
        HTTPException: 400 for other errors
    """
    try:
        # ================================================================
        # Find Certificate
        # ================================================================
        certificate = db.query(CertificateDB).filter(
            CertificateDB.certificate_id == revocation_request.certificate_id
        ).first()
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # ================================================================
        # Verify Permission to Revoke
        # ================================================================
        # Only the issuing institution or admin can revoke
        # This prevents institutions from revoking other institutions' certificates
        if current_user.role != "admin" and certificate.issuer_id != current_user.issuer_id:
            raise HTTPException(
                status_code=403,
                detail="You can only revoke certificates issued by your institution"
            )
        
        # ================================================================
        # Revoke Certificate
        # ================================================================
        blockchain_service = BlockchainService(db)
        result = blockchain_service.revoke_certificate(
            revocation_request.certificate_id,
            revocation_request.reason
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Certificate revoked successfully",
                "certificate_id": revocation_request.certificate_id,
                "reason": revocation_request.reason
            }
        else:
            raise HTTPException(status_code=404, detail=result['message'])
    
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# All Certificates Endpoint (Demo/Development)
# ============================================================================

@router.get("/all")
async def get_all_certificates(db: Session = Depends(get_db)):
    """
    Get all certificates in the system (for demo/development purposes).
    
    This endpoint returns all certificates. Useful for development and testing.
    In production, you might want to:
    - Add pagination
    - Require authentication
    - Add filtering/sorting options
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: All certificates with:
            - certificates: List of all certificate dictionaries
            - count: Total number of certificates
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        blockchain_service = BlockchainService(db)
        certificates = blockchain_service.get_all_certificates()
        return {
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
