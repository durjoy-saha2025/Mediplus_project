import tkinter as tk
from tkinter import ttk, messagebox
import database  # Matches database.py
from styles import * # Matches styles.py

class MediPlusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MEDIPLUS — Healthcare Management System")
        self.root.geometry("1280x760")
        self.root.minsize(1100, 650)
        self.root.configure(bg=NAVY)
        database.initialize_db()
        configure_styles()
        self.current_user = None
        self._show_homepage()

    # ─── HOMEPAGE ──────────────────────────────────────────────────
    def _show_homepage(self):
        for w in self.root.winfo_children():
            w.destroy()
        self._build_homepage()

    def _build_homepage(self):
        root = self.root

        # ── LEFT PANEL (Hero) ──────────────────────────────────────
        left = tk.Frame(root, bg=NAVY, width=640)
        left.pack(side="left", fill="both", expand=True)
        left.pack_propagate(False)

        # Decorative top accent line
        tk.Frame(left, bg=CYAN, height=4).pack(fill="x")

        spacer = tk.Frame(left, bg=NAVY, height=60)
        spacer.pack()

        # Logo badge
        badge_frame = tk.Frame(left, bg=NAVY)
        badge_frame.pack(pady=(10, 0))

        cross_canvas = tk.Canvas(badge_frame, width=70, height=70, bg=NAVY, highlightthickness=0)
        cross_canvas.pack()
        cross_canvas.create_oval(5, 5, 65, 65, fill=CYAN, outline="")
        cross_canvas.create_rectangle(28, 15, 42, 55, fill=WHITE, outline="")
        cross_canvas.create_rectangle(15, 28, 55, 42, fill=WHITE, outline="")

        tk.Label(left, text="MEDIPLUS", font=("Georgia", 52, "bold"),
                 fg=WHITE, bg=NAVY).pack(pady=(12, 0))
        tk.Label(left, text="Advanced Healthcare Management System",
                 font=("Helvetica", 13), fg=CYAN, bg=NAVY).pack(pady=(4, 30))

        # Feature bullets
        features = [
            ("🏥", "Multi-role Portal", "Patients, Doctors & Admins"),
            ("📋", "Smart Appointments", "Book & manage easily"),
            ("💊", "Medicine Shop", "Order anytime, anywhere"),
            ("💰", "Secure Payments", "Transparent & verified"),
        ]
        feat_frame = tk.Frame(left, bg=NAVY_LIGHT, padx=40, pady=24)
        feat_frame.pack(fill="x", padx=50)

        for icon, title, sub in features:
            row = tk.Frame(feat_frame, bg=NAVY_LIGHT)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=icon, font=("Helvetica", 20), bg=NAVY_LIGHT, fg=WHITE, width=3).pack(side="left")
            col = tk.Frame(row, bg=NAVY_LIGHT)
            col.pack(side="left", padx=8)
            tk.Label(col, text=title, font=("Helvetica", 11, "bold"), fg=WHITE, bg=NAVY_LIGHT, anchor="w").pack(fill="x")
            tk.Label(col, text=sub, font=("Helvetica", 9), fg=GRAY, bg=NAVY_LIGHT, anchor="w").pack(fill="x")

        # Stats strip
        stats_frame = tk.Frame(left, bg=NAVY, pady=28)
        stats_frame.pack(fill="x", padx=50)
        for val, lbl in [("500+", "Doctors"), ("10K+", "Patients"), ("50+", "Specialties")]:
            sf = tk.Frame(stats_frame, bg=NAVY)
            sf.pack(side="left", expand=True)
            tk.Label(sf, text=val, font=("Georgia", 22, "bold"), fg=GOLD, bg=NAVY).pack()
            tk.Label(sf, text=lbl, font=("Helvetica", 9), fg=GRAY, bg=NAVY).pack()

        tk.Frame(left, bg=CYAN, height=2).pack(fill="x", side="bottom")

        # ── RIGHT PANEL (Auth) ─────────────────────────────────────
        right = tk.Frame(root, bg=OFF_WHITE, width=640)
        right.pack(side="right", fill="both", expand=True)
        right.pack_propagate(False)

        # Top nav strip
        nav = tk.Frame(right, bg=NAVY_LIGHT, pady=12)
        nav.pack(fill="x")
        tk.Label(nav, text="MEDIPLUS", font=("Georgia", 14, "bold"),
                 fg=CYAN, bg=NAVY_LIGHT).pack(side="left", padx=24)
        tk.Label(nav, text="Healthcare for everyone", font=("Helvetica", 9),
                 fg=GRAY, bg=NAVY_LIGHT).pack(side="left")

        # Auth card
        auth_outer = tk.Frame(right, bg=OFF_WHITE)
        auth_outer.pack(expand=True)

        card = tk.Frame(auth_outer, bg=WHITE, padx=50, pady=46,
                        relief="flat", bd=0,
                        highlightbackground=GRAY_LIGHT, highlightthickness=1)
        card.pack()

        tk.Label(card, text="Welcome Back", font=("Georgia", 26, "bold"),
                 fg=NAVY, bg=WHITE).pack(pady=(0, 4))
        tk.Label(card, text="Sign in to your account or create one",
                 font=("Helvetica", 11), fg=GRAY, bg=WHITE).pack(pady=(0, 30))

        # Role selector
        tk.Label(card, text="Select Role", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        self.role_var = tk.StringVar(value="Patient")
        roles = ["Patient", "Doctor", "Intern Doctor", "Admin"]
        role_frame = tk.Frame(card, bg=WHITE)
        role_frame.pack(fill="x", pady=(4, 16))
        self.role_btns = {}
        for role in roles:
            btn = tk.Button(role_frame, text=role,
                            font=("Helvetica", 10, "bold"),
                            relief="flat", bd=0, cursor="hand2", padx=12, pady=6)
            btn.pack(side="left", padx=3)
            self.role_btns[role] = btn
            btn.config(command=lambda r=role: self._select_role(r))
        self._select_role("Patient")

        # User ID
        tk.Label(card, text="User ID", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        self.login_id = make_entry(card, width=32)
        self.login_id.pack(fill="x", pady=(4, 12), ipady=4)

        # Password
        tk.Label(card, text="Password", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        self.login_pw = make_entry(card, width=32, show="●")
        self.login_pw.pack(fill="x", pady=(4, 20), ipady=4)
        self.login_pw.bind("<Return>", lambda e: self._do_login())

        # Login button
        make_button(card, "  Sign In  →", self._do_login, color=BLUE,
                    padx=30, pady=11).pack(fill="x", pady=(0, 12))

        # Divider
        div = tk.Frame(card, bg=WHITE)
        div.pack(fill="x", pady=4)
        tk.Frame(div, bg=GRAY_LIGHT, height=1).pack(fill="x", pady=8)
        tk.Label(div, text="Don't have an account?",
                 font=("Helvetica", 10), fg=GRAY, bg=WHITE).pack()

        make_button(card, "  Create New Account  ", self._open_register,
                    color=CYAN, padx=30, pady=11).pack(fill="x", pady=(10, 0))

        # Footer
        footer = tk.Frame(right, bg=GRAY_LIGHT, pady=10)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="© 2025 MEDIPLUS Healthcare. All rights reserved.",
                 font=FONT_SMALL, fg=GRAY, bg=GRAY_LIGHT).pack()

    def _select_role(self, role):
        self.role_var.set(role)
        for r, btn in self.role_btns.items():
            if r == role:
                btn.config(bg=NAVY, fg=WHITE)
            else:
                btn.config(bg=GRAY_LIGHT, fg=DARK_TEXT)

    def _do_login(self):
        uid = self.login_id.get().strip()
        pw  = self.login_pw.get().strip()
        role = self.role_var.get()

        if not uid or not pw:
            messagebox.showwarning("Missing Info", "Please enter User ID and Password.")
            return

        if role == "Admin":
            user = database.login_admin(uid, pw)
        else:
            type_map = {"Patient": "patient", "Doctor": "doctor", "Intern Doctor": "intern"}
            user = database.login_user(uid, pw, type_map[role])

        if not user:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")
            return

        if role != "Admin" and user.get("approved") == 0:
            messagebox.showwarning("Pending Approval",
                "Your account is pending admin approval.\nPlease wait for verification.")
            return

        self.current_user = user
        self._launch_portal(role, user)

    def _launch_portal(self, role, user):
        if role == "Patient":
            import patient_view
            patient_view.PatientPortal(self.root, user, self._show_homepage)
        elif role in ("Doctor", "Intern Doctor"):
            import doctor_view
            doctor_view.DoctorPortal(self.root, user, self._show_homepage)
        elif role == "Admin":
            import admin_view
            admin_view.AdminPortal(self.root, user, self._show_homepage)

    def _open_register(self):
        import user_management
        user_management.RegisterWindow(self.root)


def main():
    root = tk.Tk()
    app = MediPlusApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()