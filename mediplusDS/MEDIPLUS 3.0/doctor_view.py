import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import *


class DoctorPortal:
    def __init__(self, root, user, logout_cb):
        self.root = root
        self.user = user
        self.logout_cb = logout_cb
        self.is_intern = (user['user_type'] == 'intern')
        self._build()

    def _build(self):
        for w in self.root.winfo_children():
            w.destroy()
        root = self.root
        dtype = "Intern Doctor" if self.is_intern else "Doctor"
        root.title(f"MEDIPLUS — {dtype} Portal | Dr. {self.user['name']}")

        # ── Top Nav ────────────────────────────────────────────────
        nav = tk.Frame(root, bg=NAVY)
        nav.pack(fill="x")
        tk.Frame(nav, bg=CYAN, height=4).pack(fill="x")
        nav_inner = tk.Frame(nav, bg=NAVY, pady=12)
        nav_inner.pack(fill="x", padx=24)
        tk.Label(nav_inner, text="✚ MEDIPLUS", font=("Georgia", 16, "bold"),
                 fg=CYAN, bg=NAVY).pack(side="left")
        badge_color = PURPLE if self.is_intern else BLUE
        tk.Label(nav_inner, text=f"  {dtype} Portal",
                 font=("Helvetica", 11), fg=WHITE, bg=NAVY).pack(side="left", padx=12)
        tag_label(nav_inner, dtype.upper(), color=badge_color).pack(side="left")

        right_nav = tk.Frame(nav_inner, bg=NAVY)
        right_nav.pack(side="right")
        tk.Label(right_nav, text=f"Dr. {self.user['name']}",
                 font=FONT_SUB, fg=WHITE, bg=NAVY).pack(side="left", padx=12)
        make_button(right_nav, "Logout", self._logout, color=RED, padx=14, pady=6).pack(side="left")

        # ── Layout ─────────────────────────────────────────────────
        body = tk.Frame(root, bg=OFF_WHITE)
        body.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg=NAVY_LIGHT, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MENU", font=("Helvetica", 9, "bold"),
                 fg=GRAY, bg=NAVY_LIGHT).pack(pady=(24, 8), padx=16, anchor="w")

        self._sidebar_btns = {}
        menu_items = [
            ("🏠", "Dashboard", self._tab_dashboard),
            ("👥", "Patients", self._tab_patients),
            ("📋", "Schedule", self._tab_schedule),
            ("💰", "Earnings", self._tab_earnings),
        ]
        for icon, label, cmd in menu_items:
            btn = tk.Button(sidebar, text=f"  {icon}  {label}",
                            font=FONT_BODY, bg=NAVY_LIGHT, fg=WHITE,
                            relief="flat", bd=0, anchor="w",
                            cursor="hand2", padx=16, pady=12,
                            activebackground=badge_color, activeforeground=WHITE)
            btn.pack(fill="x")
            btn.config(command=lambda c=cmd, b=btn, lbl=label: self._sidebar_select(b, lbl, c))
            self._sidebar_btns[label] = btn

        self.content = tk.Frame(body, bg=OFF_WHITE)
        self.content.pack(side="right", fill="both", expand=True)

        self._sidebar_select(self._sidebar_btns["Dashboard"], "Dashboard", self._tab_dashboard)

    def _sidebar_select(self, active_btn, label, cmd):
        color = PURPLE if self.is_intern else BLUE
        for lbl, btn in self._sidebar_btns.items():
            btn.config(bg=color if lbl == label else NAVY_LIGHT)
        cmd()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ─── DASHBOARD ─────────────────────────────────────────────────
    def _tab_dashboard(self):
        self._clear_content()
        c = self.content
        user = self.user
        dtype = "Intern Doctor" if self.is_intern else "Doctor"

        color = PURPLE if self.is_intern else BLUE
        hdr = tk.Frame(c, bg=color, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Welcome, Dr. {user['name']}! 👋",
                 font=FONT_TITLE, fg=WHITE, bg=color).pack(padx=32, anchor="w")
        tk.Label(hdr, text=f"{dtype}  ·  {user.get('specialization', 'General Medicine')}",
                 font=FONT_BODY, fg=OFF_WHITE, bg=color).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Stats row
        patients = database.get_doctor_patients(user['user_id'])
        earnings = database.get_doctor_earnings(user['user_id'])
        stats = [
            ("Waiting Patients", len(patients), BLUE),
            ("Total Earned", f"৳{earnings['total_earned']:.2f}", GREEN),
            ("Available", f"৳{earnings['available']:.2f}", CYAN_DARK),
        ]
        stats_row = tk.Frame(body, bg=OFF_WHITE)
        stats_row.pack(fill="x", pady=(0, 20))
        for lbl, val, col in stats:
            sf = stat_card(stats_row, lbl, val, color=col)
            sf.pack(side="left", padx=(0, 12))

        # Profile info
        info_card_outer, info_card = make_card(body)
        info_card_outer.pack(fill="x", pady=8)
        tk.Label(info_card, text="Profile Information", font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 12))

        fields = [
            ("Name", f"Dr. {user['name']}"),
            ("Type", dtype),
            ("Specialization", user.get('specialization', 'N/A')),
            ("Degree", user.get('degree', 'N/A')),
            ("Gender", user.get('gender', 'N/A')),
            ("User ID", user['user_id']),
        ]
        if self.is_intern:
            fields.append(("Institution", user.get('institution', 'N/A')))
            fields.append(("Joined", user.get('joined_date', 'N/A')))

        grid = tk.Frame(info_card, bg=WHITE)
        grid.pack(fill="x")
        for i, (lbl, val) in enumerate(fields):
            row_f = tk.Frame(grid, bg=WHITE)
            row_f.pack(fill="x", pady=3)
            tk.Label(row_f, text=f"{lbl}:", font=FONT_SUB, fg=GRAY, bg=WHITE, width=18, anchor="w").pack(side="left")
            tk.Label(row_f, text=val, font=FONT_BODY, fg=DARK_TEXT, bg=WHITE, anchor="w").pack(side="left")

    # ─── PATIENTS ──────────────────────────────────────────────────
    def _tab_patients(self):
        self._clear_content()
        c = self.content

        color = PURPLE if self.is_intern else BLUE
        hdr = tk.Frame(c, bg=color, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👥 Waiting Patients",
                 font=FONT_TITLE, fg=WHITE, bg=color).pack(padx=32, anchor="w")
        tk.Label(hdr, text="Review patient details and issue prescriptions",
                 font=FONT_BODY, fg=OFF_WHITE, bg=color).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        patients = database.get_doctor_patients(self.user['user_id'])

        if not patients:
            empty = tk.Frame(body, bg=WHITE, padx=40, pady=40)
            empty.pack(pady=20)
            tk.Label(empty, text="✅", font=("Helvetica", 48), bg=WHITE).pack()
            tk.Label(empty, text="No waiting patients at the moment.",
                     font=FONT_HEADING, fg=GRAY, bg=WHITE).pack(pady=8)
            return

        scroll_outer, _, scroll_inner = scrollable_frame(body, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        for p in patients:
            card_outer, card = make_card(scroll_inner, padx=20, pady=16)
            card_outer.pack(fill="x", pady=6)

            # Queue badge
            badge = tk.Frame(card, bg=color, padx=14, pady=10)
            badge.pack(side="left")
            tk.Label(badge, text=f"#{p.get('waiting_number', '?')}",
                     font=("Georgia", 22, "bold"), fg=WHITE, bg=color).pack()
            tk.Label(badge, text="Queue", font=FONT_SMALL, fg=WHITE, bg=color).pack()

            # Patient info
            info = tk.Frame(card, bg=WHITE, padx=16)
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=p.get('patient_name', p['patient_id']),
                     font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")

            detail_row = tk.Frame(info, bg=WHITE)
            detail_row.pack(fill="x", pady=4)
            for lbl, val in [("Age", f"{p.get('age','?')} yrs"), ("Weight", f"{p.get('weight','?')} kg"), ("Gender", p.get('gender','?'))]:
                tag_label(detail_row, f"{lbl}: {val}", color=NAVY_LIGHT).pack(side="left", padx=(0, 6))

            prob = (p.get('problem') or 'No description')[:100]
            tk.Label(info, text=f"🗒 Problem: {prob}",
                     font=FONT_BODY, fg=DARK_TEXT, bg=WHITE, anchor="w", wraplength=500).pack(fill="x")

            make_button(card, "  📋 Prescribe  ", lambda pt=p: self._open_prescribe(pt),
                        color=CYAN_DARK, pady=8, padx=14).pack(side="right")

    def _open_prescribe(self, patient):
        win = tk.Toplevel(self.root)
        win.title(f"Prescribe — {patient.get('patient_name', patient['patient_id'])}")
        win.geometry("600x600") # Increased height to ensure button is visible
        win.configure(bg=WHITE)
        win.grab_set()

        hdr = tk.Frame(win, bg=NAVY, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📋 Prescription for {patient.get('patient_name','Patient')}",
                 font=FONT_HEADING, fg=WHITE, bg=NAVY).pack(padx=20, anchor="w")

        body = tk.Frame(win, bg=WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Patient Info
        info = tk.Frame(body, bg=OFF_WHITE, padx=16, pady=12)
        info.pack(fill="x", pady=(0, 16))
        for lbl, val in [
            ("Patient", patient.get('patient_name', patient['patient_id'])),
            ("Problem", patient.get('problem', 'N/A')),
        ]:
            row = tk.Frame(info, bg=OFF_WHITE)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{lbl}:", font=FONT_SUB, fg=GRAY, bg=OFF_WHITE, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_BODY, fg=DARK_TEXT, bg=OFF_WHITE).pack(side="left")

        # Inputs
        tk.Label(body, text="Medicines *", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(anchor="w")
        med_text = tk.Text(body, height=5, font=FONT_BODY, relief="solid", bd=1)
        med_text.pack(fill="x", pady=(4, 12))

        tk.Label(body, text="Notes", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(anchor="w")
        notes_text = tk.Text(body, height=3, font=FONT_BODY, relief="solid", bd=1)
        notes_text.pack(fill="x", pady=(4, 16))

        def submit():
            meds = med_text.get("1.0", "end").strip()
            notes = notes_text.get("1.0", "end").strip()
            
            if not meds:
                messagebox.showwarning("Missing", "Please enter medicines.", parent=win)
                return

            # Call the database with all required IDs
            success = database.save_prescription(
                self.user['user_id'], 
                patient['patient_id'], 
                patient['id'], # This is the Appointment ID
                meds, 
                notes
            )
            
            if success:
                messagebox.showinfo("Success", "Prescription submitted.", parent=win)
                win.destroy()
                self._tab_patients() # This refreshes your list!
            else:
                messagebox.showerror("Error", "Failed to save.", parent=win)

        # --- THE BUTTON SECTION ---
        btn_row = tk.Frame(body, bg=WHITE)
        btn_row.pack(fill="x", side="bottom", pady=20) # Forced to bottom with padding
        
        make_button(btn_row, "  Submit Prescription  ", submit, color=GREEN).pack(side="left", padx=5)
        make_button(btn_row, "  Cancel  ", win.destroy, color=GRAY).pack(side="left", padx=5)

    # ─── SCHEDULE ──────────────────────────────────────────────────
    def _tab_schedule(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=NAVY_LIGHT, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📅 Weekly Schedule",
                 font=FONT_TITLE, fg=WHITE, bg=NAVY_LIGHT).pack(padx=32, anchor="w")
        tk.Label(hdr, text="Manage your availability and set time-off days",
                 font=FONT_BODY, fg=GRAY, bg=NAVY_LIGHT).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        schedule = {s['day']: s for s in database.get_doctor_schedule(self.user['user_id'])}

        for day in days:
            card_outer, card = make_card(body, padx=16, pady=12)
            card_outer.pack(fill="x", pady=4)

            day_info = schedule.get(day, {'available': 1, 'note': ''})
            is_available = day_info.get('available', 1)

            # Day name
            day_color = GREEN if is_available else RED
            tk.Label(card, text=day, font=FONT_SUB, fg=NAVY, bg=WHITE, width=12, anchor="w").pack(side="left")
            status_txt = "✅ Available" if is_available else "🔴 Day Off"
            tk.Label(card, text=status_txt, font=FONT_BODY, fg=day_color, bg=WHITE).pack(side="left", padx=20)

            note = day_info.get('note', '') or ''
            if note:
                tk.Label(card, text=f"Note: {note}", font=FONT_SMALL, fg=GRAY, bg=WHITE).pack(side="left")

            btn_frame = tk.Frame(card, bg=WHITE)
            btn_frame.pack(side="right")

            if is_available:
                def set_off(d=day):
                    self._set_time_off_dialog(d)
                make_button(btn_frame, "Set Day Off", set_off, color=RED, pady=6, padx=10).pack(side="left")
            else:
                def set_avail(d=day):
                    database.set_day_available(self.user['user_id'], d)
                    self._tab_schedule()
                make_button(btn_frame, "Mark Available", set_avail, color=GREEN, pady=6, padx=10).pack(side="left")

    def _set_time_off_dialog(self, day):
        win = tk.Toplevel(self.root)
        win.title(f"Set Day Off — {day}")
        win.geometry("380x220")
        win.configure(bg=WHITE)
        win.grab_set()

        tk.Label(win, text=f"Set {day} as Day Off",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(pady=20)
        tk.Label(win, text="Reason / Note (optional):", font=FONT_BODY, fg=NAVY, bg=WHITE).pack(anchor="w", padx=30)
        note_e = make_entry(win, width=32)
        note_e.pack(padx=30, pady=8, ipady=4, fill="x")

        def confirm():
            database.set_day_off(self.user['user_id'], day, note_e.get().strip())
            win.destroy()
            self._tab_schedule()

        btn_row = tk.Frame(win, bg=WHITE)
        btn_row.pack(pady=16)
        make_button(btn_row, "Confirm", confirm, color=RED, pady=8, padx=14).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", win.destroy, color=GRAY, pady=8, padx=14).pack(side="left")

    # ─── EARNINGS ──────────────────────────────────────────────────
    def _tab_earnings(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=GREEN, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💰 My Earnings",
                 font=FONT_TITLE, fg=WHITE, bg=GREEN).pack(padx=32, anchor="w")
        tk.Label(hdr, text="View and withdraw your consultation earnings",
                 font=FONT_BODY, fg=OFF_WHITE, bg=GREEN).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        earnings = database.get_doctor_earnings(self.user['user_id'])

        stats_row = tk.Frame(body, bg=OFF_WHITE)
        stats_row.pack(fill="x", pady=(0, 24))
        for lbl, val, col in [
            ("Total Earned", f"৳{earnings['total_earned']:.2f}", GREEN),
            ("Available to Withdraw", f"৳{earnings['available']:.2f}", CYAN_DARK),
        ]:
            sf = stat_card(stats_row, lbl, val, color=col)
            sf.pack(side="left", padx=(0, 16))

        # Withdraw section
        card_outer, card = make_card(body, padx=24, pady=20)
        card_outer.pack(fill="x")
        tk.Label(card, text="Withdraw Earnings", font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 12))

        if earnings['available'] <= 0:
            tk.Label(card, text="No funds available for withdrawal at this time.",
                     font=FONT_BODY, fg=GRAY, bg=WHITE).pack()
        else:
            tk.Label(card, text=f"Available: ৳{earnings['available']:.2f}",
                     font=FONT_SUB, fg=GREEN, bg=WHITE).pack(anchor="w")
            tk.Label(card, text="Enter your phone number (bKash/Nagad):",
                     font=FONT_BODY, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(12, 4))
            phone_e = make_entry(card, width=24)
            phone_e.pack(anchor="w", ipady=4)
            if self.user.get('phone'):
                phone_e.insert(0, self.user['phone'])

            def withdraw():
                phone = phone_e.get().strip()
                if not phone or len(phone) < 10:
                    messagebox.showwarning("Invalid", "Enter a valid phone number.")
                    return
                ok, amount = database.withdraw_earnings(self.user['user_id'], phone)
                if ok:
                    messagebox.showinfo("Withdrawn! ✓",
                        f"৳{amount:.2f} sent to {phone}\nThank you!")
                    self._tab_earnings()
                else:
                    messagebox.showerror("Error", "Withdrawal failed.")

            make_button(card, "  Withdraw Now  →", withdraw, color=CYAN_DARK,
                        pady=10, padx=20).pack(anchor="w", pady=12)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logout_cb()