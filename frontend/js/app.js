// Certificate Validation System - Frontend JavaScript

// Configuration
const API_BASE = 'http://localhost:8000';

// DOM Elements
let currentTab = 'issue';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up tab navigation
    setupTabNavigation();
    
    // Set up form event listeners
    setupFormListeners();
    
    // Load initial data
    loadBlockchainInfo();
}

// Tab Navigation
function setupTabNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update active tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    
    currentTab = tabName;
}

// Form Event Listeners
function setupFormListeners() {
    // Issue Certificate Form
    document.getElementById('issueForm').addEventListener('submit', handleIssueCertificate);
    
    // Verify Certificate Form
    document.getElementById('verifyForm').addEventListener('submit', handleVerifyCertificate);
    
    // Student Portfolio Form
    document.getElementById('studentForm').addEventListener('submit', handleViewStudentCertificates);
}

// Issue Certificate
async function handleIssueCertificate(e) {
    e.preventDefault();
    
    const formData = {
        student_name: document.getElementById('studentName').value,
        student_id: document.getElementById('studentId').value,
        course_name: document.getElementById('courseName').value,
        grade: document.getElementById('grade').value,
        issuer_name: document.getElementById('issuerName').value,
        issuer_id: document.getElementById('issuerId').value,
        course_duration: document.getElementById('courseDuration').value
    };
    
    showLoading('issueResult', 'Issuing certificate...');
    
    try {
        const response = await fetch(`${API_BASE}/certificates/issue`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('issueResult', `
                <h3>✅ Certificate Issued Successfully!</h3>
                <div class="certificate">
                    <div class="certificate-details">
                        <div><strong>Student:</strong> ${result.certificate.student_name}</div>
                        <div><strong>Student ID:</strong> ${result.certificate.student_id}</div>
                        <div><strong>Course:</strong> ${result.certificate.course_name}</div>
                        <div><strong>Grade:</strong> ${result.certificate.grade}</div>
                        <div><strong>Issuer:</strong> ${result.certificate.issuer_name}</div>
                        <div><strong>Duration:</strong> ${result.certificate.course_duration}</div>
                    </div>
                    <div class="certificate-id">
                        <strong>Certificate ID:</strong> ${result.certificate.certificate_id}
                    </div>
                </div>
                <p><strong>Blockchain Info:</strong> Block ${result.blockchain_info.block_index} | Hash: ${result.blockchain_info.block_hash.substring(0, 20)}...</p>
            `);
            document.getElementById('issueForm').reset();
        } else {
            showError('issueResult', `Error: ${result.message}`);
        }
    } catch (error) {
        showError('issueResult', `Network Error: ${error.message}`);
    }
}

