import hashlib
import json
import time
from typing import Dict
from datetime import datetime

class Certificate:
    """Certificate class for academic certificates"""
    
    def __init__(self, student_name: str, student_id: str, course_name: str, 
                 grade: str, issuer_name: str, issuer_id: str, 
                 course_duration: str = None, issue_date: str = None):
        self.student_name = student_name
        self.student_id = student_id
        self.course_name = course_name
        self.grade = grade
        self.issuer_name = issuer_name
        self.issuer_id = issuer_id
        self.course_duration = course_duration or "N/A"
        self.issue_date = issue_date or datetime.now().strftime("%Y-%m-%d")
        self.timestamp = time.time()
        self.certificate_id = self.generate_certificate_id()
        self.status = "active"  # active, revoked, expired
    
    def generate_certificate_id(self) -> str:
        """Generate unique certificate ID using SHA-256"""
        cert_string = f"{self.student_id}_{self.course_name}_{self.timestamp}"
        return hashlib.sha256(cert_string.encode()).hexdigest()[:16].upper()
    
    def to_dict(self) -> Dict:
        """Convert certificate to dictionary for blockchain storage"""
        return {
            'certificate_id': self.certificate_id,
            'student_name': self.student_name,
            'student_id': self.student_id,
            'course_name': self.course_name,
            'grade': self.grade,
            'issuer_name': self.issuer_name,
            'issuer_id': self.issuer_id,
            'course_duration': self.course_duration,
            'issue_date': self.issue_date,
            'timestamp': self.timestamp,
            'status': self.status
        }
    
    def revoke(self) -> None:
        """Revoke the certificate"""
        self.status = "revoked"
    
    def is_valid(self) -> bool:
        """Check if certificate is valid"""
        return self.status == "active"
    
    def __str__(self) -> str:
        return f"Certificate: {self.student_name} - {self.course_name} ({self.grade})"
