# 🎓 Certificate Validation System

A blockchain-based platform for issuing, storing, and verifying academic certificates using **Ethereum blockchain**. Certificates are stored on Ethereum smart contracts, making them **immutable, tamper-proof, and verifiable**.

---

## 📖 About This Project

This system allows educational institutions to issue digital certificates on the Ethereum blockchain. Students can verify their certificates instantly without contacting the issuer, and all certificate data is stored immutably on the blockchain.

### Key Features
- ✅ Issue certificates on Ethereum blockchain
- ✅ Verify certificates instantly
- ✅ View student portfolio with all courses
- ✅ Revoke certificates if needed
- ✅ Privacy-preserving (only PII hashes on blockchain)
- ✅ Tamper-proof storage

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** and **npm** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd certificate-validation-system
```

### Step 2: Install Dependencies

Install dependencies for all three parts of the project:

**Backend (Python):**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
cd ../frontend
npm install
```

**Smart Contracts (Node.js):**
```bash
cd ../contracts
npm install
```

### Step 3: Configure Environment Variables

**Backend Configuration:**

You can use the helper script to create the `.env` file:
```bash
cd backend
python create_env.py
```

Or manually create `backend/.env`:
```env
DATABASE_URL=sqlite:///./certificates.db
SECRET_KEY=your-secret-key-here-change-this
ETHEREUM_NETWORK=hardhat
CONTRACT_ADDRESS=
ETHEREUM_PRIVATE_KEY=
HARDHAT_RPC_URL=http://127.0.0.1:8545
```

**Frontend Configuration:**

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_USE_ETHEREUM=true
VITE_ETHEREUM_CONTRACT_ADDRESS=
VITE_ETHEREUM_NETWORK=hardhat
```

> **Note:** Leave `CONTRACT_ADDRESS` and `VITE_ETHEREUM_CONTRACT_ADDRESS` empty for now. You'll fill them in after deploying the contract.

### Step 4: Start the Local Blockchain (Hardhat)

Open **Terminal 1** and start the Hardhat local blockchain:
```bash
cd contracts
npx hardhat node
```

Keep this terminal running! You should see a list of accounts with private keys and ETH balances.

### Step 5: Deploy the Smart Contract

Open **Terminal 2** and deploy the contract:
```bash
cd contracts
npx hardhat run scripts/deploy.js --network localhost
```

You'll see output like:
```
CertificateVerifier deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

**Copy the contract address** and update:
1. `backend/.env` - Set `CONTRACT_ADDRESS=0x...`
2. `frontend/.env` - Set `VITE_ETHEREUM_CONTRACT_ADDRESS=0x...`

### Step 6: Initialize the Database

The database will be automatically created when you start the backend, but you can also initialize it manually:
```bash
cd backend
python -m app.init_db
```

### Step 7: Start the Backend Server

Open **Terminal 3** and start the FastAPI backend:
```bash
cd backend
python run.py
```

Or using uvicorn directly:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

The backend will be available at: http://localhost:8000

### Step 8: Start the Frontend

Open **Terminal 4** and start the React frontend:
```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173 (or the port shown in the terminal)

### Step 9: Access the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs:** http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Database Issues
- If you get database errors, delete `backend/certificates.db` and restart the backend (it will recreate the database)
- Or manually initialize: `cd backend && python -m app.init_db`

### Port Already in Use
- Backend (8000): Change port in `backend/run.py` or use: `uvicorn app.main:app --port 8001`
- Frontend (5173): Vite will automatically use the next available port
- Hardhat (8545): Stop any other Hardhat nodes or change the port in `contracts/hardhat.config.js`

### Contract Deployment Issues
- Make sure Hardhat node is running before deploying
- Check that `ETHEREUM_PRIVATE_KEY` in `backend/.env` matches one of the Hardhat accounts
- Verify the contract address is correctly set in both `.env` files

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`
- Check browser console for CORS errors

### Module Not Found Errors
- Make sure you've installed all dependencies in all three directories
- For Python: `pip install -r requirements.txt` in `backend/`
- For Node.js: `npm install` in both `frontend/` and `contracts/`

### Environment Variables Not Loading
- Ensure `.env` files are in the correct directories (`backend/.env` and `frontend/.env`)
- Restart the servers after changing `.env` files
- Check for typos in variable names

---

## ⚡ Quick Reference

**Start all services (4 terminals required):**

```bash
# Terminal 1: Start Hardhat blockchain
cd contracts && npx hardhat node

# Terminal 2: Deploy contract (after Terminal 1 is running)
cd contracts && npx hardhat run scripts/deploy.js --network localhost
# Copy contract address to backend/.env and frontend/.env

# Terminal 3: Start backend
cd backend && python run.py

# Terminal 4: Start frontend
cd frontend && npm run dev
```

**Default URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📚 Documentation

For detailed information about:
- How the system works
- Complete setup guide
- All features and implementation details

See **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)**

---

## 🛠️ Technology Stack

- **Backend:** FastAPI, Python, SQLite, Web3.py
- **Frontend:** React, Vite, ethers.js
- **Blockchain:** Solidity, Hardhat, Ethereum

---

## 📄 License

MIT License

---

**Built with ❤️ for secure certificate validation on Ethereum!**