// Verify Certificate
async function handleVerifyCertificate(e) {
    e.preventDefault();
    
    const certificateId = document.getElementById('certificateId').value;
    
    showLoading('verifyResult', 'Verifying certificate...');
    
    try {
        const response = await fetch(`${API_BASE}/certificates/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ certificate_id: certificateId })
        });
        
        const result = await response.json();
        
        if (result.verified && result.valid) {
            showSuccess('verifyResult', `
                <h3>✅ Certificate Verified Successfully!</h3>
                <div class="certificate">
                    <div class="certificate-details">
                        <div><strong>Student:</strong> ${result.certificate.student_name}</div>
                        <div><strong>Student ID:</strong> ${result.certificate.student_id}</div>
                        <div><strong>Course:</strong> ${result.certificate.course_name}</div>
                        <div><strong>Grade:</strong> ${result.certificate.grade}</div>
                        <div><strong>Issuer:</strong> ${result.certificate.issuer_name}</div>
                        <div><strong>Issue Date:</strong> ${new Date(result.certificate.timestamp * 1000).toLocaleDateString()}</div>
                    </div>
                    <div class="certificate-id">
                        <strong>Certificate ID:</strong> ${result.certificate.certificate_id}
                    </div>
                </div>
                <p><strong>Blockchain Proof:</strong> Block ${result.blockchain_proof.block_index} | Hash: ${result.blockchain_proof.block_hash.substring(0, 20)}...</p>
            `);
        } else if (result.verified && !result.valid) {
            showError('verifyResult', '❌ Certificate found but has been revoked or is invalid.');
        } else {
            showError('verifyResult', '❌ Certificate not found in the blockchain.');
        }
    } catch (error) {
        showError('verifyResult', `Network Error: ${error.message}`);
    }
}

// View Student Certificates
async function handleViewStudentCertificates(e) {
    e.preventDefault();
    
    const studentId = document.getElementById('viewStudentId').value;
    
    showLoading('studentResult', 'Loading student certificates...');
    
    try {
        const response = await fetch(`${API_BASE}/certificates/student/${studentId}`);
        const result = await response.json();
        
        if (result.certificates.length > 0) {
            let html = `<h3>📚 Found ${result.count} certificate(s) for Student ID: ${result.student_id}</h3>`;
            
            result.certificates.forEach((cert, index) => {
                html += `
                    <div class="certificate">
                        <h4>Certificate ${index + 1}</h4>
                        <div class="certificate-details">
                            <div><strong>Course:</strong> ${cert.course_name}</div>
                            <div><strong>Grade:</strong> ${cert.grade}</div>
                            <div><strong>Issuer:</strong> ${cert.issuer_name}</div>
                            <div><strong>Issue Date:</strong> ${new Date(cert.timestamp * 1000).toLocaleDateString()}</div>
                            <div><strong>Status:</strong> <span style="color: ${cert.status === 'active' ? 'green' : 'red'}">${cert.status.toUpperCase()}</span></div>
                        </div>
                        <div class="certificate-id">
                            <strong>Certificate ID:</strong> ${cert.certificate_id}
                        </div>
                    </div>
                `;
            });
            
            showSuccess('studentResult', html);
        } else {
            showError('studentResult', `No certificates found for Student ID: ${studentId}`);
        }
    } catch (error) {
        showError('studentResult', `Network Error: ${error.message}`);
    }
}

// Blockchain Functions
async function loadBlockchainInfo() {
    try {
        const response = await fetch(`${API_BASE}/blockchain/info`);
        const result = await response.json();
        
        if (result.success) {
            const info = result.blockchain_info;
            showInfo('blockchainResult', `
                <h3>🔗 Blockchain Information</h3>
                <div class="certificate">
                    <div class="certificate-details">
                        <div><strong>Total Blocks:</strong> ${info.total_blocks}</div>
                        <div><strong>Total Certificates:</strong> ${info.total_certificates}</div>
                        <div><strong>Active Certificates:</strong> ${info.active_certificates}</div>
                        <div><strong>Revoked Certificates:</strong> ${info.revoked_certificates}</div>
                        <div><strong>Chain Length:</strong> ${info.chain_length}</div>
                    </div>
                    <div class="certificate-id">
                        <strong>Latest Block Hash:</strong> ${info.latest_block_hash.substring(0, 30)}...
                    </div>
                </div>
            `);
        }
    } catch (error) {
        console.error('Error loading blockchain info:', error);
    }
}

async function validateBlockchain() {
    showLoading('blockchainResult', 'Validating blockchain integrity...');
    
    try {
        const response = await fetch(`${API_BASE}/blockchain/validate`);
        const result = await response.json();
        
        if (result.success) {
            if (result.valid) {
                showSuccess('blockchainResult', `
                    <h3>✅ Blockchain Validation Successful!</h3>
                    <p>${result.message}</p>
                `);
            } else {
                showError('blockchainResult', `
                    <h3>❌ Blockchain Validation Failed!</h3>
                    <p>${result.message}</p>
                `);
            }
        }
    } catch (error) {
        showError('blockchainResult', `Network Error: ${error.message}`);
    }
}

async function loadAllCertificates() {
    showLoading('blockchainResult', 'Loading all certificates...');
    
    try {
        const response = await fetch(`${API_BASE}/certificates/all`);
        const result = await response.json();
        
        if (result.certificates.length > 0) {
            let html = `<h3>📋 All Certificates (${result.count})</h3>`;
            
            result.certificates.forEach((cert, index) => {
                html += `
                    <div class="certificate">
                        <h4>Certificate ${index + 1}</h4>
                        <div class="certificate-details">
                            <div><strong>Student:</strong> ${cert.student_name} (${cert.student_id})</div>
                            <div><strong>Course:</strong> ${cert.course_name}</div>
                            <div><strong>Grade:</strong> ${cert.grade}</div>
                            <div><strong>Issuer:</strong> ${cert.issuer_name}</div>
                            <div><strong>Issue Date:</strong> ${new Date(cert.timestamp * 1000).toLocaleDateString()}</div>
                            <div><strong>Status:</strong> <span style="color: ${cert.status === 'active' ? 'green' : 'red'}">${cert.status.toUpperCase()}</span></div>
                        </div>
                        <div class="certificate-id">
                            <strong>Certificate ID:</strong> ${cert.certificate_id}
                        </div>
                    </div>
                `;
            });
            
            showSuccess('blockchainResult', html);
        } else {
            showError('blockchainResult', 'No certificates found in the blockchain.');
        }
    } catch (error) {
        showError('blockchainResult', `Network Error: ${error.message}`);
    }
}

// Utility Functions
function showLoading(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="result info">
            <div class="loading"></div> ${message}
        </div>
    `;
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="result success">${message}</div>`;
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="result error">${message}</div>`;
}

function showInfo(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="result info">${message}</div>`;
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}
