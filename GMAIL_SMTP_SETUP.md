# 📧 Gmail SMTP Setup Guide for OTP Verification

## 🎯 What You Need to Do

To send **real OTP emails** to Gmail addresses during sign-up, follow these 3 steps:

---

## Step 1: Enable Gmail App Password

Google requires an "App Password" for applications to send emails via Gmail SMTP.

### **Instructions:**

1. **Go to your Google Account**: https://myaccount.google.com/
2. **Enable 2-Step Verification** (if not already enabled):

   - Go to: https://myaccount.google.com/signinoptions/two-step-verification
   - Click "Get Started" and follow the prompts
   - **You MUST have 2FA enabled to create app passwords**

3. **Create an App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Windows Computer" as the device (or "Other")
   - Click "Generate"
   - **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)
   - **Remove the spaces**: `abcdefghijklmnop`

---

## Step 2: Update Your `.env` File

Open the `.env` file and replace these values:

```env
# Email (Gmail SMTP for real email delivery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com          # ← Replace with YOUR Gmail address
SMTP_PASSWORD=abcdefghijklmnop          # ← Replace with YOUR App Password (no spaces)
SMTP_FROM=your-email@gmail.com          # ← Replace with YOUR Gmail address
SMTP_USE_TLS=true
```

### **Example:**

If your Gmail is `srinath8789@gmail.com` and your app password is `wxyz abcd 1234 5678`:

```env
SMTP_USER=srinath8789@gmail.com
SMTP_PASSWORD=wxyzabcd12345678
SMTP_FROM=srinath8789@gmail.com
```

---

## Step 3: Restart Your Application

After updating `.env`, restart the application:

1. **Stop the current app** (press `Ctrl+C` in the terminal where it's running)
2. **Start it again**:
   ```bash
   bash start-all.sh
   ```

---

## ✅ Test the Flow

### **Sign Up with OTP:**

1. Go to: http://localhost:3000/auth/signup
2. Fill in:
   - **Email**: Any Gmail address (e.g., `test@gmail.com`)
   - **Password**: Your secure password
   - **Full Name**: Your name
   - **Organization Name**: Your company
3. Click **"Sign Up"**
4. **Check your email inbox** for the OTP code
5. Enter the **6-digit OTP** in the verification screen
6. ✅ **Account created and stored in database!**

### **Sign In:**

1. Go to: http://localhost:3000/auth/signin
2. Enter your **email and password**
3. Click **"Sign In"**
4. ✅ **You're logged in!**

---

## 🔧 How It Works (Technical Details)

### **Registration Flow:**

```
1. User submits email/password/name/org → POST /v1/auth/register/start
   ↓
2. Backend creates User (is_active=false) in database
   ↓
3. Backend generates 6-digit OTP and stores hash in EmailVerification table
   ↓
4. Backend sends OTP email via Gmail SMTP
   ↓
5. User receives email with OTP code
   ↓
6. User submits OTP → POST /v1/auth/register/verify
   ↓
7. Backend verifies OTP against hash
   ↓
8. Backend sets user.is_active=true
   ↓
9. ✅ Account verified and ready to use!
```

### **Login Flow:**

```
1. User submits email/password → POST /v1/auth/login
   ↓
2. Backend checks if user exists and is_active=true
   ↓
3. Backend verifies password hash
   ↓
4. Backend generates JWT token
   ↓
5. ✅ User logged in with token!
```

---

## 🐛 Troubleshooting

### **"Failed to send email: authentication failed"**

- ❌ Wrong Gmail password → Use the **App Password**, not your regular Gmail password
- ❌ Spaces in password → Remove all spaces from the 16-character app password
- ❌ 2FA not enabled → Enable 2-Step Verification first

### **"Failed to send email: connection refused"**

- ❌ Wrong SMTP settings → Make sure:
  ```env
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  ```

### **"User account is inactive or unverified"**

- ❌ You didn't verify the OTP yet
- ✅ Check your email for the OTP and complete verification
- ✅ Or request a new OTP by signing up again

### **Email not received?**

1. Check your **Spam folder**
2. Make sure you're using a valid Gmail address
3. Check the terminal logs for any email sending errors
4. Verify your App Password is correct

### **OTP expired?**

- OTPs expire after **10 minutes**
- Just sign up again to get a fresh OTP

---

## 🔐 Security Notes

✅ **App Passwords are safe** - They only work for the app you created them for
✅ **Never commit `.env` to Git** - Your app password should stay private
✅ **OTP codes are hashed** - They're stored securely in the database (bcrypt)
✅ **Passwords are hashed** - User passwords are never stored in plain text

---

## 📌 Alternative: Use Other Email Services

If you don't want to use Gmail, you can use:

### **SendGrid** (Free tier: 100 emails/day):

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
SMTP_FROM=your-verified-sender@yourdomain.com
SMTP_USE_TLS=true
```

### **Mailgun** (Free tier: 5,000 emails/month):

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=YOUR_MAILGUN_SMTP_PASSWORD
SMTP_FROM=noreply@your-domain.mailgun.org
SMTP_USE_TLS=true
```

### **Outlook/Hotmail**:

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_FROM=your-email@outlook.com
SMTP_USE_TLS=true
```

---

## ✨ Quick Setup Checklist

- [ ] Enable 2-Step Verification on Google Account
- [ ] Generate App Password from Google
- [ ] Update `.env` with Gmail and App Password
- [ ] Restart the application
- [ ] Test sign-up (check email for OTP)
- [ ] Verify OTP
- [ ] Test sign-in
- [ ] ✅ Done!

---

**Need Help?** If you get stuck, share the error message from the terminal and I can help troubleshoot!
