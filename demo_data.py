#!/usr/bin/env python3
"""
Certificate Validation System - Demo Data Script
This script creates sample certificates for demonstration purposes.
"""

import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8000"

# Sample certificate data
DEMO_CERTIFICATES = [
    {
        "student_name": "John Doe",
        "student_id": "STU001",
        "course_name": "Computer Science",
        "grade": "A+",
        "issuer_name": "Massachusetts Institute of Technology",
        "issuer_id": "MIT001",
        "course_duration": "4 years"
    },
    {
        "student_name": "Jane Smith",
        "student_id": "STU002",
        "course_name": "Data Science",
        "grade": "A",
        "issuer_name": "Stanford University",
        "issuer_id": "STAN001",
        "course_duration": "2 years"
    },
    {
        "student_name": "Mike Johnson",
        "student_id": "STU003",
        "course_name": "Artificial Intelligence",
        "grade": "A+",
        "issuer_name": "Carnegie Mellon University",
        "issuer_id": "CMU001",
        "course_duration": "3 years"
    },
    {
        "student_name": "Sarah Wilson",
        "student_id": "STU004",
        "course_name": "Cybersecurity",
        "grade": "B+",
        "issuer_name": "University of California, Berkeley",
        "issuer_id": "UCB001",
        "course_duration": "2 years"
    },
    {
        "student_name": "David Brown",
        "student_id": "STU005",
        "course_name": "Software Engineering",
        "grade": "A",
        "issuer_name": "Georgia Institute of Technology",
        "issuer_id": "GIT001",
        "course_duration": "4 years"
    }
]

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def issue_certificate(cert_data):
    """Issue a certificate"""
    try:
        response = requests.post(
            f"{API_BASE}/certificates/issue",
            json=cert_data,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main function to create demo data"""
    print("🎓 Certificate Validation System - Demo Data Creator")
    print("=" * 50)
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the server first using: python start.py")
        return
    
    print("✅ Server is running!")
    
    # Issue demo certificates
    print("\n📜 Creating demo certificates...")
    issued_certificates = []
    
    for i, cert_data in enumerate(DEMO_CERTIFICATES, 1):
        print(f"Creating certificate {i}/{len(DEMO_CERTIFICATES)}: {cert_data['student_name']} - {cert_data['course_name']}")
        
        result = issue_certificate(cert_data)
        
        if "error" in result:
            print(f"❌ Failed to create certificate: {result['error']}")
        elif result.get("success"):
            certificate_id = result["certificate_id"]
            issued_certificates.append({
                "student_name": cert_data["student_name"],
                "student_id": cert_data["student_id"],
                "course_name": cert_data["course_name"],
                "certificate_id": certificate_id
            })
            print(f"✅ Certificate created: {certificate_id}")
        else:
            print(f"❌ Failed to create certificate: {result.get('message', 'Unknown error')}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Display summary
    print("\n🎉 Demo data creation complete!")
    print("=" * 50)
    print(f"✅ Successfully created {len(issued_certificates)} certificates")
    
    if issued_certificates:
        print("\n📋 Created Certificates:")
        for cert in issued_certificates:
            print(f"  • {cert['student_name']} ({cert['student_id']}) - {cert['course_name']}")
            print(f"    Certificate ID: {cert['certificate_id']}")
        
        print("\n🧪 You can now test the system:")
        print("1. Open the frontend in your browser")
        print("2. Try verifying any of the certificate IDs above")
        print("3. View student portfolios using the student IDs")
        print("4. Check blockchain information")
        
        # Save certificate IDs to file for easy reference
        with open("demo_certificate_ids.txt", "w") as f:
            f.write("Demo Certificate IDs for Testing\n")
            f.write("=" * 40 + "\n\n")
            for cert in issued_certificates:
                f.write(f"Student: {cert['student_name']} ({cert['student_id']})\n")
                f.write(f"Course: {cert['course_name']}\n")
                f.write(f"Certificate ID: {cert['certificate_id']}\n")
                f.write("-" * 40 + "\n")
        
        print(f"\n💾 Certificate IDs saved to: demo_certificate_ids.txt")

if __name__ == "__main__":
    main()
