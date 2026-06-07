import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import *


class PatientPortal:
    def __init__(self, root, user, logout_cb):
        self.root = root
        self.user = user
        self.logout_cb = logout_cb
        self._build()

    def _build(self):
        for w in self.root.winfo_children():
            w.destroy()
        root = self.root
        root.title(f"MEDIPLUS — Patient Portal | {self.user['name']}")

        # ── Top Nav ────────────────────────────────────────────────
        nav = tk.Frame(root, bg=NAVY, pady=0)
        nav.pack(fill="x")
        tk.Frame(nav, bg=CYAN, height=4).pack(fill="x")
        nav_inner = tk.Frame(nav, bg=NAVY, pady=12)
        nav_inner.pack(fill="x", padx=24)
        tk.Label(nav_inner, text="✚ MEDIPLUS", font=("Georgia", 16, "bold"),
                 fg=CYAN, bg=NAVY).pack(side="left")
        tk.Label(nav_inner, text=f"  Patient Portal",
                 font=("Helvetica", 11), fg=GRAY, bg=NAVY).pack(side="left", padx=12)

        right_nav = tk.Frame(nav_inner, bg=NAVY)
        right_nav.pack(side="right")
        tk.Label(right_nav, text=f"👤 {self.user['name']}",
                 font=FONT_SUB, fg=WHITE, bg=NAVY).pack(side="left", padx=12)
        make_button(right_nav, "Logout", self._logout, color=RED, padx=14, pady=6).pack(side="left")

        # ── Main with sidebar ──────────────────────────────────────
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
            ("👨‍⚕️", "Find Doctors", self._tab_doctors),
            ("📅", "My Appointments", self._tab_appointments),
            ("💊", "Medicine Shop", self._tab_medicine),
            ("❤️", "Funding", self._tab_funding),
        ]
        for icon, label, cmd in menu_items:
            btn = tk.Button(sidebar, text=f"  {icon}  {label}",
                            font=FONT_BODY, bg=NAVY_LIGHT, fg=WHITE,
                            relief="flat", bd=0, anchor="w",
                            cursor="hand2", padx=16, pady=12,
                            activebackground=BLUE, activeforeground=WHITE)
            btn.pack(fill="x")
            btn.config(command=lambda c=cmd, b=btn, lbl=label: self._sidebar_select(b, lbl, c))
            self._sidebar_btns[label] = btn

        # Content area
        self.content = tk.Frame(body, bg=OFF_WHITE)
        self.content.pack(side="right", fill="both", expand=True)

        self._sidebar_select(self._sidebar_btns["Dashboard"], "Dashboard", self._tab_dashboard)

    def _sidebar_select(self, active_btn, label, cmd):
        for lbl, btn in self._sidebar_btns.items():
            btn.config(bg=BLUE if lbl == label else NAVY_LIGHT)
        cmd()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ─── DASHBOARD ─────────────────────────────────────────────────
    def _tab_dashboard(self):
        self._clear_content()
        c = self.content
        user = self.user

        # Header
        hdr = tk.Frame(c, bg=BLUE, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Welcome, {user['name']}! 👋",
                 font=FONT_TITLE, fg=WHITE, bg=BLUE).pack(padx=32, anchor="w")
        tk.Label(hdr, text="Here's your health overview",
                 font=FONT_BODY, fg=OFF_WHITE, bg=BLUE).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Info cards
        info_row = tk.Frame(body, bg=OFF_WHITE)
        info_row.pack(fill="x", pady=(0, 20))

        info = [
            ("Name", user.get('name', '-'), BLUE),
            ("Age", f"{user.get('age', '-')} yrs", CYAN_DARK),
            ("Weight", f"{user.get('weight', '-')} kg", PURPLE),
            ("Gender", user.get('gender', '-'), GOLD),
        ]
        for lbl, val, color in info:
            card = tk.Frame(info_row, bg=color, padx=20, pady=16)
            card.pack(side="left", padx=(0, 12), fill="y")
            tk.Label(card, text=val, font=("Georgia", 20, "bold"), fg=WHITE, bg=color).pack()
            tk.Label(card, text=lbl, font=("Helvetica", 9), fg=WHITE, bg=color).pack()

        # Waiting list
        tk.Label(body, text="Your Current Waiting List", font=FONT_HEADING,
                 fg=NAVY, bg=OFF_WHITE).pack(anchor="w", pady=(10, 8))

        cols = ("Doctor", "Problem", "Status", "Queue #")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=6)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=170, anchor="center")
        tree.pack(fill="x")

        appts = database.get_patient_appointments(user['user_id'])
        for a in appts:
            tree.insert("", "end", values=(
                a.get('doctor_name', a['doctor_id']),
                (a.get('problem') or '')[:30],
                a.get('status', '').upper(),
                a.get('waiting_number', '-')
            ))

    # ─── FIND DOCTORS ──────────────────────────────────────────────
    def _tab_doctors(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=CYAN_DARK, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👨‍⚕️ Find & Book a Doctor",
                 font=FONT_TITLE, fg=WHITE, bg=CYAN_DARK).pack(padx=32, anchor="w")
        tk.Label(hdr, text="All listed doctors are verified and approved",
                 font=FONT_BODY, fg=OFF_WHITE, bg=CYAN_DARK).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # Search
        search_row = tk.Frame(body, bg=OFF_WHITE)
        search_row.pack(fill="x", pady=(0, 14))
        tk.Label(search_row, text="Search:", font=FONT_SUB, fg=NAVY, bg=OFF_WHITE).pack(side="left")
        self.search_var = tk.StringVar()
        se = make_entry(search_row, width=28)
        se.pack(side="left", padx=8, ipady=4)
        se.bind("<KeyRelease>", lambda e: self._refresh_doctors())

        # Doctors list
        scroll_outer, _, scroll_inner = scrollable_frame(body, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)
        self._doctors_frame = scroll_inner

        self._refresh_doctors()

    def _refresh_doctors(self):
        for w in self._doctors_frame.winfo_children():
            w.destroy()
        doctors = database.get_approved_doctors()
        search = getattr(self, 'search_var', tk.StringVar()).get().lower()
        if search:
            doctors = [d for d in doctors if
                       search in d['name'].lower() or
                       search in (d.get('specialization') or '').lower()]

        if not doctors:
            tk.Label(self._doctors_frame, text="No approved doctors found.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for doc in doctors:
            card_outer, card = make_card(self._doctors_frame, bg=WHITE, padx=20, pady=16)
            card_outer.pack(fill="x", pady=6)

            left = tk.Frame(card, bg=WHITE)
            left.pack(side="left", fill="y")

            avatar = tk.Label(left, text="👨‍⚕️" if doc.get('gender') != 'Female' else "👩‍⚕️",
                              font=("Helvetica", 32), bg=WHITE)
            avatar.pack()

            info = tk.Frame(card, bg=WHITE)
            info.pack(side="left", fill="both", expand=True, padx=16)

            tk.Label(info, text=f"Dr. {doc['name']}", font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            dtype = "Intern Doctor" if doc['user_type'] == 'intern' else "Doctor"
            spec = doc.get('specialization') or 'General Medicine'
            tk.Label(info, text=f"{dtype}  ·  {spec}",
                     font=FONT_BODY, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x", pady=2)

            fee_frame = tk.Frame(info, bg=WHITE)
            fee_frame.pack(fill="x", pady=4)
            tag_label(fee_frame, f"৳ {doc.get('fee', 500)} Consultation Fee", color=GREEN).pack(side="left")
            if doc.get('degree'):
                tag_label(fee_frame, doc['degree'], color=BLUE).pack(side="left", padx=6)

            make_button(card, "  Book Appointment  →", lambda d=doc: self._open_book(d),
                        color=CYAN_DARK, pady=8, padx=14).pack(side="right", padx=(10, 0))

    def _open_book(self, doctor):
        win = tk.Toplevel(self.root)
        win.title(f"Book Dr. {doctor['name']}")
        win.geometry("520x420")
        win.configure(bg=WHITE)
        win.grab_set()

        tk.Frame(win, bg=NAVY, pady=14).pack(fill="x")
        tk.Label(win.winfo_children()[-1], text=f"📅 Book Appointment with Dr. {doctor['name']}",
                 font=FONT_HEADING, fg=WHITE, bg=NAVY).pack(padx=20)

        body = tk.Frame(win, bg=WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        info = tk.Frame(body, bg=OFF_WHITE, padx=16, pady=12)
        info.pack(fill="x", pady=(0, 16))
        tk.Label(info, text=f"Doctor: Dr. {doctor['name']}  |  {doctor.get('specialization','General')}",
                 font=FONT_SUB, fg=NAVY, bg=OFF_WHITE).pack(anchor="w")
        tk.Label(info, text=f"Fee: ৳{doctor.get('fee', 500)}",
                 font=FONT_BODY, fg=GREEN, bg=OFF_WHITE).pack(anchor="w")

        tk.Label(body, text="Describe your problem / symptoms: *",
                 font=FONT_SUB, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 6))
        problem_text = tk.Text(body, height=6, font=FONT_BODY, fg=DARK_TEXT,
                               bg=WHITE, relief="solid", bd=1, wrap="word")
        problem_text.pack(fill="x")

        def submit():
            prob = problem_text.get("1.0", "end").strip()
            if not prob:
                messagebox.showwarning("Missing", "Please describe your problem.", parent=win)
                return
            num = database.book_appointment(self.user['user_id'], doctor['user_id'], prob)
            messagebox.showinfo("Booked! ✓",
                f"Appointment booked!\nYour queue number: #{num}\n"
                f"Doctor: Dr. {doctor['name']}\nPayment will be processed after prescription.",
                parent=win)
            win.destroy()
            self._tab_doctors()

        btn_row = tk.Frame(body, bg=WHITE)
        btn_row.pack(fill="x", pady=16)
        make_button(btn_row, "  Confirm Booking  ", submit, color=CYAN_DARK, pady=10, padx=20).pack(side="left")
        make_button(btn_row, "  Cancel  ", win.destroy, color=GRAY, pady=10, padx=16).pack(side="left", padx=8)

    # ─── MY APPOINTMENTS ───────────────────────────────────────────
    def _tab_appointments(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=NAVY_LIGHT, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📅 My Appointments & Waiting List",
                 font=FONT_TITLE, fg=WHITE, bg=NAVY_LIGHT).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        appts = database.get_patient_appointments(self.user['user_id'])

        if not appts:
            tk.Label(body, text="You have no appointments yet.\nGo to 'Find Doctors' to book one!",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE, justify="center").pack(pady=60)
            return

        for a in appts:
            card_outer, card = make_card(body, bg=WHITE)
            card_outer.pack(fill="x", pady=6)

            left = tk.Frame(card, bg=WHITE)
            left.pack(side="left", fill="y")

            num_frame = tk.Frame(left, bg=BLUE, padx=16, pady=12)
            num_frame.pack()
            tk.Label(num_frame, text=f"#{a.get('waiting_number', '?')}",
                     font=("Georgia", 24, "bold"), fg=WHITE, bg=BLUE).pack()
            tk.Label(num_frame, text="Queue", font=FONT_SMALL, fg=WHITE, bg=BLUE).pack()

            info = tk.Frame(card, bg=WHITE, padx=16)
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=f"Dr. {a.get('doctor_name', a['doctor_id'])}",
                     font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(info, text=f"Problem: {(a.get('problem') or 'N/A')[:60]}",
                     font=FONT_BODY, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x", pady=2)

            status_colors = {'waiting': GOLD, 'prescribed': GREEN, 'done': GRAY, 'cancelled': RED}
            status = a.get('status', 'waiting')
            tag_label(info, status.upper(), color=status_colors.get(status, GRAY)).pack(anchor="w", pady=4)

            if status == 'waiting':
                def cancel_appt(aid=a['id']):
                    if messagebox.askyesno("Cancel?", "Cancel this appointment?"):
                        database.cancel_appointment(aid)
                        self._tab_appointments()
                make_button(card, "Cancel", cancel_appt, color=RED, pady=6, padx=12).pack(side="right")

    # ─── MEDICINE SHOP ─────────────────────────────────────────────
    def _tab_medicine(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=PURPLE, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💊 Medicine Shop",
                 font=FONT_TITLE, fg=WHITE, bg=PURPLE).pack(padx=32, anchor="w")
        tk.Label(hdr, text="Search and order medicines from our verified pharmacy",
                 font=FONT_BODY, fg=OFF_WHITE, bg=PURPLE).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # Search row
        search_row = tk.Frame(body, bg=OFF_WHITE)
        search_row.pack(fill="x", pady=(0, 14))
        tk.Label(search_row, text="Search Medicine:", font=FONT_SUB, fg=NAVY, bg=OFF_WHITE).pack(side="left")
        self.med_search = tk.StringVar()
        se = make_entry(search_row, width=28)
        se.pack(side="left", padx=8, ipady=4)
        se.bind("<KeyRelease>", lambda e: self._refresh_medicines())

        # Medicine list
        scroll_outer, _, scroll_inner = scrollable_frame(body, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)
        self._med_frame = scroll_inner

        self._refresh_medicines()

    def _refresh_medicines(self):
        for w in self._med_frame.winfo_children():
            w.destroy()
        meds = database.get_all_medicines()
        search = getattr(self, 'med_search', tk.StringVar()).get().lower()
        if search:
            meds = [m for m in meds if search in m['name'].lower()]
        meds = [m for m in meds if m['quantity'] > 0]

        if not meds:
            tk.Label(self._med_frame, text="No medicines in stock matching your search.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for med in meds:
            card_outer, card = make_card(self._med_frame, bg=WHITE, padx=16, pady=12)
            card_outer.pack(fill="x", pady=5)

            icon = tk.Label(card, text="💊", font=("Helvetica", 28), bg=WHITE)
            icon.pack(side="left")

            info = tk.Frame(card, bg=WHITE, padx=16)
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=med['name'], font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            detail_row = tk.Frame(info, bg=WHITE)
            detail_row.pack(fill="x", pady=3)
            tag_label(detail_row, f"৳ {med['price']:.2f} / unit", color=GREEN).pack(side="left")
            tag_label(detail_row, f"Stock: {med['quantity']}", color=BLUE).pack(side="left", padx=6)

            order_frame = tk.Frame(card, bg=WHITE)
            order_frame.pack(side="right", padx=10)
            tk.Label(order_frame, text="Qty:", font=FONT_BODY, fg=NAVY, bg=WHITE).pack(side="left")
            qty_var = tk.StringVar(value="1")
            qty_e = tk.Entry(order_frame, textvariable=qty_var, width=4, font=FONT_BODY,
                             relief="solid", bd=1, justify="center")
            qty_e.pack(side="left", padx=4, ipady=3)

            def order(m=med, qv=qty_var):
                try:
                    q = int(qv.get())
                    if q < 1:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Invalid", "Enter a valid quantity.")
                    return
                ok, msg = database.order_medicine(self.user['user_id'], m['name'], q)
                if ok:
                    messagebox.showinfo("Order Placed ✓", msg)
                    self._tab_medicine()
                else:
                    messagebox.showerror("Error", msg)

            make_button(order_frame, "Order", order, color=CYAN_DARK, pady=6, padx=10).pack(side="left")

    # ─── FUNDING ───────────────────────────────────────────────────
    def _tab_funding(self):
        self._clear_content()
        c = self.content

        hdr = tk.Frame(c, bg=ORANGE, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="❤️ Community Funding",
                 font=FONT_TITLE, fg=WHITE, bg=ORANGE).pack(padx=32, anchor="w")
        tk.Label(hdr, text="Create campaigns and support fellow patients",
                 font=FONT_BODY, fg=OFF_WHITE, bg=ORANGE).pack(padx=32, anchor="w")

        body = tk.Frame(c, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tabs = ttk.Notebook(body)
        tabs.pack(fill="both", expand=True)

        # Browse campaigns
        browse_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(browse_frame, text="Browse Campaigns")
        self._build_browse_campaigns(browse_frame)

        # My campaigns
        my_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(my_frame, text="My Campaigns")
        self._build_my_campaigns(my_frame)

        # Create campaign
        create_frame = tk.Frame(tabs, bg=WHITE, padx=30, pady=20)
        tabs.add(create_frame, text="+ Create Campaign")
        self._build_create_campaign(create_frame)

    def _build_browse_campaigns(self, parent):
        campaigns = database.get_approved_campaigns()
        scroll_outer, _, scroll_inner = scrollable_frame(parent, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        if not campaigns:
            tk.Label(scroll_inner, text="No approved campaigns yet.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for camp in campaigns:
            card_outer, card = make_card(scroll_inner, padx=20, pady=16)
            card_outer.pack(fill="x", pady=6, padx=10)

            tk.Label(card, text=camp['title'], font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(card, text=f"By: {camp['creator_name']}",
                     font=FONT_SMALL, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(card, text=camp.get('description', '')[:80],
                     font=FONT_BODY, fg=DARK_TEXT, bg=WHITE, anchor="w", wraplength=500).pack(fill="x", pady=4)

            # Progress
            target = camp['target_amount']
            raised = camp['raised_amount']
            pct = min(100, int((raised / target) * 100)) if target > 0 else 0

            prog_bg = tk.Frame(card, bg=GRAY_LIGHT, height=10)
            prog_bg.pack(fill="x", pady=4)
            prog_bg.pack_propagate(False)
            prog_fill = tk.Frame(prog_bg, bg=GREEN, height=10, width=max(1, int(pct * 4)))
            prog_fill.pack(side="left", fill="y")

            info_row = tk.Frame(card, bg=WHITE)
            info_row.pack(fill="x", pady=2)
            tk.Label(info_row, text=f"Raised: ৳{raised:.2f} / Target: ৳{target:.2f} ({pct}%)",
                     font=FONT_SMALL, fg=GREEN, bg=WHITE).pack(side="left")

            def donate(cid=camp['id'], cname=camp['title']):
                self._donate_dialog(cid, cname)
            make_button(card, "Donate ❤️", donate, color=ORANGE, pady=7, padx=14).pack(anchor="e")

    def _donate_dialog(self, campaign_id, campaign_title):
        win = tk.Toplevel(self.root)
        win.title(f"Donate to: {campaign_title}")
        win.geometry("400x280")
        win.configure(bg=WHITE)
        win.grab_set()

        tk.Label(win, text=f"Donate to\n{campaign_title}",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(pady=20)

        tk.Label(win, text="Your Name (optional):", font=FONT_BODY, fg=NAVY, bg=WHITE).pack(anchor="w", padx=30)
        name_e = make_entry(win, width=32)
        name_e.pack(padx=30, pady=4, ipady=4, fill="x")

        tk.Label(win, text="Donation Amount (৳):", font=FONT_BODY, fg=NAVY, bg=WHITE).pack(anchor="w", padx=30)
        amt_e = make_entry(win, width=32)
        amt_e.pack(padx=30, pady=4, ipady=4, fill="x")

        def submit():
            try:
                amt = float(amt_e.get())
                if amt <= 0: raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a valid positive amount.", parent=win)
                return
            donor = name_e.get().strip() or "Anonymous"
            database.donate_to_campaign(campaign_id, donor, amt)
            messagebox.showinfo("Thank You! ❤️", f"You donated ৳{amt:.2f}.\nThank you, {donor}!", parent=win)
            win.destroy()

        make_button(win, "Donate Now ❤️", submit, color=ORANGE, pady=10).pack(pady=16)

    def _build_my_campaigns(self, parent):
        campaigns = database.get_patient_campaigns(self.user['user_id'])
        scroll_outer, _, scroll_inner = scrollable_frame(parent, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        if not campaigns:
            tk.Label(scroll_inner, text="You haven't created any campaigns yet.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for camp in campaigns:
            card_outer, card = make_card(scroll_inner, padx=20, pady=14)
            card_outer.pack(fill="x", pady=6, padx=10)
            tk.Label(card, text=camp['title'], font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            status = "Approved ✓" if camp['approved'] else "Pending Approval..."
            color = GREEN if camp['approved'] else GOLD
            tag_label(card, status, color=color).pack(anchor="w", pady=4)
            tk.Label(card, text=f"Target: ৳{camp['target_amount']:.2f} | Raised: ৳{camp['raised_amount']:.2f}",
                     font=FONT_BODY, fg=DARK_TEXT, bg=WHITE).pack(anchor="w")

    def _build_create_campaign(self, parent):
        tk.Label(parent, text="Create Funding Campaign",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 16))

        tk.Label(parent, text="Campaign Title *", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        title_e = make_entry(parent, width=40)
        title_e.pack(fill="x", pady=(2, 12), ipady=4)

        tk.Label(parent, text="Description *", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        desc_t = tk.Text(parent, height=5, font=FONT_BODY, relief="solid", bd=1)
        desc_t.pack(fill="x", pady=(2, 12))

        tk.Label(parent, text="Target Amount (৳) *", font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
        target_e = make_entry(parent, width=20)
        target_e.pack(fill="x", pady=(2, 16), ipady=4)

        def submit():
            title = title_e.get().strip()
            desc  = desc_t.get("1.0", "end").strip()
            target_s = target_e.get().strip()
            if not title or not desc:
                messagebox.showwarning("Missing", "Title and description are required.")
                return
            try:
                target = float(target_s)
                if target <= 0: raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a valid target amount.")
                return
            database.create_campaign(self.user['user_id'], title, desc, target)
            messagebox.showinfo("Submitted!",
                "Your campaign has been submitted.\nAn admin will review and approve it soon.")
            title_e.delete(0, "end")
            desc_t.delete("1.0", "end")
            target_e.delete(0, "end")
            self._tab_funding()

        make_button(parent, "  Submit Campaign  ", submit, color=ORANGE, pady=10, padx=20).pack(pady=(0, 10))

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logout_cb()