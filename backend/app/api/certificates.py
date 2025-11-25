from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..models.certificate import Certificate
from ..models.blockchain import blockchain

router = APIRouter(prefix="/certificates", tags=["certificates"])

# Pydantic models for request/response
class CertificateRequest(BaseModel):
    student_name: str
    student_id: str
    course_name: str
    grade: str
    issuer_name: str
    issuer_id: str
    course_duration: str = None

class VerificationRequest(BaseModel):
    certificate_id: str

class RevocationRequest(BaseModel):
    certificate_id: str
    reason: str = None

@router.post("/issue")
async def issue_certificate(cert_request: CertificateRequest):
    """Issue a new certificate"""
    try:
        # Create certificate object
        certificate = Certificate(
            student_name=cert_request.student_name,
            student_id=cert_request.student_id,
            course_name=cert_request.course_name,
            grade=cert_request.grade,
            issuer_name=cert_request.issuer_name,
            issuer_id=cert_request.issuer_id,
            course_duration=cert_request.course_duration
        )
        
        # Add to blockchain
        result = blockchain.add_certificate(certificate.to_dict())
        
        if result['success']:
            return {
                "success": True,
                "message": "Certificate issued successfully",
                "certificate_id": certificate.certificate_id,
                "certificate": certificate.to_dict(),
                "blockchain_info": {
                    "block_index": result['block_index'],
                    "block_hash": result['block_hash']
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_certificate(verification_request: VerificationRequest):
    """Verify a certificate"""
    try:
        result = blockchain.verify_certificate(verification_request.certificate_id)
        
        if result['found']:
            return {
                "verified": True,
                "valid": result['valid'],
                "certificate": result['certificate'],
                "blockchain_proof": {
                    "block_index": result['block_index'],
                    "block_hash": result['block_hash'],
                    "timestamp": result['timestamp']
                }
            }
        else:
            return {
                "verified": False,
                "valid": False,
                "message": "Certificate not found"
            }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/student/{student_id}")
async def get_student_certificates(student_id: str):
    """Get all certificates for a specific student"""
    try:
        certificates = blockchain.get_certificates_by_student(student_id)
        return {
            "student_id": student_id,
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/issuer/{issuer_id}")
async def get_issuer_certificates(issuer_id: str):
    """Get all certificates issued by a specific institution"""
    try:
        certificates = blockchain.get_certificates_by_issuer(issuer_id)
        return {
            "issuer_id": issuer_id,
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/revoke")
async def revoke_certificate(revocation_request: RevocationRequest):
    """Revoke a certificate"""
    try:
        result = blockchain.revoke_certificate(revocation_request.certificate_id)
        
        if result['success']:
            return {
                "success": True,
                "message": "Certificate revoked successfully",
                "certificate_id": revocation_request.certificate_id,
                "reason": revocation_request.reason
            }
        else:
            raise HTTPException(status_code=404, detail=result['message'])
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/all")
async def get_all_certificates():
    """Get all certificates (for demo purposes)"""
    try:
        certificates = blockchain.get_all_certificates()
        return {
            "certificates": certificates,
            "count": len(certificates)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
