# Certificate Validation System - User Guide

## 🎓 How to Use the Application

### Step-by-Step Guide

---

## 1️⃣ **Register an Account**

To issue certificates, you need to register as an **Institution** or **Admin**.

### Registration Steps:

1. **Open the application** in your browser (usually `http://localhost:3000`)

2. **Click on "Login/Register"** tab (if not already selected)

3. **Click the "Register" tab** in the authentication form

4. **Fill in the registration form:**
   - **Username**: Choose a unique username
   - **Email**: Enter your email address
   - **Password**: At least 6 characters (maximum 72 bytes)
   - **Role**: **Select "Institution"** or **"Admin"** (NOT "Student")
   - **Issuer ID**: (Required for Institution) - Enter a unique identifier (e.g., "UNI001")
   - **Issuer Name**: (Required for Institution) - Enter your institution name (e.g., "University of Technology")

5. **Click "Register"**

6. **After successful registration**, you'll be automatically logged in! You'll see:
   - ✅ "Registration successful! Logging you in..." message
   - ✅ "Registration and login successful!" message
   - You'll be automatically redirected to the appropriate page based on your role
   - **No need to manually login** - you're already authenticated!

---

## 2️⃣ **Login**

**Note:** If you just registered, you're already logged in! Skip this step.

1. **Enter your username and password** in the Login form

2. **Click "Login"**

