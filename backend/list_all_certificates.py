"""
Script to list all certificates from the database index and check their status on Ethereum.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.db_models import CertificateIndex
from app.services.ethereum_helper import get_ethereum_service

def list_all_certificates():
    """List all certificates from index and check their Ethereum status."""
    db = SessionLocal()
    
    try:
        # Initialize database tables if needed
        try:
            from app.database import init_db
            init_db()
        except Exception as e:
            print(f"Note: Database initialization: {e}")
        
        # Get all certificate index entries
        try:
            index_entries = db.query(CertificateIndex).all()
        except Exception as e:
            if 'no such table' in str(e).lower():
                print("⚠️  Certificate index table does not exist yet.")
                print("   This table is created automatically when you issue your first certificate.")
                print("   Issue a certificate to create the index table.\n")
                return
            else:
                raise
        
        if not index_entries:
            print("No certificates found in the database index.")
            print("Certificates will be added to the index when you issue them.\n")
            return
        
        print(f"\n{'='*80}")
        print(f"Certificate Index: {len(index_entries)} certificate(s) found")
        print(f"{'='*80}\n")
        
        # Get Ethereum service
        try:
            ethereum_service = get_ethereum_service()
            print("✅ Connected to Ethereum network\n")
        except Exception as e:
            print(f"❌ Failed to connect to Ethereum: {e}\n")
            ethereum_service = None
        
        # Check each certificate
        verified_count = 0
        not_verified_count = 0
        
        for idx, entry in enumerate(index_entries, 1):
            print(f"{'─'*80}")
            print(f"Certificate #{idx}")
            print(f"{'─'*80}")
            print(f"Certificate ID: {entry.certificate_id}")
            print(f"Student ID:     {entry.student_id}")
            print(f"Course Name:    {entry.course_name}")
            print(f"Issuer ID:      {entry.issuer_id}")
            print(f"Status:         {entry.status}")
            print(f"Issued:         {entry.timestamp} ({entry.created_at})")
            
            # Check on Ethereum
            if ethereum_service:
                try:
                    cert_data = ethereum_service.get_certificate(entry.certificate_id)
                    if cert_data and (cert_data.get('exists') == True or cert_data.get('found') == True):
                        print(f"Ethereum:       ✅ VERIFIED")
                        print(f"  - Course:     {cert_data.get('course_name', 'N/A')}")
                        print(f"  - Issuer:      {cert_data.get('issuer_id', 'N/A')}")
                        print(f"  - Timestamp:   {cert_data.get('timestamp', 'N/A')}")
                        print(f"  - Revoked:     {'Yes' if cert_data.get('revoked') else 'No'}")
                        if cert_data.get('revoked') and cert_data.get('revocation_reason'):
                            print(f"  - Reason:      {cert_data.get('revocation_reason')}")
                        verified_count += 1
                    else:
                        print(f"Ethereum:       ❌ NOT FOUND")
                        error = cert_data.get('error', 'Unknown error') if cert_data else 'No response'
                        print(f"  - Error:       {error}")
                        not_verified_count += 1
                except Exception as e:
                    print(f"Ethereum:       ❌ ERROR")
                    print(f"  - Error:       {str(e)}")
                    not_verified_count += 1
            else:
                print(f"Ethereum:       ⚠️  Cannot check (Ethereum not connected)")
                not_verified_count += 1
            
            print()
        
        # Summary
        print(f"{'='*80}")
        print(f"Summary:")
        print(f"  Total certificates in index: {len(index_entries)}")
        if ethereum_service:
            print(f"  ✅ Verified on Ethereum:     {verified_count}")
            print(f"  ❌ Not found on Ethereum:     {not_verified_count}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_all_certificates()

