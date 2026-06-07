import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import *


class AdminPortal:
    def __init__(self, root, user, logout_cb):
        self.root = root
        self.user = user
        self.logout_cb = logout_cb
        self._build()

    def _build(self):
        for w in self.root.winfo_children():
            w.destroy()
        root = self.root
        root.title(f"MEDIPLUS — Admin Console | {self.user['name']}")

        # ── Top Nav ────────────────────────────────────────────────
        nav = tk.Frame(root, bg=NAVY)
        nav.pack(fill="x")
        tk.Frame(nav, bg=GOLD, height=4).pack(fill="x")
        nav_inner = tk.Frame(nav, bg=NAVY, pady=12)
        nav_inner.pack(fill="x", padx=24)
        tk.Label(nav_inner, text="✚ MEDIPLUS", font=("Georgia", 16, "bold"),
                 fg=GOLD, bg=NAVY).pack(side="left")
        tk.Label(nav_inner, text="  ADMIN CONSOLE",
                 font=("Helvetica", 12, "bold"), fg=WHITE, bg=NAVY).pack(side="left", padx=12)
        tag_label(nav_inner, "ADMINISTRATOR", color=GOLD).pack(side="left")

        right_nav = tk.Frame(nav_inner, bg=NAVY)
        right_nav.pack(side="right")
        tk.Label(right_nav, text=f"⚡ {self.user['name']}",
                 font=FONT_SUB, fg=GOLD, bg=NAVY).pack(side="left", padx=12)
        make_button(right_nav, "Logout", self._logout, color=RED, padx=14, pady=6).pack(side="left")

        # ── Layout ─────────────────────────────────────────────────
        body = tk.Frame(root, bg=OFF_WHITE)
        body.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg=NAVY_LIGHT, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="ADMIN MENU", font=("Helvetica", 9, "bold"),
                 fg=GRAY, bg=NAVY_LIGHT).pack(pady=(24, 8), padx=16, anchor="w")

        self._sidebar_btns = {}
        menu_items = [
            ("🏠", "Dashboard", self._tab_dashboard),
            ("✅", "Verify Users", self._tab_verify),
            ("💊", "Medicine Storage", self._tab_medicine),
            ("💰", "Payments", self._tab_payments),
            ("📋", "Prescriptions", self._tab_prescriptions),
            ("🛒", "Medicine Orders", self._tab_orders),
            ("❤️", "Funding", self._tab_funding),
            ("👥", "All Users", self._tab_users),
        ]
        for icon, label, cmd in menu_items:
            btn = tk.Button(sidebar, text=f"  {icon}  {label}",
                            font=FONT_BODY, bg=NAVY_LIGHT, fg=WHITE,
                            relief="flat", bd=0, anchor="w",
                            cursor="hand2", padx=16, pady=12,
                            activebackground=GOLD, activeforeground=DARK_TEXT)
            btn.pack(fill="x")
            btn.config(command=lambda c=cmd, b=btn, lbl=label: self._sidebar_select(b, lbl, c))
            self._sidebar_btns[label] = btn

        self.content = tk.Frame(body, bg=OFF_WHITE)
        self.content.pack(side="right", fill="both", expand=True)

        self._sidebar_select(self._sidebar_btns["Dashboard"], "Dashboard", self._tab_dashboard)

    def _sidebar_select(self, active_btn, label, cmd):
        for lbl, btn in self._sidebar_btns.items():
            btn.config(bg=GOLD if lbl == label else NAVY_LIGHT,
                       fg=DARK_TEXT if lbl == label else WHITE)
        cmd()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _page_header(self, title, subtitle="", color=NAVY):
        hdr = tk.Frame(self.content, bg=color, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=FONT_TITLE, fg=WHITE, bg=color).pack(padx=32, anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONT_BODY, fg=OFF_WHITE, bg=color).pack(padx=32, anchor="w")
        return hdr

    # ─── DASHBOARD ─────────────────────────────────────────────────
    def _tab_dashboard(self):
        self._clear_content()
        self._page_header("⚡ Admin Dashboard", "System overview and quick stats", NAVY)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        doctors = database.get_all_doctors_interns()
        pending = [d for d in doctors if not d['approved']]
        approved = [d for d in doctors if d['approved']]
        payments = database.get_all_payments()
        pending_pay = [p for p in payments if p['status'] == 'pending']
        campaigns = database.get_all_campaigns()

        stats = [
            ("Pending Verifications", len(pending), RED),
            ("Approved Doctors", len(approved), GREEN),
            ("Pending Payments", len(pending_pay), GOLD),
            ("Total Campaigns", len(campaigns), PURPLE),
        ]
        stats_row = tk.Frame(body, bg=OFF_WHITE)
        stats_row.pack(fill="x", pady=(0, 24))
        for lbl, val, col in stats:
            sf = stat_card(stats_row, lbl, val, color=col)
            sf.pack(side="left", padx=(0, 12))

        # Quick actions
        card_outer, card = make_card(body, padx=24, pady=20)
        card_outer.pack(fill="x")
        tk.Label(card, text="Quick Actions", font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 16))
        actions_row = tk.Frame(card, bg=WHITE)
        actions_row.pack(fill="x")
        quick = [
            ("✅ Verify Users", self._tab_verify, BLUE),
            ("💰 Review Payments", self._tab_payments, GREEN),
            ("❤️ Approve Campaigns", self._tab_funding, ORANGE),
            ("💊 Manage Medicines", self._tab_medicine, PURPLE),
        ]
        for lbl, cmd, col in quick:
            make_button(actions_row, lbl, cmd, color=col, pady=10, padx=14).pack(side="left", padx=6)

        # Recent payments
        pay_card_outer, pay_card = make_card(body, padx=24, pady=20)
        pay_card_outer.pack(fill="x", pady=14)
        tk.Label(pay_card, text="Recent Payments", font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 10))
        cols = ("Patient", "Doctor", "Amount", "Status", "Date")
        tree = ttk.Treeview(pay_card, columns=cols, show="headings", height=5)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        tree.pack(fill="x")
        for pay in payments[:8]:
            tree.insert("", "end", values=(
                pay.get('patient_name', pay['patient_id']),
                pay.get('doctor_name', pay['doctor_id']),
                f"৳{pay['amount']:.2f}",
                pay['status'].upper(),
                (pay.get('created_at') or '')[:10]
            ))

    # ─── VERIFY USERS ──────────────────────────────────────────────
    def _tab_verify(self):
        self._clear_content()
        self._page_header("✅ Verify Doctors & Interns",
                           "Review and approve new doctor/intern registrations", BLUE)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tabs = ttk.Notebook(body)
        tabs.pack(fill="both", expand=True)

        pending_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(pending_frame, text="Pending Approval")
        self._build_verify_list(pending_frame, approved=False)

        approved_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(approved_frame, text="Approved")
        self._build_verify_list(approved_frame, approved=True)

    def _build_verify_list(self, parent, approved):
        doctors = database.get_all_doctors_interns()
        filtered = [d for d in doctors if bool(d['approved']) == approved]

        scroll_outer, _, scroll_inner = scrollable_frame(parent, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        if not filtered:
            msg = "No approved doctors." if approved else "No pending verifications. 🎉"
            tk.Label(scroll_inner, text=msg, font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for doc in filtered:
            card_outer, card = make_card(scroll_inner, padx=20, pady=16)
            card_outer.pack(fill="x", pady=6)

            left = tk.Frame(card, bg=WHITE)
            left.pack(side="left", fill="y")
            avatar_color = PURPLE if doc['user_type'] == 'intern' else BLUE
            av = tk.Frame(left, bg=avatar_color, padx=14, pady=14)
            av.pack()
            ltr = doc['name'][0].upper() if doc['name'] else "D"
            tk.Label(av, text=ltr, font=("Georgia", 24, "bold"), fg=WHITE, bg=avatar_color).pack()

            info = tk.Frame(card, bg=WHITE, padx=16)
            info.pack(side="left", fill="both", expand=True)

            name_row = tk.Frame(info, bg=WHITE)
            name_row.pack(fill="x")
            tk.Label(name_row, text=f"Dr. {doc['name']}",
                     font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(side="left")
            dtype = "Intern" if doc['user_type'] == 'intern' else "Doctor"
            tag_label(name_row, dtype.upper(), color=avatar_color).pack(side="left", padx=8)

            details = [
                ("User ID", doc['user_id']),
                ("NID", doc['nid']),
                ("Age", f"{doc.get('age','?')} years"),
                ("Gender", doc.get('gender', '?')),
                ("Specialization", doc.get('specialization', 'N/A')),
            ]
            if doc['user_type'] == 'doctor':
                details.append(("Degree", doc.get('degree', 'N/A')))
            else:
                details.append(("Institution", doc.get('institution', 'N/A')))
                details.append(("Joined", doc.get('joined_date', 'N/A')))

            detail_grid = tk.Frame(info, bg=WHITE)
            detail_grid.pack(fill="x", pady=4)
            for i, (lbl, val) in enumerate(details):
                col = i % 3
                row_num = i // 3
                df = tk.Frame(detail_grid, bg=WHITE)
                df.grid(row=row_num, column=col, sticky="w", padx=(0, 20), pady=1)
                tk.Label(df, text=f"{lbl}: ", font=FONT_SUB, fg=GRAY, bg=WHITE).pack(side="left")
                tk.Label(df, text=val, font=FONT_BODY, fg=DARK_TEXT, bg=WHITE).pack(side="left")

            if not approved:
                btn_frame = tk.Frame(card, bg=WHITE)
                btn_frame.pack(side="right", padx=10)

                def approve(uid=doc['user_id']):
                    if messagebox.askyesno("Approve?", f"Approve Dr. {doc['name']}?"):
                        database.approve_user(uid)
                        messagebox.showinfo("Approved ✓", f"Dr. {doc['name']} is now approved!")
                        self._tab_verify()

                def reject(uid=doc['user_id'], dname=doc['name']):
                    if messagebox.askyesno("Reject?", f"Reject and DELETE Dr. {dname}'s account?\nThis cannot be undone."):
                        database.reject_user(uid)
                        messagebox.showinfo("Rejected", f"{dname}'s account has been removed.")
                        self._tab_verify()

                make_button(btn_frame, "✓ Approve", approve, color=GREEN, pady=8, padx=12).pack(pady=(0, 6))
                make_button(btn_frame, "✗ Reject", reject, color=RED, pady=8, padx=12).pack()
            else:
                tag_label(card, "APPROVED ✓", color=GREEN).pack(side="right", padx=10)

    # ─── MEDICINE STORAGE ──────────────────────────────────────────
    def _tab_medicine(self):
        self._clear_content()
        self._page_header("💊 Medicine Storage", "Manage inventory, stock, and pricing", PURPLE)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # Add / Update form
        form_outer, form = make_card(body, padx=24, pady=16)
        form_outer.pack(fill="x", pady=(0, 14))
        tk.Label(form, text="Add / Restock Medicine", font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(form, bg=WHITE)
        row.pack(fill="x")

        tk.Label(row, text="Medicine Name:", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(side="left")
        name_e = make_entry(row, width=20)
        name_e.pack(side="left", padx=8, ipady=4)

        tk.Label(row, text="Quantity:", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(side="left")
        qty_e = make_entry(row, width=8)
        qty_e.pack(side="left", padx=8, ipady=4)

        tk.Label(row, text="Price (৳):", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(side="left")
        price_e = make_entry(row, width=8)
        price_e.pack(side="left", padx=8, ipady=4)

        def add_med():
            name = name_e.get().strip()
            qty_s = qty_e.get().strip()
            price_s = price_e.get().strip()
            if not name or not qty_s or not price_s:
                messagebox.showwarning("Missing", "All fields are required.")
                return
            try:
                qty = int(qty_s)
                price = float(price_s)
                if qty < 0 or price < 0: raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Quantity must be integer, price must be a number.")
                return
            database.add_medicine(name, qty, price)
            messagebox.showinfo("Added ✓", f"'{name}' updated in storage!")
            name_e.delete(0, "end")
            qty_e.delete(0, "end")
            price_e.delete(0, "end")
            self._tab_medicine()

        make_button(row, "+ Add / Restock", add_med, color=PURPLE, pady=8, padx=14).pack(side="left", padx=12)

        # Medicine table
        table_outer, table_card = make_card(body, padx=24, pady=16)
        table_outer.pack(fill="both", expand=True)
        tk.Label(table_card, text="Current Inventory",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(0, 10))

        cols = ("ID", "Medicine Name", "Quantity", "Price (৳)", "Action")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("ID", width=50, anchor="center")
        tree.column("Medicine Name", width=220, anchor="w")
        tree.column("Quantity", width=100, anchor="center")
        tree.column("Price (৳)", width=100, anchor="center")
        tree.column("Action", width=100, anchor="center")
        tree.pack(fill="both", expand=True)

        meds = database.get_all_medicines()
        self._med_tree = tree
        self._med_data = meds
        for med in meds:
            stock_status = "✅" if med['quantity'] > 10 else "⚠️" if med['quantity'] > 0 else "❌ OUT"
            tree.insert("", "end", iid=str(med['id']), values=(
                med['id'], med['name'], f"{med['quantity']} {stock_status}",
                f"৳{med['price']:.2f}", "Edit | Delete"
            ))

        btn_frame = tk.Frame(table_card, bg=WHITE)
        btn_frame.pack(fill="x", pady=10)

        def edit_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Please select a medicine to edit.")
                return
            med_id = int(sel[0])
            med = next((m for m in meds if m['id'] == med_id), None)
            if med:
                self._edit_medicine_dialog(med)

        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Please select a medicine to delete.")
                return
            med_id = int(sel[0])
            med = next((m for m in meds if m['id'] == med_id), None)
            if med and messagebox.askyesno("Delete?", f"Delete '{med['name']}' from inventory?"):
                database.delete_medicine(med_id)
                messagebox.showinfo("Deleted", f"'{med['name']}' has been removed.")
                self._tab_medicine()

        make_button(btn_frame, "✏️ Edit Selected", edit_selected, color=BLUE, pady=8, padx=14).pack(side="left", padx=(0, 8))
        make_button(btn_frame, "🗑 Delete Selected", delete_selected, color=RED, pady=8, padx=14).pack(side="left")

    def _edit_medicine_dialog(self, med):
        win = tk.Toplevel(self.root)
        win.title(f"Edit — {med['name']}")
        win.geometry("400x300")
        win.configure(bg=WHITE)
        win.grab_set()

        tk.Label(win, text=f"Edit Medicine: {med['name']}",
                 font=FONT_HEADING, fg=NAVY, bg=WHITE).pack(pady=20)

        fields_frame = tk.Frame(win, bg=WHITE, padx=30)
        fields_frame.pack(fill="x")

        for lbl, key, val in [("Name:", "name", med['name']),
                               ("Quantity:", "qty", str(med['quantity'])),
                               ("Price (৳):", "price", str(med['price']))]:
            row = tk.Frame(fields_frame, bg=WHITE)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=lbl, font=FONT_SUB, fg=NAVY, bg=WHITE, width=12, anchor="w").pack(side="left")
            e = make_entry(row, width=20)
            e.insert(0, val)
            e.pack(side="left", ipady=4)
            if key == "name": name_e = e
            elif key == "qty": qty_e = e
            else: price_e = e

        def save():
            name = name_e.get().strip()
            try:
                qty = int(qty_e.get())
                price = float(price_e.get())
            except ValueError:
                messagebox.showwarning("Invalid", "Check quantity and price values.", parent=win)
                return
            database.update_medicine(med['id'], name, qty, price)
            messagebox.showinfo("Updated ✓", f"'{name}' has been updated.", parent=win)
            win.destroy()
            self._tab_medicine()

        btn_row = tk.Frame(win, bg=WHITE)
        btn_row.pack(pady=16)
        make_button(btn_row, "Save Changes", save, color=GREEN, pady=8, padx=16).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", win.destroy, color=GRAY, pady=8, padx=16).pack(side="left")

    # ─── PAYMENTS ──────────────────────────────────────────────────
    def _tab_payments(self):
        self._clear_content()
        self._page_header("💰 Payment Management",
                           "Review payments — approve only after prescription is issued", GREEN)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        payments = database.get_all_payments()

        if not payments:
            tk.Label(body, text="No payment records found.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        scroll_outer, _, scroll_inner = scrollable_frame(body, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        for pay in payments:
            status = pay['status']
            status_colors = {'pending': GOLD, 'approved': GREEN, 'rejected': RED}
            card_outer, card = make_card(scroll_inner, padx=20, pady=14)
            card_outer.pack(fill="x", pady=5)

            # Amount badge
            amt_f = tk.Frame(card, bg=GREEN if status == 'approved' else GOLD, padx=16, pady=12)
            amt_f.pack(side="left")
            tk.Label(amt_f, text=f"৳{pay['amount']:.2f}",
                     font=("Georgia", 18, "bold"), fg=WHITE, bg=amt_f['bg']).pack()
            tk.Label(amt_f, text="Amount", font=FONT_SMALL, fg=WHITE, bg=amt_f['bg']).pack()

            info = tk.Frame(card, bg=WHITE, padx=16)
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=f"Patient: {pay.get('patient_name', pay['patient_id'])}",
                     font=FONT_SUB, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(info, text=f"Doctor: Dr. {pay.get('doctor_name', pay['doctor_id'])}",
                     font=FONT_BODY, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(info, text=f"Date: {(pay.get('created_at') or '')[:16]}",
                     font=FONT_SMALL, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x", pady=2)
            tag_label(info, status.upper(), color=status_colors.get(status, GRAY)).pack(anchor="w", pady=3)

            if status == 'pending':
                def approve_pay(pid=pay['id'], pdata=pay):
                    has_presc = database.has_prescription_for_payment(pid)
                    if not has_presc:
                        messagebox.showwarning("Cannot Approve",
                            "Doctor has not issued a prescription yet.\n"
                            "Payment can only be approved after prescription.")
                        return
                    if messagebox.askyesno("Approve Payment?",
                            f"Approve ৳{pdata['amount']:.2f} from {pdata.get('patient_name','?')}\n"
                            f"to Dr. {pdata.get('doctor_name','?')}?"):
                        database.approve_payment(pid)
                        messagebox.showinfo("Approved ✓", "Payment approved and credited to doctor.")
                        self._tab_payments()

                make_button(card, "✓ Approve", approve_pay, color=GREEN, pady=8, padx=12).pack(side="right", padx=6)

    # ─── PRESCRIPTIONS ─────────────────────────────────────────────
    def _tab_prescriptions(self):
        self._clear_content()
        self._page_header("📋 Prescription Records",
                           "View all prescriptions issued by doctors", NAVY_LIGHT)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        prescriptions = database.get_all_prescriptions()

        if not prescriptions:
            tk.Label(body, text="No prescriptions recorded yet.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        # Table view
        cols = ("Date", "Doctor", "Patient", "Medicines", "Notes")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("Date", width=120, anchor="center")
        tree.column("Doctor", width=150, anchor="w")
        tree.column("Patient", width=150, anchor="w")
        tree.column("Medicines", width=250, anchor="w")
        tree.column("Notes", width=200, anchor="w")

        vsb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for presc in prescriptions:
            tree.insert("", "end", values=(
                (presc.get('created_at') or '')[:10],
                f"Dr. {presc.get('doctor_name', presc['doctor_id'])}",
                presc.get('patient_name', presc['patient_id']),
                (presc.get('medicines') or '')[:50],
                (presc.get('notes') or '')[:40]
            ))

        # Detail view on click
        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            if idx < len(prescriptions):
                presc = prescriptions[idx]
                self._prescription_detail(presc)

        tree.bind("<Double-1>", on_select)
        tk.Label(body, text="Double-click a row to view full prescription details",
                 font=FONT_SMALL, fg=GRAY, bg=OFF_WHITE).pack(side="bottom", pady=4)

    def _prescription_detail(self, presc):
        win = tk.Toplevel(self.root)
        win.title("Prescription Detail")
        win.geometry("520x400")
        win.configure(bg=WHITE)
        win.grab_set()

        hdr = tk.Frame(win, bg=NAVY, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📋 Prescription Detail",
                 font=FONT_HEADING, fg=WHITE, bg=NAVY).pack(padx=20, anchor="w")

        body = tk.Frame(win, bg=WHITE, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        fields = [
            ("Date", (presc.get('created_at') or '')[:16]),
            ("Doctor", f"Dr. {presc.get('doctor_name', presc['doctor_id'])}"),
            ("Patient", presc.get('patient_name', presc['patient_id'])),
        ]
        for lbl, val in fields:
            row = tk.Frame(body, bg=WHITE)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{lbl}:", font=FONT_SUB, fg=GRAY, bg=WHITE, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_BODY, fg=DARK_TEXT, bg=WHITE).pack(side="left")

        tk.Frame(body, bg=GRAY_LIGHT, height=1).pack(fill="x", pady=12)

        tk.Label(body, text="Medicines Prescribed:", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(anchor="w")
        med_box = tk.Text(body, height=4, font=FONT_BODY, bg=OFF_WHITE, relief="flat", bd=0)
        med_box.insert("1.0", presc.get('medicines', 'N/A'))
        med_box.config(state="disabled")
        med_box.pack(fill="x", pady=4)

        if presc.get('notes'):
            tk.Label(body, text="Dosage Notes:", font=FONT_SUB, fg=NAVY, bg=WHITE).pack(anchor="w", pady=(8, 0))
            notes_box = tk.Text(body, height=3, font=FONT_BODY, bg=OFF_WHITE, relief="flat", bd=0)
            notes_box.insert("1.0", presc['notes'])
            notes_box.config(state="disabled")
            notes_box.pack(fill="x", pady=4)

        make_button(body, "Close", win.destroy, color=NAVY, pady=8, padx=20).pack(pady=12)

    # ─── MEDICINE ORDERS ───────────────────────────────────────────
    def _tab_orders(self):
        self._clear_content()
        self._page_header("🛒 Medicine Orders",
                           "View all patient medicine orders and details", PURPLE)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        orders = database.get_all_medicine_orders()
        if not orders:
            tk.Label(body, text="No medicine orders yet.",
                     font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        cols = ("Date", "Patient", "Medicine", "Qty", "Unit Price", "Total Cost", "Status")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
        tree.column("Date", width=110, anchor="center")
        tree.column("Patient", width=140, anchor="w")
        tree.column("Medicine", width=160, anchor="w")
        tree.column("Qty", width=60, anchor="center")
        tree.column("Unit Price", width=90, anchor="center")
        tree.column("Total Cost", width=100, anchor="center")
        tree.column("Status", width=90, anchor="center")

        vsb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for order in orders:
            tree.insert("", "end", values=(
                (order.get('created_at') or '')[:10],
                order.get('patient_name', order['patient_id']),
                order['medicine_name'],
                order['quantity'],
                f"৳{order.get('unit_price', 0):.2f}",
                f"৳{order.get('total_cost', 0):.2f}",
                order.get('status', 'ordered').upper()
            ))

    # ─── FUNDING ───────────────────────────────────────────────────
    def _tab_funding(self):
        self._clear_content()
        self._page_header("❤️ Funding Campaigns",
                           "Review and approve patient funding campaigns", ORANGE)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        tabs = ttk.Notebook(body)
        tabs.pack(fill="both", expand=True)

        pending_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(pending_frame, text="Pending Approval")
        self._build_campaign_list(pending_frame, approved=False)

        approved_frame = tk.Frame(tabs, bg=OFF_WHITE)
        tabs.add(approved_frame, text="Approved Campaigns")
        self._build_campaign_list(approved_frame, approved=True)

    def _build_campaign_list(self, parent, approved):
        campaigns = database.get_all_campaigns()
        filtered = [c for c in campaigns if bool(c['approved']) == approved]

        scroll_outer, _, scroll_inner = scrollable_frame(parent, bg=OFF_WHITE)
        scroll_outer.pack(fill="both", expand=True)

        if not filtered:
            msg = "No approved campaigns." if approved else "No campaigns pending approval. 🎉"
            tk.Label(scroll_inner, text=msg, font=FONT_BODY, fg=GRAY, bg=OFF_WHITE).pack(pady=30)
            return

        for camp in filtered:
            card_outer, card = make_card(scroll_inner, padx=20, pady=16)
            card_outer.pack(fill="x", pady=6)

            info = tk.Frame(card, bg=WHITE)
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=camp['title'], font=FONT_HEADING, fg=NAVY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(info, text=f"By: {camp.get('creator_name', camp['patient_id'])}",
                     font=FONT_SMALL, fg=GRAY, bg=WHITE, anchor="w").pack(fill="x")
            tk.Label(info, text=(camp.get('description') or '')[:80],
                     font=FONT_BODY, fg=DARK_TEXT, bg=WHITE, anchor="w").pack(fill="x", pady=4)

            fin_row = tk.Frame(info, bg=WHITE)
            fin_row.pack(fill="x")
            tag_label(fin_row, f"Target: ৳{camp['target_amount']:.2f}", color=BLUE).pack(side="left")
            tag_label(fin_row, f"Raised: ৳{camp['raised_amount']:.2f}", color=GREEN).pack(side="left", padx=6)
            tag_label(fin_row, f"Date: {(camp.get('created_at') or '')[:10]}", color=GRAY).pack(side="left", padx=6)

            if not approved:
                def approve_c(cid=camp['id'], cname=camp['title']):
                    if messagebox.askyesno("Approve?", f"Approve campaign:\n'{cname}'?"):
                        database.approve_campaign(cid)
                        messagebox.showinfo("Approved ✓", f"Campaign '{cname}' is now live!")
                        self._tab_funding()
                make_button(card, "✓ Approve", approve_c, color=GREEN, pady=8, padx=12).pack(side="right")
            else:
                tag_label(card, "APPROVED ✓", color=GREEN).pack(side="right", padx=10)

    # ─── ALL USERS LIST ────────────────────────────────────────────
    def _tab_users(self):
        self._clear_content()
        self._page_header("👥 All Registered Users", "Complete database of patients and medical staff", NAVY)

        body = tk.Frame(self.content, bg=OFF_WHITE, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # --- ADDED: Remove User Button Container ---
        btn_bar = tk.Frame(body, bg=OFF_WHITE)
        btn_bar.pack(fill="x", pady=(0, 10))

        def handle_delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please select a user from the list to remove.")
                return
            
            # Get data from the selected row
            values = tree.item(selected)['values']
            u_id = values[0]
            u_name = values[1]

            confirm = messagebox.askyesno("Confirm Deletion", 
                f"Are you sure you want to PERMANENTLY delete {u_name} ({u_id})?\n"
                "This will remove their account and all associated data.")
            
            if confirm:
                if database.delete_user(str(u_id)):
                    messagebox.showinfo("Success", f"User {u_name} has been removed.")
                    self._tab_users() # Refresh the list
                else:
                    messagebox.showerror("Error", "Could not delete user from database.")

        make_button(btn_bar, "🗑 Remove Selected User", handle_delete, color=RED, padx=15).pack(side="left")
        # -------------------------------------------

        # Filtering / Search Header
        filter_frame = tk.Frame(body, bg=WHITE, padx=15, pady=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        tk.Label(filter_frame, text="Filter by Type:", font=FONT_SUB, bg=WHITE).pack(side="left")
        
        flt_var = tk.StringVar(value="All")
        cb = ttk.Combobox(filter_frame, textvariable=flt_var, values=["All", "Patient", "Doctor", "Intern"], state="readonly", width=15)
        cb.pack(side="left", padx=10)
        cb.bind("<<ComboboxSelected>>", lambda e: self._tab_users()) # Simplified refresh for this example

        # Fetch Data
        flt = flt_var.get()
        if flt == "All":
            users = database.get_all_users()
        else:
            # Map "Intern" to "intern" for DB query
            db_type = "intern" if flt == "Intern" else flt.lower()
            conn = database.get_connection()
            users = [dict(r) for r in conn.execute("SELECT * FROM users WHERE user_type=? ORDER BY created_at DESC", (db_type,)).fetchall()]
            conn.close()

        cols = ("ID", "Name", "Type", "NID", "Age", "Gender", "Status", "Joined")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=16)
        for col in cols:
            tree.heading(col, text=col)
        
        # Column Widths
        tree.column("ID", width=100, anchor="w")
        tree.column("Name", width=150, anchor="w")
        tree.column("Type", width=80, anchor="center")
        tree.column("NID", width=100, anchor="center")
        tree.column("Age", width=50, anchor="center")
        tree.column("Gender", width=80, anchor="center")
        tree.column("Status", width=90, anchor="center")
        tree.column("Joined", width=100, anchor="center")

        vsb = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for u in users:
            status = "Approved" if u['approved'] else "Pending"
            tree.insert("", "end", values=(
                u['user_id'],
                u['name'],
                u['user_type'].upper(),
                u['nid'],
                u.get('age', 'N/A'),
                u.get('gender', 'N/A'),
                status,
                (u.get('created_at') or '')[:10]
            ))

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout from Admin Console?"):
            self.logout_cb()