3. **After successful login**, you'll see:
   - Your username and role displayed in the header (e.g., "Logged in as: john (institution)")
   - The **"Issue Certificate"** tab will now appear in the navigation menu (if you're an institution/admin)
   - You'll be automatically taken to the appropriate page based on your role:
     - **Institutions/Admins** → "Issue Certificate" tab
     - **Students** → "Verify Certificate" tab

4. **To Logout**: Click the "Logout" button in the header (top right)

---

## 3️⃣ **Issue a Certificate**

Once logged in as an Institution or Admin:

1. **Click on "Issue Certificate"** tab (should be visible and active)

2. **Fill in the certificate form:**
   - **Student Name**: Full name of the student
   - **Student ID**: Unique student identifier
   - **Course Name**: Name of the course/degree
   - **Grade**: Select from dropdown (A+, A, B+, B, C+, C, D, F)
   - **Course Duration**: (Optional) e.g., "4 years", "6 months"

3. **Click "Issue Certificate"**

4. **After successful issuance**, you'll see:
   - ✅ Success message
   - Certificate details including:
     - Certificate ID (save this for verification)
     - Blockchain information (Block number, Hash)
     - Digital signature status
   - **Note**: If this is your first certificate, you'll see a note that the Genesis block (Block 0) was created automatically. This is normal - every blockchain needs a starting point!

---

## 4️⃣ **Revoke a Certificate**

Once logged in as an Institution or Admin:

1. **Click on "Revoke Certificate"** tab (should be visible in navigation)

2. **Fill in the revocation form:**
   - **Certificate ID**: Enter the certificate ID to revoke
   - **Revocation Reason**: (Optional) Enter a reason for revocation (e.g., "Certificate issued in error", "Student misconduct")

3. **Read the warning** - Revoking a certificate marks it as invalid and cannot be undone

4. **Click "Revoke Certificate"**

5. **After successful revocation**, you'll see:
   - ✅ Success message
   - Certificate ID that was revoked
   - Revocation reason (if provided)
   - **Note**: The certificate remains on the blockchain but will show as revoked during verification

**Important:**
- Only the issuing institution or admin can revoke certificates
- Institutions can only revoke certificates they issued
- Admins can revoke any certificate
- Revoked certificates cannot be un-revoked

---

## 5️⃣ **Verify a Certificate**

Anyone can verify certificates (no login required):

1. **Click on "Verify Certificate"** tab

2. **Enter the Certificate ID** (obtained when certificate was issued)

3. **Click "Verify Certificate"**

4. **You'll see:**
   - ✅ Certificate details if valid
   - ❌ Error message if certificate not found or invalid
   - Blockchain proof information
   - Digital signature verification status

---

## 6️⃣ **View Student Portfolio**

View all certificates for a specific student:

1. **Click on "Student Portfolio"** tab

2. **Enter the Student ID**

3. **Click "View Certificates"**

4. **You'll see all certificates** issued to that student

---

## 7️⃣ **View Blockchain Information**

View blockchain statistics and validate the chain:

1. **Click on "Blockchain Info"** tab

2. **You can:**
   - **Get Blockchain Info**: View statistics (total blocks, certificates, active/revoked counts, etc.)
   - **Validate Blockchain**: Check blockchain integrity (validates all blocks and their links)
   - **View All Certificates**: See all certificates in the system with their details

3. **Blockchain Statistics include:**
   - Total number of blocks
   - Total number of certificates
   - Active certificates count
   - Revoked certificates count
   - Latest block hash
   - Chain length

---

## 🔐 **User Roles Explained**

### **Student Role**
- ✅ Can verify certificates
- ✅ Can view student portfolios
- ✅ Can view blockchain information
- ❌ **Cannot issue certificates**

### **Institution Role**
- ✅ Can issue certificates
- ✅ Can revoke certificates they issued
- ✅ Can verify certificates
- ✅ Can view student portfolios
- ✅ Can view blockchain information

### **Admin Role**
- ✅ Can issue certificates
- ✅ Can revoke any certificate
- ✅ Can verify certificates
- ✅ Can view student portfolios
- ✅ Can view blockchain information

---

## ❓ **Common Issues & Solutions**

### **Problem: "Issue Certificate" tab is not visible**

**Solution:**
- You're logged in as a "Student". 
- **Logout** and **register a new account** with role "Institution" or "Admin"
- Or create a new account with institution/admin role

### **Problem: "Only institutions and admins can issue certificates"**

**Solution:**
- You're logged in as a "Student"
- Register a new account with "Institution" or "Admin" role

### **Problem: Registration fails with "Issuer ID already registered"**

**Solution:**
- The Issuer ID you chose is already taken
- Choose a different unique Issuer ID

### **Problem: Can't see certificates after issuing**

**Solution:**
- Check the "Blockchain Info" tab → "View All Certificates"
- Or use "Student Portfolio" with the student's ID
- Make sure the certificate was successfully issued (check for success message)

---

## 📝 **Quick Start Checklist**

- [ ] Backend server is running (`cd backend && python run.py`)
- [ ] Frontend server is running (`cd frontend && npm run dev`)
- [ ] Register an account with **"Institution"** or **"Admin"** role
- [ ] Login with your credentials
- [ ] "Issue Certificate" tab should be visible
- [ ] Issue your first certificate
- [ ] Verify the certificate using the Certificate ID

---

## 🎯 **Example Workflow**

1. **Register as Institution:**
   - Username: `university_admin`
   - Email: `admin@university.edu`
   - Password: `securepass123`
   - Role: `Institution`
   - Issuer ID: `UNI001`
   - Issuer Name: `University of Technology`
   - **After clicking "Register"**: You'll be automatically logged in and taken to the "Issue Certificate" page

2. **Issue Certificate:**
   - Student Name: `John Doe`
   - Student ID: `STU001`
   - Course Name: `Computer Science`
   - Grade: `A+`
   - Course Duration: `4 years`

3. **Save the Certificate ID** (e.g., `A1B2C3D4E5F6G7H8`)

4. **Verify Certificate:**
   - Go to "Verify Certificate" tab
   - Enter the Certificate ID
   - See verification results including:
     - Certificate details
     - Blockchain proof
     - Digital signature verification status

5. **View Blockchain Info:**
   - Go to "Blockchain Info" tab
   - Click "Get Blockchain Info" to see statistics
   - Click "Validate Blockchain" to verify integrity
   - Click "View All Certificates" to see all issued certificates

---

## 💡 **Tips**

- **Save Certificate IDs**: Always save the Certificate ID when issuing a certificate. It's needed for verification.
- **Student IDs**: Use consistent Student IDs for the same student across multiple certificates.
- **Issuer IDs**: Must be unique. Use a format like "UNI001", "SCH001", etc.
- **Blockchain**: All certificates are stored on a blockchain for immutability and verification.
- **Auto-Login**: After registration, you're automatically logged in - no need to login again!
- **First Certificate**: When you issue your first certificate, 2 blocks are created (Genesis block + your certificate). This is normal blockchain behavior.
- **Password Security**: Passwords are hashed using bcrypt and never stored in plain text.
- **Digital Signatures**: All certificates are digitally signed using ECDSA to prove authenticity.

---

## 🆘 **Need Help?**

If you encounter any issues:
1. Check that both backend and frontend servers are running
2. Check the browser console for errors (F12)
3. Check the backend terminal for error messages
4. Ensure you're using the correct role (Institution/Admin) to issue certificates

---

**Happy Certificate Issuing! 🎓**

