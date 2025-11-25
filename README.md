# 🎓 Certificate Validation System

A blockchain-based system for issuing, storing, and verifying academic certificates with cryptographic security and instant verification.

## 🚀 Features

- **Certificate Issuance** - Educational institutions can issue digital certificates
- **Instant Verification** - Employers can verify certificates without contacting the issuer
- **Tamper-Proof Storage** - Certificates are stored on an immutable blockchain
- **Student Portfolio** - Students can view all their certificates
- **Cryptographic Security** - SHA-256 hashing ensures data integrity
- **Web Interface** - Clean, modern UI for all stakeholders

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Blockchain    │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)     │◄──►│   (Custom)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
blockchain/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Data models (Block, Certificate, Blockchain)
│   │   ├── api/           # API routes
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── README.md         # Backend documentation
├── frontend/              # Web frontend
│   ├── index.html        # Main HTML file
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── app.js        # JavaScript functionality
├── docs/
│   └── API.md           # API documentation
└── README.md            # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Modern web browser

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server:**
   ```bash
   # Option 1: Using the run script (recommended)
   python run.py
   
   # Option 2: Using uvicorn directly
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Option 3: Using python module (legacy)
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Open the frontend:**
   - Navigate to the `frontend` directory
   - Open `index.html` in your web browser
   - Or serve it using a local server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```
     Then visit `http://localhost:3000`

## 🎯 How to Use

### 1. Issue a Certificate
- Go to the "Issue Certificate" tab
- Fill in student and course details
- Click "Issue Certificate"
- Copy the generated Certificate ID

### 2. Verify a Certificate
- Go to the "Verify Certificate" tab
- Enter the Certificate ID
- Click "Verify Certificate"
- View the verification result

### 3. View Student Portfolio
- Go to the "Student Portfolio" tab
- Enter a Student ID
- View all certificates for that student

### 4. Blockchain Information
- Go to the "Blockchain Info" tab
- View blockchain statistics
- Validate blockchain integrity
- See all certificates in the system

## 🔧 API Endpoints

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

## 🔒 Security Features

- **Cryptographic Hashing** - SHA-256 for data integrity
- **Immutable Records** - Once added, certificates cannot be modified
- **Blockchain Validation** - Continuous integrity checking
- **Unique Certificate IDs** - Generated using student data + timestamp

## 🎨 Frontend Features

- **Responsive Design** - Works on desktop and mobile
- **Modern UI** - Clean, professional interface
- **Real-time Feedback** - Loading states and success/error messages
- **Tab Navigation** - Easy switching between functions
- **Certificate Display** - Formatted certificate information

## 🧪 Testing

### Manual Testing
1. Issue a certificate
2. Verify the certificate using its ID
3. View student portfolio
4. Check blockchain information

### API Testing
Use the Swagger UI at `http://localhost:8000/docs` to test API endpoints directly.

## 🚀 Deployment

### Development
- Backend: `cd backend && python run.py` or `uvicorn app.main:app --reload`
- Frontend: Open `index.html` in browser

### Production
- Use a production WSGI server like Gunicorn
- Serve frontend through a web server like Nginx
- Implement proper authentication and rate limiting
- Use a production database

## 🔮 Future Enhancements

- **Mobile App** - React Native or Flutter app
- **QR Code Integration** - Generate and scan QR codes
- **Digital Signatures** - RSA signatures for additional security
- **Batch Processing** - Issue multiple certificates at once
- **Email Notifications** - Notify students when certificates are issued
- **Advanced Analytics** - Certificate statistics and reporting
- **Multi-language Support** - Internationalization
- **Integration APIs** - Connect with existing systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation in `docs/API.md`
2. Review the backend README in `backend/README.md`
3. Open an issue on GitHub

## 🎉 Demo

Try the system with these sample data:

**Issue Certificate:**
- Student Name: John Doe
- Student ID: STU001
- Course Name: Computer Science
- Grade: A+
- Issuer Name: MIT
- Issuer ID: MIT001

**Verify Certificate:**
- Use the Certificate ID generated from the issuance

---

**Built with ❤️ for the 24-hour hackathon!**
