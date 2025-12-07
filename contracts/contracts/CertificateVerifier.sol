// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CertificateVerifier
 * @dev Smart contract for verifying academic certificates on Ethereum
 * @notice Stores certificate hashes (PII hashes) on-chain for tamper-proof verification
 */
contract CertificateVerifier {
    event CertificateIssued(
        bytes32 indexed certificateId,
        bytes32 indexed piiHash,
        address indexed issuer,
        uint256 timestamp,
        string courseName,
        string issuerId
    );
    
    event CertificateRevoked(
        bytes32 indexed certificateId,
        address indexed issuer,
        uint256 timestamp,
        string reason
    );
    
    struct Certificate {
        bytes32 certificateId;
        bytes32 piiHash;
        address issuer;
        uint256 timestamp;
        bool revoked;
        string courseName;
        string issuerId;
        string revocationReason;
    }
    
    mapping(bytes32 => Certificate) public certificates;
    
    mapping(address => bool) public authorizedIssuers;
    
    address public owner;
    
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    modifier onlyAuthorizedIssuer() {
        require(
            authorizedIssuers[msg.sender] || msg.sender == owner,
            "Only authorized issuers can perform this action"
        );
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
    }
    
    
    /**
     * @dev Issue a new certificate on the blockchain
     * @param certificateId Unique certificate identifier (hashed)
     * @param piiHash SHA-256 hash of PII (student name, student ID, grade)
     * @param courseName Name of the course (public information)
     * @param issuerId Institution identifier
     */
    function issueCertificate(
        bytes32 certificateId,
        bytes32 piiHash,
        string memory courseName,
        string memory issuerId
    ) public onlyAuthorizedIssuer {
        require(
            certificates[certificateId].certificateId == bytes32(0),
            "Certificate already exists"
        );
        
        certificates[certificateId] = Certificate({
            certificateId: certificateId,
            piiHash: piiHash,
            issuer: msg.sender,
            timestamp: block.timestamp,
            revoked: false,
            courseName: courseName,
            issuerId: issuerId,
            revocationReason: ""
        });
        
        emit CertificateIssued(
            certificateId,
            piiHash,
            msg.sender,
            block.timestamp,
            courseName,
            issuerId
        );
    }
    
    
    /**
     * @dev Verify a certificate's authenticity
     * @param certificateId Unique certificate identifier
     * @param piiHash SHA-256 hash of PII to verify against
     * @return valid True if certificate exists, matches PII hash, and is not revoked
     * @return issuer Address of the issuing institution
     * @return timestamp Block timestamp when certificate was issued
     * @return revoked True if certificate has been revoked
     */
    function verifyCertificate(bytes32 certificateId, bytes32 piiHash)
        public
        view
        returns (
            bool valid,
            address issuer,
            uint256 timestamp,
            bool revoked
        )
    {
        Certificate memory cert = certificates[certificateId];
        
        if (cert.certificateId == bytes32(0)) {
            return (false, address(0), 0, false);
        }
        
        bool hashMatches = (cert.piiHash == piiHash);
        
        valid = hashMatches && !cert.revoked;
        issuer = cert.issuer;
        timestamp = cert.timestamp;
        revoked = cert.revoked;
    }
    
    /**
     * @dev Get certificate information
     * @param certificateId Unique certificate identifier
     * @return cert Certificate struct with all information
     */
    function getCertificate(bytes32 certificateId)
        public
        view
        returns (Certificate memory cert)
    {
        require(
            certificates[certificateId].certificateId != bytes32(0),
            "Certificate does not exist"
        );
        return certificates[certificateId];
    }
    
    
    /**
     * @dev Revoke a certificate
     * @param certificateId Unique certificate identifier
     * @param reason Reason for revocation
     */
    function revokeCertificate(bytes32 certificateId, string memory reason)
        public
        onlyAuthorizedIssuer
    {
        Certificate storage cert = certificates[certificateId];
        require(
            cert.certificateId != bytes32(0),
            "Certificate does not exist"
        );
        require(
            cert.issuer == msg.sender || msg.sender == owner,
            "Only issuer or owner can revoke"
        );
        require(!cert.revoked, "Certificate already revoked");
        
        cert.revoked = true;
        cert.revocationReason = reason;
        
        emit CertificateRevoked(certificateId, msg.sender, block.timestamp, reason);
    }
    
    
    /**
     * @dev Authorize a new issuer address
     * @param issuer Address to authorize
     */
    function authorizeIssuer(address issuer) public onlyOwner {
        authorizedIssuers[issuer] = true;
    }
    
    /**
     * @dev Revoke authorization from an issuer
     * @param issuer Address to revoke authorization from
     */
    function revokeIssuer(address issuer) public onlyOwner {
        authorizedIssuers[issuer] = false;
    }
    
    
    /**
     * @dev Check if an address is authorized to issue certificates
     * @param issuer Address to check
     * @return True if authorized
     */
    function isAuthorizedIssuer(address issuer) public view returns (bool) {
        return authorizedIssuers[issuer] || issuer == owner;
    }
    
    /**
     * @dev Check if a certificate exists
     * @param certificateId Unique certificate identifier
     * @return True if certificate exists
     */
    function certificateExists(bytes32 certificateId) public view returns (bool) {
        return certificates[certificateId].certificateId != bytes32(0);
    }
}

