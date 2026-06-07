import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "mediplus.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_db():
    conn = get_connection()
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT NOT NULL,
        name TEXT NOT NULL,
        gender TEXT,
        birth_date TEXT,
        weight REAL,
        age INTEGER,
        nid TEXT UNIQUE NOT NULL,
        degree TEXT,
        specialization TEXT,
        institution TEXT,
        joined_date TEXT,
        user_id TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        approved INTEGER DEFAULT 0,
        fee REAL DEFAULT 500,
        phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        doctor_id TEXT NOT NULL,
        problem TEXT,
        status TEXT DEFAULT 'waiting',
        waiting_number INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT NOT NULL,
        patient_id TEXT NOT NULL,
        appointment_id INTEGER,
        medicines TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        quantity INTEGER DEFAULT 0,
        price REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS medicine_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        medicine_name TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        unit_price REAL,
        total_cost REAL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        doctor_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        appointment_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS doctor_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT UNIQUE NOT NULL,
        total_earned REAL DEFAULT 0,
        available REAL DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS doctor_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT NOT NULL,
        day TEXT NOT NULL,
        available INTEGER DEFAULT 1,
        note TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS funding_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_amount REAL NOT NULL,
        raised_amount REAL DEFAULT 0,
        approved INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER NOT NULL,
        donor_name TEXT DEFAULT 'Anonymous',
        amount REAL NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # ─── INSERT PERMANENT ADMINS ──────────────────────────────────
    fixed_admins = [
        ("Raju", "242014131"),
        ("Tamid", "242014085"),
        ("Durjoy", "242014211")
    ]

    for name, uid in fixed_admins:
        c.execute("SELECT id FROM users WHERE user_id = ?", (uid,))
        if not c.fetchone():
            hashed_pw = hash_password(uid)
            c.execute('''INSERT INTO users 
                         (user_type, name, user_id, password, approved, nid) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      ('admin', name, uid, hashed_pw, 1, f"ADMIN_NID_{uid}"))

    conn.commit()
    conn.close()

# ─── USER FUNCTIONS ────────────────────────────────────────────────
def nid_exists(nid):
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE nid=?", (nid,)).fetchone()
    conn.close()
    return row is not None

def user_id_exists(user_id):
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row is not None

def register_user(data):
    conn = get_connection()
    try:
        conn.execute('''INSERT INTO users
            (user_type,name,gender,birth_date,weight,age,nid,degree,specialization,institution,joined_date,user_id,password,approved)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data['user_type'], data['name'], data.get('gender'), data.get('birth_date'),
             data.get('weight'), data.get('age'), data['nid'], data.get('degree'),
             data.get('specialization'), data.get('institution'), data.get('joined_date'),
             data['user_id'], hash_password(data['password']),
             1 if data['user_type'] == 'patient' else 0))
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(user_id, password, user_type):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE user_id=? AND password=? AND user_type=?",
        (user_id, hash_password(password), user_type)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def login_admin(username, password):
    ADMINS = {
        "Raju":   "242014131",
        "Tamid":  "242014085",
        "Durjoy": "242014211"
    }
    if username in ADMINS and ADMINS[username] == password:
        return {"user_id": username, "name": username, "user_type": "admin"}
    return None

def get_approved_doctors():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE user_type IN ('doctor','intern') AND approved=1"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_doctors_interns():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE user_type IN ('doctor','intern')"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_user(user_id):
    conn = get_connection()
    conn.execute("UPDATE users SET approved=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def reject_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_fee(user_id, fee):
    conn = get_connection()
    conn.execute("UPDATE users SET fee=? WHERE user_id=?", (fee, user_id))
    conn.commit()
    conn.close()

# ─── APPOINTMENT FUNCTIONS ──────────────────────────────────────────
def book_appointment(patient_id, doctor_id, problem):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM appointments WHERE doctor_id=? AND status='waiting'",
        (doctor_id,)
    ).fetchone()['c']
    waiting_num = count + 1
    conn.execute(
        "INSERT INTO appointments (patient_id,doctor_id,problem,status,waiting_number) VALUES (?,?,?,?,?)",
        (patient_id, doctor_id, problem, 'waiting', waiting_num)
    )
    doctor = conn.execute("SELECT fee FROM users WHERE user_id=?", (doctor_id,)).fetchone()
    fee = doctor['fee'] if doctor else 500
    conn.execute(
        "INSERT INTO payments (patient_id,doctor_id,amount,status) VALUES (?,?,?,?)",
        (patient_id, doctor_id, fee, 'pending')
    )
    conn.commit()
    conn.close()
    return waiting_num

