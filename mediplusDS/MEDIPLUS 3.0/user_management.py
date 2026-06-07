import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import *

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("MEDIPLUS — Create New Account")
        self.geometry("700x700")
        self.resizable(True, True)
        self.configure(bg=OFF_WHITE)
        self.grab_set()
        configure_styles()
        self._fields = {}
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=NAVY, pady=20)
        hdr.pack(fill="x")
        tk.Canvas(hdr, width=36, height=36, bg=NAVY, highlightthickness=0).pack(side="left", padx=16)
        tk.Label(hdr, text="MEDIPLUS", font=("Georgia", 18, "bold"), fg=CYAN, bg=NAVY).pack(side="left")
        tk.Label(hdr, text="— Create Account", font=("Helvetica", 14), fg=WHITE, bg=NAVY).pack(side="left", padx=8)

        # Scrollable body
        scroll_outer, _, scroll_inner = scrollable_frame(self, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True, padx=0, pady=0)
        self._scroll_inner = scroll_inner

        # Card wrapper
        card = tk.Frame(scroll_inner, bg=WHITE, padx=40, pady=30)
        card.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(card, text="Register New Account", font=FONT_TITLE, fg=NAVY, bg=WHITE).pack(pady=(0, 4))
        tk.Label(card, text="Fill in the details below to create your MEDIPLUS account",
                 font=("Helvetica", 10), fg=GRAY, bg=WHITE).pack(pady=(0, 20))

        # Account type
        self._add_label(card, "Account Type *")
        self.type_var = tk.StringVar(value="Patient")
        types = ["Patient", "Doctor", "Intern Doctor"]
        type_row = tk.Frame(card, bg=WHITE)
        type_row.pack(fill="x", pady=(0, 16))
        self._type_btns = {}
        for t in types:
            btn = tk.Button(type_row, text=t, font=FONT_BTN, relief="flat",
                            bd=0, cursor="hand2", padx=16, pady=7)
            btn.pack(side="left", padx=3)
            self._type_btns[t] = btn
            btn.config(command=lambda _t=t: self._switch_type(_t))

        # Dynamic form area
        self.form_area = tk.Frame(card, bg=WHITE)
        self.form_area.pack(fill="both", expand=True)

        # Credentials section
        sep = tk.Frame(card, bg=GRAY_LIGHT, height=1)
        sep.pack(fill="x", pady=20)
        tk.Label(card, text="Create Your Login Credentials",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 12))

        self._add_label(card, "Choose User ID *")
        self.uid_entry = make_entry(card, width=38)
        self.uid_entry.pack(fill="x", pady=(2, 12), ipady=4)

        self._add_label(card, "Choose Password *")
        self.pwd_entry = make_entry(card, width=38, show="●")
        self.pwd_entry.pack(fill="x", pady=(2, 12), ipady=4)

        self._add_label(card, "Confirm Password *")
        self.cpw_entry = make_entry(card, width=38, show="●")
        self.cpw_entry.pack(fill="x", pady=(2, 20), ipady=4)

        # Buttons
        btn_row = tk.Frame(card, bg=WHITE)
        btn_row.pack(fill="x", pady=(0, 10))
        make_button(btn_row, "  ✓ Create Account  ", self._submit,
                    color=CYAN, padx=24, pady=11).pack(side="left", padx=(0, 10))
        make_button(btn_row, "  Cancel  ", self.destroy,
                    color=GRAY, padx=24, pady=11).pack(side="left")
        
        # Trigger initial view
        self._switch_type("Patient")

    def _add_label(self, parent, text):
        tk.Label(parent, text=text, font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x", pady=(4, 0))

    def _switch_type(self, t):
        self.type_var.set(t)
        for _t, btn in self._type_btns.items():
            btn.config(bg=NAVY if _t == t else GRAY_LIGHT,
                       fg=WHITE if _t == t else DARK_TEXT)
        for w in self.form_area.winfo_children():
            w.destroy()
        self._fields = {} 
        self._build_form(t)

    def _build_form(self, t):
        f = self.form_area

        def lbl(text): self._add_label(f, text)
        def entry(key, show=None):
            e = make_entry(f, width=38)
            if show: e.config(show=show)
            e.pack(fill="x", pady=(2, 12), ipady=4)
            self._fields[key] = e
            return e

        def combo(key, values, default=None):
            v = tk.StringVar(value=default or values[0])
            cb = ttk.Combobox(f, textvariable=v, values=values, state="readonly",
                              font=FONT_BODY, width=36)
            cb.pack(fill="x", pady=(2, 12), ipady=4)
            self._fields[key] = v
            return cb, v

        lbl("Full Name *")
        entry("name")
        lbl("Gender *")
        combo("gender", ["Male", "Female"], "Male")
        lbl("Age *")
        entry("age")
        lbl("NID Number * (must be exactly 7 digits)")
        entry("nid")

        if t == "Patient":
            lbl("Date of Birth * (DD/MM/YYYY)")
            entry("birth_date")
            lbl("Weight (kg) *")
            entry("weight")
        elif t == "Doctor":
            lbl("Medical Degree *")
            entry("degree")
            lbl("Specialization *")
            combo("specialization", ["General Medicine", "Cardiology", "Neurology", "Surgery", "Other"])
            lbl("Consultation Fee (৳)")
            entry("fee")
        elif t == "Intern Doctor":
            lbl("Institution Name *")
            entry("institution")
            lbl("Joining Date * (DD/MM/YYYY)")
            entry("joined_date")
            lbl("Specialization Area")
            combo("specialization", ["General Medicine", "Cardiology", "Pediatrics", "Other"])

    def _get_val(self, key):
        f = self._fields.get(key)
        if f is None: return ""
        return f.get().strip() if isinstance(f, (tk.StringVar, tk.Entry)) else ""

    def _validate_date(self, date_str):
        parts = date_str.split("/")
        if len(parts) != 3: return False, "Use DD/MM/YYYY format"
        try:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            if 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= y <= 2026: return True, ""
        except: pass
        return False, "Invalid date values"

    def _submit(self):
        t = self.type_var.get()
        errors = []
        
        uid = self.uid_entry.get().strip()
        pw = self.pwd_entry.get().strip()
        cpw = self.cpw_entry.get().strip()
        
        name = self._get_val("name")
        age_str = self._get_val("age")
        nid = self._get_val("nid")

        if not name: errors.append("Name is required.")
        if not age_str.isdigit(): errors.append("Valid age is required.")
        if not (nid.isdigit() and len(nid) == 7): errors.append("NID must be 7 digits.")
        if not uid or not pw: errors.append("Credentials are required.")
        if pw != cpw: errors.append("Passwords do not match.")
        
        if uid and database.user_id_exists(uid): errors.append("User ID taken.")
        if nid and database.nid_exists(nid): errors.append("NID already registered.")

        if errors:
            messagebox.showerror("Validation Errors", "\n".join(f"• {e}" for e in errors))
            return

        data = {
            "user_type": t.lower().replace(" ", "_").replace("intern_doctor", "intern"),
            "name": name, "gender": self._get_val("gender"), "age": int(age_str),
            "nid": nid, "user_id": uid, "password": pw
        }

        # Handle type-specific data
        if t == "Patient":
            data.update({"birth_date": self._get_val("birth_date"), "weight": self._get_val("weight")})
        elif t == "Doctor":
            data.update({"degree": self._get_val("degree"), "specialization": self._get_val("specialization"), "fee": self._get_val("fee")})
        elif t == "Intern Doctor":
            data.update({"institution": self._get_val("institution"), "joined_date": self._get_val("joined_date"), "specialization": self._get_val("specialization")})

        ok, msg = database.register_user(data)
        if ok:
            messagebox.showinfo("Success", f"Account created for {name}!")
            self.destroy()
        else:
            messagebox.showerror("Error", msg)