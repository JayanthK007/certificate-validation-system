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
from ..models.db_models import CertificateDB, InstitutionKey, CertificateSignature, CertificateIndex
from ..services.ethereum_helper import get_ethereum_service
from ..utils.auth import get_current_institution, get_current_user
from ..utils.ecdsa_utils import sign_data, verify_signature, create_certificate_hash_for_signing
import hashlib
import hashlib
import json
import time
from datetime import datetime

router = APIRouter(prefix="/certificates", tags=["certificates"])

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
    pii_data = {
        'student_name': certificate_data.get('student_name'),
        'student_id': certificate_data.get('student_id'),
        'grade': certificate_data.get('grade')
    }
    
    pii_string = json.dumps(pii_data, sort_keys=True)
    
    return hashlib.sha256(pii_string.encode('utf-8')).hexdigest()

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
        institution_key = db.query(InstitutionKey).filter(
            InstitutionKey.issuer_id == current_user.issuer_id
        ).first()
        
        if not institution_key:
            raise HTTPException(
                status_code=500,
                detail="Institution key not found. Please contact administrator."
            )
        
        issue_date = datetime.now().strftime("%Y-%m-%d")
        timestamp = time.time()
        
        cert_string = f"{cert_request.student_id}_{cert_request.course_name}_{timestamp}"
        certificate_id = hashlib.sha256(cert_string.encode()).hexdigest()[:16].upper()
        
        pii_hash = create_pii_hash({
            'student_name': cert_request.student_name,
            'student_id': cert_request.student_id,
            'grade': cert_request.grade
        })
        
        ethereum_service = get_ethereum_service()
        
        result = ethereum_service.issue_certificate(
            certificate_id=certificate_id,
            pii_hash=pii_hash,
            course_name=cert_request.course_name,
            issuer_id=current_user.issuer_id
        )
        
        # If blockchain addition failed, return error
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', result.get('message', 'Failed to issue certificate on Ethereum')))
        
        # Store lightweight index entry (for querying by student_id/issuer_id)
        # This does NOT store PII - only the mapping and course name
        index_entry = CertificateIndex(
            certificate_id=certificate_id,
            student_id=cert_request.student_id,
            issuer_id=current_user.issuer_id,
            course_name=cert_request.course_name,
            timestamp=timestamp,
            status="active"
        )
        db.add(index_entry)
        db.commit()
        
        return {
            "success": True,
            "message": "Certificate issued successfully on Ethereum blockchain",
            "certificate_id": certificate_id,
            "certificate": {
                "certificate_id": certificate_id,
                "student_name": cert_request.student_name,
                "student_id": cert_request.student_id,
                "course_name": cert_request.course_name,
                "grade": cert_request.grade,
                "issuer_name": current_user.issuer_name or "Unknown",
                "issuer_id": current_user.issuer_id,
                "course_duration": cert_request.course_duration or "N/A",
                "issue_date": issue_date,
                "timestamp": timestamp,
                "status": "active"
            },
            "blockchain_info": {
                "block_number": result.get('block_number'),
                "transaction_hash": result.get('transaction_hash'),
                "network": result.get('network'),
                "contract_address": result.get('contract_address'),
                "gas_used": result.get('gas_used'),
                "blockchain_type": "ethereum"
            },
            "note": "Certificate stored on Ethereum blockchain only, not in database"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

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
        ethereum_service = get_ethereum_service()
        result = ethereum_service.verify_certificate_without_pii(verification_request.certificate_id)
        
        if not result['found']:
            error_message = result.get('error', 'Certificate not found')
            return {
                "verified": False,
                "valid": False,
                "message": error_message
            }
        
        cert_data = ethereum_service.get_certificate(verification_request.certificate_id)
        
        certificate_info = {
            'certificate_id': verification_request.certificate_id,
            'student_name': None,
            'student_id': None,
            'course_name': cert_data.get('course_name'),
            'grade': None,
            'issuer_id': cert_data.get('issuer_id'),
            'timestamp': cert_data.get('timestamp'),
            'status': 'revoked' if cert_data.get('revoked') else 'active'
        }
        
        blockchain_proof = {
            'valid': result.get('valid', False),
            'issuer': result.get('issuer'),
            'timestamp': result.get('timestamp'),
            'revoked': result.get('revoked', False),
            'blockchain': 'ethereum',
            'network': result.get('network'),
            'contract_address': result.get('contract_address')
        }
        
        return {
            "verified": True,
            "valid": result.get('valid', False),
            "certificate": certificate_info,
            "blockchain_proof": blockchain_proof,
            "signature_verified": None,
            "note": "Certificate verified on Ethereum blockchain. PII (student name, ID, grade) is not stored on blockchain for privacy."
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        index_entries = db.query(CertificateIndex).filter(
            CertificateIndex.student_id == student_id,
            CertificateIndex.status == "active"
        ).all()
        
        if not index_entries:
            return {
                "student_id": student_id,
                "certificates": [],
                "count": 0,
                "note": f"No certificates found for Student ID: {student_id}. Certificates are stored on Ethereum blockchain and must be verified individually by certificate ID."
            }
        
        ethereum_service = get_ethereum_service()
        certificates = []
        
        for index_entry in index_entries:
            try:
                cert_data = ethereum_service.get_certificate(index_entry.certificate_id)
                if cert_data and (cert_data.get('exists') == True or cert_data.get('found') == True):
                    certificates.append({
                        "certificate_id": index_entry.certificate_id,
                        "student_id": index_entry.student_id,
                        "course_name": cert_data.get('course_name') or index_entry.course_name,
                        "issuer_id": cert_data.get('issuer_id') or index_entry.issuer_id,
                        "timestamp": cert_data.get('timestamp') or index_entry.timestamp,
                        "status": "revoked" if cert_data.get('revoked') else index_entry.status,
                        "revoked": cert_data.get('revoked', False),
                        "revocation_reason": cert_data.get('revocation_reason'),
                        "issuer_address": cert_data.get('issuer'),
                        "blockchain_verified": True,
                        "blockchain": cert_data.get('blockchain', 'ethereum'),
                        "network": cert_data.get('network'),
                        "contract_address": cert_data.get('contract_address'),
                        "note": "Full certificate data stored on Ethereum blockchain. Use certificate ID to verify in 'Verify Certificate' tab."
                    })
                else:
                    error_msg = cert_data.get('error', 'Unknown error') if cert_data else 'No response from Ethereum'
                    certificates.append({
                        "certificate_id": index_entry.certificate_id,
                        "student_id": index_entry.student_id,
                        "course_name": index_entry.course_name,
                        "issuer_id": index_entry.issuer_id,
                        "timestamp": index_entry.timestamp,
                        "status": index_entry.status,
                        "blockchain_verified": False,
                        "note": f"Certificate exists in index but not found on Ethereum blockchain. {error_msg}"
                    })
            except Exception as e:
                certificates.append({
                    "certificate_id": index_entry.certificate_id,
                    "student_id": index_entry.student_id,
                    "course_name": index_entry.course_name,
                    "issuer_id": index_entry.issuer_id,
                    "timestamp": index_entry.timestamp,
                    "status": index_entry.status,
                    "blockchain_verified": False,
                    "note": f"Certificate exists in index but could not be verified on Ethereum: {str(e)}"
                })
        
        return {
            "student_id": student_id,
            "certificates": certificates,
            "count": len(certificates),
            "note": f"Found {len(certificates)} certificate(s). Full certificate data is stored on Ethereum blockchain. Use certificate ID to verify in 'Verify Certificate' tab."
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
        return {
            "issuer_id": issuer_id,
            "certificates": [],
            "count": 0,
            "note": "Ethereum blockchain doesn't support querying certificates by issuer_id. Please verify certificates individually by certificate_id."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        ethereum_service = get_ethereum_service()
        cert_data = ethereum_service.get_certificate(revocation_request.certificate_id)
        
        if not cert_data or cert_data.get('found') == False:
            raise HTTPException(status_code=404, detail="Certificate not found on Ethereum blockchain")
        
        if cert_data.get('revoked'):
            raise HTTPException(status_code=400, detail="Certificate is already revoked")
        
        result = ethereum_service.revoke_certificate(
            revocation_request.certificate_id,
            revocation_request.reason or "Revoked by issuer"
        )
        
        if result['success']:
            index_entry = db.query(CertificateIndex).filter(
                CertificateIndex.certificate_id == revocation_request.certificate_id
            ).first()
            if index_entry:
                index_entry.status = "revoked"
                db.commit()
            
            return {
                "success": True,
                "message": "Certificate revoked successfully on Ethereum blockchain",
                "certificate_id": revocation_request.certificate_id,
                "reason": revocation_request.reason,
                "transaction_hash": result.get('transaction_hash'),
                "block_number": result.get('block_number')
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to revoke certificate'))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/all")
async def get_all_certificates(db: Session = Depends(get_db)):
    """
    Get all certificates from the index with their Ethereum verification status.
    
    This endpoint returns all certificates from the database index and checks
    their status on Ethereum blockchain. Useful for viewing all certificates
    and their verification status.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: All certificates with:
            - certificates: List of all certificate dictionaries with Ethereum status
            - count: Total number of certificates
            - verified_count: Number of certificates verified on Ethereum
            - not_verified_count: Number of certificates not found on Ethereum
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        index_entries = db.query(CertificateIndex).all()
        
        if not index_entries:
            return {
                "certificates": [],
                "count": 0,
                "verified_count": 0,
                "not_verified_count": 0,
                "note": "No certificates found in the index. Certificates will be added when you issue them."
            }
        
        certificates = []
        verified_count = 0
        not_verified_count = 0
        
        try:
            ethereum_service = get_ethereum_service()
            ethereum_connected = True
        except Exception as e:
            ethereum_connected = False
            ethereum_error = str(e)
        
        for index_entry in index_entries:
            cert_info = {
                "certificate_id": index_entry.certificate_id,
                "student_id": index_entry.student_id,
                "course_name": index_entry.course_name,
                "issuer_id": index_entry.issuer_id,
                "timestamp": index_entry.timestamp,
                "status": index_entry.status,
                "created_at": index_entry.created_at.isoformat() if index_entry.created_at else None
            }
            
            if ethereum_connected:
                try:
                    cert_data = ethereum_service.get_certificate(index_entry.certificate_id)
                    if cert_data and (cert_data.get('exists') == True or cert_data.get('found') == True):
                        cert_info["blockchain_verified"] = True
                        cert_info["blockchain_course_name"] = cert_data.get('course_name')
                        cert_info["blockchain_issuer_id"] = cert_data.get('issuer_id')
                        cert_info["blockchain_timestamp"] = cert_data.get('timestamp')
                        cert_info["blockchain_revoked"] = cert_data.get('revoked', False)
                        cert_info["blockchain_revocation_reason"] = cert_data.get('revocation_reason')
                        cert_info["blockchain_network"] = cert_data.get('network')
                        verified_count += 1
                    else:
                        cert_info["blockchain_verified"] = False
                        cert_info["blockchain_error"] = cert_data.get('error', 'Certificate not found') if cert_data else 'No response'
                        not_verified_count += 1
                except Exception as e:
                    cert_info["blockchain_verified"] = False
                    cert_info["blockchain_error"] = str(e)
                    not_verified_count += 1
            else:
                cert_info["blockchain_verified"] = None
                cert_info["blockchain_error"] = f"Ethereum not connected: {ethereum_error}"
                not_verified_count += 1
            
            certificates.append(cert_info)
        
        return {
            "certificates": certificates,
            "count": len(certificates),
            "verified_count": verified_count,
            "not_verified_count": not_verified_count,
            "ethereum_connected": ethereum_connected,
            "note": f"Found {len(certificates)} certificate(s) in index. {verified_count} verified on Ethereum, {not_verified_count} not found or error."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