def get_patient_appointments(patient_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT a.*, u.name as doctor_name FROM appointments a JOIN users u ON a.doctor_id=u.user_id WHERE a.patient_id=?",
        (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_doctor_patients(doctor_id):
    conn = get_connection()
    rows = conn.execute(
        '''SELECT a.*, u.name as patient_name, u.age, u.weight, u.gender
           FROM appointments a JOIN users u ON a.patient_id=u.user_id
           WHERE a.doctor_id=? AND a.status='waiting' ORDER BY a.waiting_number''',
        (doctor_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_appointment_status(appt_id, status):
    conn = get_connection()
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    conn.commit()
    conn.close()

def cancel_appointment(appt_id):
    conn = get_connection()
    conn.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
    conn.commit()
    conn.close()

# ─── PRESCRIPTION FUNCTIONS ─────────────────────────────────────────
def save_prescription(doctor_id, patient_id, appt_id, medicines, notes):
    conn = get_connection()
    try:
        # 1. Save the actual prescription
        conn.execute(
            "INSERT INTO prescriptions (doctor_id, patient_id, appointment_id, medicines, notes) VALUES (?, ?, ?, ?, ?)",
            (doctor_id, patient_id, appt_id, medicines, notes)
        )
        
        # 2. UPDATE the appointment status so they aren't 'waiting' anymore
        conn.execute("UPDATE appointments SET status='prescribed' WHERE id=?", (appt_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# ─── MEDICINE FUNCTIONS ─────────────────────────────────────────────
def get_all_medicines():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM medicines ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_medicine(name, quantity, price):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO medicines (name,quantity,price) VALUES (?,?,?)", (name, quantity, price))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.execute("UPDATE medicines SET quantity=quantity+?, price=? WHERE name=?", (quantity, price, name))
        conn.commit()
        return True
    finally:
        conn.close()

def update_medicine(med_id, name, quantity, price):
    conn = get_connection()
    conn.execute("UPDATE medicines SET name=?,quantity=?,price=? WHERE id=?", (name, quantity, price, med_id))
    conn.commit()
    conn.close()

def delete_medicine(med_id):
    conn = get_connection()
    conn.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()
    conn.close()

def order_medicine(patient_id, medicine_name, quantity):
    conn = get_connection()
    med = conn.execute("SELECT * FROM medicines WHERE name=? AND quantity>=?", (medicine_name, quantity)).fetchone()
    if not med:
        conn.close()
        return False, "Medicine not available or insufficient stock"
    total = med['price'] * quantity
    conn.execute(
        "INSERT INTO medicine_orders (patient_id,medicine_name,quantity,unit_price,total_cost,status) VALUES (?,?,?,?,?,?)",
        (patient_id, medicine_name, quantity, med['price'], total, 'ordered')
    )
    conn.execute("UPDATE medicines SET quantity=quantity-? WHERE name=?", (quantity, medicine_name))
    conn.commit()
    conn.close()
    return True, f"Order placed! Total: ৳{total:.2f}"

def get_all_medicine_orders():
    conn = get_connection()
    rows = conn.execute(
        '''SELECT mo.*, u.name as patient_name FROM medicine_orders mo
           JOIN users u ON mo.patient_id=u.user_id ORDER BY mo.created_at DESC'''
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── PAYMENT FUNCTIONS ──────────────────────────────────────────────
def get_all_payments():
    conn = get_connection()
    rows = conn.execute(
        '''SELECT p.*, u1.name as patient_name, u2.name as doctor_name
           FROM payments p
           JOIN users u1 ON p.patient_id=u1.user_id
           JOIN users u2 ON p.doctor_id=u2.user_id
           ORDER BY p.created_at DESC'''
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_payment(payment_id):
    conn = get_connection()
    pay = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()
    if pay:
        conn.execute("UPDATE payments SET status='approved' WHERE id=?", (payment_id,))
        existing = conn.execute("SELECT id FROM doctor_earnings WHERE doctor_id=?", (pay['doctor_id'],)).fetchone()
        if existing:
            conn.execute(
                "UPDATE doctor_earnings SET total_earned=total_earned+?, available=available+? WHERE doctor_id=?",
                (pay['amount'], pay['amount'], pay['doctor_id'])
            )
        else:
            conn.execute(
                "INSERT INTO doctor_earnings (doctor_id,total_earned,available) VALUES (?,?,?)",
                (pay['doctor_id'], pay['amount'], pay['amount'])
            )
        conn.commit()
    conn.close()

def get_doctor_earnings(doctor_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM doctor_earnings WHERE doctor_id=?", (doctor_id,)).fetchone()
    conn.close()
    return dict(row) if row else {'total_earned': 0, 'available': 0}

def withdraw_earnings(doctor_id, phone):
    conn = get_connection()
    row = conn.execute("SELECT * FROM doctor_earnings WHERE doctor_id=?", (doctor_id,)).fetchone()
    if row and row['available'] > 0:
        conn.execute("UPDATE doctor_earnings SET available=0 WHERE doctor_id=?", (doctor_id,))
        conn.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, doctor_id))
        conn.commit()
        conn.close()
        return True, row['available']
    conn.close()
    return False, 0

# ─── SCHEDULE FUNCTIONS ─────────────────────────────────────────────
def get_doctor_schedule(doctor_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM doctor_schedule WHERE doctor_id=?", (doctor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_day_off(doctor_id, day, note=""):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM doctor_schedule WHERE doctor_id=? AND day=?", (doctor_id, day)).fetchone()
    if existing:
        conn.execute("UPDATE doctor_schedule SET available=0,note=? WHERE doctor_id=? AND day=?", (note, doctor_id, day))
    else:
        conn.execute("INSERT INTO doctor_schedule (doctor_id,day,available,note) VALUES (?,?,0,?)", (doctor_id, day, note))
    conn.commit()
    conn.close()

def set_day_available(doctor_id, day):
    conn = get_connection()
    conn.execute("UPDATE doctor_schedule SET available=1,note='' WHERE doctor_id=? AND day=?", (doctor_id, day))
    conn.commit()
    conn.close()

# ─── FUNDING FUNCTIONS ──────────────────────────────────────────────
def create_campaign(patient_id, title, description, target):
    conn = get_connection()
    conn.execute("INSERT INTO funding_campaigns (patient_id,title,description,target_amount) VALUES (?,?,?,?)", (patient_id, title, description, target))
    conn.commit()
    conn.close()

def get_all_campaigns():
    conn = get_connection()
    rows = conn.execute('''SELECT fc.*, u.name as creator_name FROM funding_campaigns fc JOIN users u ON fc.patient_id=u.user_id ORDER BY fc.created_at DESC''').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_campaign(campaign_id):
    conn = get_connection()
    conn.execute("UPDATE funding_campaigns SET approved=1 WHERE id=?", (campaign_id,))
    conn.commit()
    conn.close()

def donate_to_campaign(campaign_id, donor_name, amount):
    conn = get_connection()
    conn.execute("INSERT INTO donations (campaign_id,donor_name,amount) VALUES (?,?,?)", (campaign_id, donor_name, amount))
    conn.execute("UPDATE funding_campaigns SET raised_amount=raised_amount+? WHERE id=?", (amount, campaign_id))
    conn.commit()
    conn.close()

# ─── ADMIN USER MANAGEMENT FUNCTIONS ───────────────────────────────
def get_all_users():
    """Fetches every user (except admins) for the Admin Channel list."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users WHERE user_type != 'admin' ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(user_id):
    """Allows Admin to remove Patient, Doctor, or Intern accounts."""
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# ─── UserDelete.py ────────────────────────────
def delete_user(user_id):
    """Permanently deletes a user from the database by their unique User ID."""
    conn = get_connection()
    try:
        # This will remove the user record completely
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        conn.close()
# users_filter.py
def get_users_by_type(user_type):
    """Fetches users filtered by type (patient, doctor, or intern)."""
    conn = get_connection()
    # Map UI display name to database value
    query_type = "intern" if user_type.lower() == "intern doctor" else user_type.lower()
    
    rows = conn.execute(
        "SELECT * FROM users WHERE user_type = ? AND user_type != 'admin' ORDER BY created_at DESC", 
        (query_type,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]