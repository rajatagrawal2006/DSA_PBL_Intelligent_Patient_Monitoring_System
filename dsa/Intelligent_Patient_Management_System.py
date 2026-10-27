import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

PATIENT_FILE = "hospital_patients.json"

# ==========================================
# 1. ADVANCED DSA-2 IMPLEMENTATIONS (FROM SCRATCH)
# ==========================================

# --- Stack for Action Audit Log ---
class ActionStack:
    def __init__(self):
        self.stack = []

    def push(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stack.append(f"[{timestamp}] {action}")

    def get_all(self):
        return list(reversed(self.stack))


# --- AVL Tree for Patients ---
class AVLNode:
    def __init__(self, data):
        self.data = data
        self.height = 1
        self.left = None
        self.right = None

class PatientAVLTree:
    def __init__(self):
        self.root = None

    def height(self, node):
        return node.height if node else 0

    def balance_factor(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = max(self.height(y.left), self.height(y.right)) + 1
        x.height = max(self.height(x.left), self.height(x.right)) + 1
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.height(x.left), self.height(x.right)) + 1
        y.height = max(self.height(y.left), self.height(y.right)) + 1
        return y

    def _insert(self, root, p):
        if not root:
            return AVLNode(p), True
        if p["id"] == root.data["id"]:
            return root, False
        if p["id"] < root.data["id"]:
            root.left, inserted = self._insert(root.left, p)
        else:
            root.right, inserted = self._insert(root.right, p)
        if not inserted:
            return root, False

        root.height = 1 + max(self.height(root.left), self.height(root.right))
        balance = self.balance_factor(root)

        if balance > 1 and p["id"] < root.left.data["id"]:
            return self.right_rotate(root), True
        if balance < -1 and p["id"] > root.right.data["id"]:
            return self.left_rotate(root), True
        if balance > 1 and p["id"] > root.left.data["id"]:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root), True
        if balance < -1 and p["id"] < root.right.data["id"]:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root), True
        return root, True

    def insert(self, p):
        self.root, success = self._insert(self.root, p)
        if success: self.save_to_file()
        return success

    def _delete(self, root, patient_id):
        if not root: return root, False
        if patient_id < root.data["id"]:
            root.left, deleted = self._delete(root.left, patient_id)
        elif patient_id > root.data["id"]:
            root.right, deleted = self._delete(root.right, patient_id)
        else:
            deleted = True
            if not root.left: return root.right, True
            elif not root.right: return root.left, True
            temp = self._get_min_value_node(root.right)
            root.data = temp.data
            root.right, _ = self._delete(root.right, temp.data["id"])
        if not root: return root, deleted

        root.height = 1 + max(self.height(root.left), self.height(root.right))
        balance = self.balance_factor(root)
        if balance > 1 and self.balance_factor(root.left) >= 0: return self.right_rotate(root), deleted
        if balance > 1 and self.balance_factor(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root), deleted
        if balance < -1 and self.balance_factor(root.right) <= 0: return self.left_rotate(root), deleted
        if balance < -1 and self.balance_factor(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root), deleted
        return root, deleted

    def delete(self, patient_id):
        self.root, success = self._delete(self.root, patient_id)
        if success: self.save_to_file()
        return success

    def _get_min_value_node(self, node):
        current = node
        while current.left: current = current.left
        return current

    def search(self, patient_id):
        node = self.root
        while node:
            if patient_id == node.data["id"]: return node.data
            elif patient_id < node.data["id"]: node = node.left
            else: node = node.right
        return None

    def inorder(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)

    def save_to_file(self):
        with open(PATIENT_FILE, "w") as f:
            json.dump(self.inorder(), f, indent=4)

    def load_from_file(self):
        if os.path.exists(PATIENT_FILE):
            try:
                with open(PATIENT_FILE, "r") as f:
                    data = json.load(f)
                    for item in data: self.root, _ = self._insert(self.root, item)
            except Exception as e: print("Error loading patients:", e)


# --- Min-Heap for Emergency Triage ---
class CustomMinHeap:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def parent(self, i): return (i - 1) // 2
    def left_child(self, i): return 2 * i + 1
    def right_child(self, i): return 2 * i + 2

    def insert(self, priority, name, condition):
        node = (priority, self.counter, name, condition)
        self.counter += 1
        self.heap.append(node)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, i):
        p = self.parent(i)
        if i > 0 and self.heap[i] < self.heap[p]:
            self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
            self._heapify_up(p)

    def extract_min(self):
        if not self.heap: return None
        if len(self.heap) == 1: return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_down(self, i):
        smallest = i
        l, r, n = self.left_child(i), self.right_child(i), len(self.heap)
        if l < n and self.heap[l] < self.heap[smallest]: smallest = l
        if r < n and self.heap[r] < self.heap[smallest]: smallest = r
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._heapify_down(smallest)

    def view_all(self): return sorted(self.heap)


# --- Graph & Advanced Algorithms ---
class HospitalGraph:
    def __init__(self):
        self.departments = [
            "Main Entrance", "Reception", "Emergency", 
            "Pharmacy", "General Wards", "ICU", "Operation Theater", "Lab"
        ]
        self.matrix = {
            "Main Entrance": {"Main Entrance": 0, "Reception": 50, "Emergency": 30, "Pharmacy": 90, "General Wards": 110, "ICU": 75, "Operation Theater": 100, "Lab": 115},
            "Reception": {"Main Entrance": 50, "Reception": 0, "Emergency": 60, "Pharmacy": 40, "General Wards": 60, "ICU": 90, "Operation Theater": 110, "Lab": 65},
            "Emergency": {"Main Entrance": 30, "Reception": 60, "Emergency": 0, "Pharmacy": 85, "General Wards": 90, "ICU": 45, "Operation Theater": 70, "Lab": 95},
            "Pharmacy": {"Main Entrance": 90, "Reception": 40, "Emergency": 85, "Pharmacy": 0, "General Wards": 75, "ICU": 85, "Operation Theater": 105, "Lab": 25},
            "General Wards": {"Main Entrance": 110, "Reception": 60, "Emergency": 90, "Pharmacy": 75, "General Wards": 0, "ICU": 95, "Operation Theater": 115, "Lab": 35},
            "ICU": {"Main Entrance": 75, "Reception": 90, "Emergency": 45, "Pharmacy": 85, "General Wards": 95, "ICU": 0, "Operation Theater": 20, "Lab": 90},
            "Operation Theater": {"Main Entrance": 100, "Reception": 110, "Emergency": 70, "Pharmacy": 105, "General Wards": 115, "ICU": 20, "Operation Theater": 0, "Lab": 110},
            "Lab": {"Main Entrance": 115, "Reception": 65, "Emergency": 95, "Pharmacy": 25, "General Wards": 35, "ICU": 90, "Operation Theater": 110, "Lab": 0}
        }

    def dijkstra(self, start, end):
        visited = set()
        queue = [(0, start, [start])]
        while queue:
            queue.sort(key=lambda x: x[0])
            cost, node, path = queue.pop(0)
            if node in visited: continue
            visited.add(node)
            if node == end: return cost, path
            for neighbor, weight in self.matrix[node].items():
                if weight > 0 and neighbor not in visited:
                    queue.append((cost + weight, neighbor, path + [neighbor]))
        return float("inf"), []

    def floyd_warshall(self):
        nodes = self.departments
        dist = {i: {j: self.matrix[i][j] if j in self.matrix[i] else float('inf') for j in nodes} for i in nodes}
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        return dist

    def prim_mst(self):
        nodes = self.departments
        visited = {nodes[0]}
        mst_edges = []
        while len(visited) < len(nodes):
            min_wt = float('inf')
            u_sel, v_sel = None, None
            for u in visited:
                for v, wt in self.matrix[u].items():
                    if v not in visited and 0 < wt < min_wt:
                        min_wt = wt
                        u_sel, v_sel = u, v
            if v_sel:
                visited.add(v_sel)
                mst_edges.append((u_sel, v_sel, min_wt))
            else: break
        return mst_edges


# ==========================================
# 2. MAIN APPLICATION GUI
# ==========================================

class CarePointApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CarePoint — Intelligent Hospital Management System")
        self.root.geometry("1200x750")
        self.root.config(bg="#f4f6f9")

        self.audit_stack = ActionStack()
        self.patient_avl = PatientAVLTree()
        self.patient_avl.load_from_file()
        
        if not self.patient_avl.inorder():
            demo_patients = [
                {"id": "PAT-1001", "name": "Ramesh Chander", "age": 58, "gender": "Male", "contact": "+91-91234-56781", "blood": "B+", "allergies": "Penicillin"},
                {"id": "PAT-1002", "name": "Pooja Sundaram", "age": 34, "gender": "Female", "contact": "+91-91234-56782", "blood": "O-", "allergies": "Sulfa drugs"},
                {"id": "PAT-1003", "name": "Harpreet Singh", "age": 46, "gender": "Male", "contact": "+91-91234-56783", "blood": "A+", "allergies": "None"},
                {"id": "PAT-1004", "name": "Fatima Noor", "age": 9, "gender": "Female", "contact": "+91-91234-56784", "blood": "AB+", "allergies": "None"},
                {"id": "PAT-1005", "name": "Devendra Patel", "age": 65, "gender": "Male", "contact": "+91-91234-56785", "blood": "O-", "allergies": "Aspirin"}
            ]
            for p in demo_patients: self.patient_avl.insert(p)

        self.triage_heap = CustomMinHeap()
        self.triage_heap.insert(1, "Ramesh Chander", "Level-1 Resuscitation")
        self.triage_heap.insert(2, "Harpreet Singh", "Level-2 Urgent Trauma")

        self.hospital_graph = HospitalGraph()
        self.audit_stack.push("System initialized successfully.")

        self.doctors_list = [
            {"id": "DOC-101", "name": "Dr. Arvind Sharma", "dept": "General Medicine", "spec": "Consultant Physician", "fee": 600, "hours": "09:00 - 17:00", "status": "Active"},
            {"id": "DOC-102", "name": "Dr. Meenakshi Rao", "dept": "Cardiology", "spec": "Senior Cardiologist", "fee": 1200, "hours": "10:00 - 16:00", "status": "Active"},
            {"id": "DOC-103", "name": "Dr. Rajesh Kulkarni", "dept": "Orthopaedics", "spec": "Trauma Surgeon", "fee": 850, "hours": "09:30 - 15:30", "status": "Active"},
            {"id": "DOC-104", "name": "Dr. Sneha Pillai", "dept": "Paediatrics", "spec": "Paediatrician", "fee": 550, "hours": "09:00 - 14:00", "status": "Active"},
            {"id": "DOC-105", "name": "Dr. Vikrant Verma", "dept": "Dermatology", "spec": "Dermatologist", "fee": 700, "hours": "11:00 - 17:00", "status": "Active"}
        ]

        self.appointments_list = [
            {"apt_id": "APT-5001", "patient": "Ramesh Chander", "dept": "General Medicine", "doctor": "Dr. Arvind Sharma", "schedule": "2026-10-28 09:30", "status": "Scheduled"},
            {"apt_id": "APT-5002", "patient": "Pooja Sundaram", "dept": "Cardiology", "doctor": "Dr. Meenakshi Rao", "schedule": "2026-10-27 10:30", "status": "Completed"}
        ]

        self.create_sidebar()
        self.create_topbar()
        self.create_main_content_area()
        self.show_dashboard()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#0f172a", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        brand_frame = tk.Frame(self.sidebar, bg="#0f172a", pady=15)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="+ CAREPOINT", font=("Arial", 14, "bold"), bg="#0f172a", fg="white").pack(anchor="w", padx=15)
        tk.Label(brand_frame, text="Intelligent Hospital System", font=("Arial", 9), bg="#0f172a", fg="#94a3b8").pack(anchor="w", padx=15)

        separator = tk.Frame(self.sidebar, height=1, bg="#1e293b")
        separator.pack(fill=tk.X, padx=10, pady=5)

        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Patients", self.show_patients),
            ("Doctors", self.show_doctors),
            ("Appointments", self.show_appointments),
            ("Billing & Payments", self.show_billing),
            ("Emergency & Triage", self.show_triage),
            ("Campus Navigation", self.show_navigation),
            ("System Audit", self.show_audit)
        ]

        self.nav_buttons = {}
        for name, cmd in nav_items:
            btn = tk.Button(self.sidebar, text=name, font=("Arial", 10), bg="#0f172a", fg="#cbd5e1", 
                            activebackground="#1e293b", activeforeground="white", bd=0, anchor="w", padx=20, pady=8, command=cmd)
            btn.pack(fill=tk.X, pady=2)
            self.nav_buttons[name] = btn

        footer_frame = tk.Frame(self.sidebar, bg="#0f172a", pady=15)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(footer_frame, text="CarePoint OS v2.0", font=("Arial", 8), bg="#0f172a", fg="#64748b").pack(anchor="w", padx=15)

    def create_topbar(self):
        self.topbar = tk.Frame(self.root, bg="white", height=50, bd=1, relief=tk.SOLID)
        self.topbar.pack(side=tk.TOP, fill=tk.X)
        self.topbar.pack_propagate(False)

        self.lbl_title = tk.Label(self.topbar, text="Executive Clinical Operations Dashboard", font=("Arial", 11, "bold"), bg="white", fg="#1e293b")
        self.lbl_title.pack(side=tk.LEFT, padx=20)

        date_str = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(self.topbar, text=date_str, font=("Arial", 9), bg="white", fg="#64748b").pack(side=tk.RIGHT, padx=10)
        
        status_lbl = tk.Label(self.topbar, text=" System Online ", font=("Arial", 9, "bold"), bg="#dcfce7", fg="#166534", padx=8, pady=2)
        status_lbl.pack(side=tk.RIGHT, padx=10)

    def create_main_content_area(self):
        self.content_area = tk.Frame(self.root, bg="#f4f6f9")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def clear_content(self):
        for widget in self.content_area.winfo_children(): widget.destroy()

    def highlight_nav(self, active_name):
        for name, btn in self.nav_buttons.items():
            if name == active_name: btn.config(bg="#2563eb", fg="white")
            else: btn.config(bg="#0f172a", fg="#cbd5e1")

    # ================= VIEW 1: DASHBOARD =================
    def show_dashboard(self):
        self.highlight_nav("Dashboard")
        self.clear_content()
        self.lbl_title.config(text="Executive Clinical Operations Dashboard")

        dash_frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        dash_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(dash_frame, text="Hospital Operations Dashboard", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(dash_frame, text="Real-time clinical metrics, patient queues, and department workloads", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 15))

        cards_frame = tk.Frame(dash_frame, bg="#f4f6f9")
        cards_frame.pack(fill=tk.X, pady=5)

        total_patients = len(self.patient_avl.inorder())
        metrics = [
            ("TOTAL PATIENTS", str(total_patients), "Managed via AVL Tree", "#2563eb"),
            ("ACTIVE DOCTORS", str(len([d for d in self.doctors_list if d['status'] == 'Active'])), "Across Departments", "#16a34a"),
            ("APPOINTMENTS", str(len(self.appointments_list)), "Scheduled Consultations", "#9333ea"),
            ("EMERGENCY QUEUE", str(len(self.triage_heap.heap)), "Critical Triage Heap", "#dc2626")
        ]

        for title, val, sub, color in metrics:
            card = tk.Frame(cards_frame, bg="white", bd=1, relief=tk.SOLID, padx=12, pady=10)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
            indicator = tk.Frame(card, bg=color, width=4)
            indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            info = tk.Frame(card, bg="white")
            info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(info, text=title, font=("Arial", 8, "bold"), bg="white", fg="#64748b").pack(anchor="w")
            tk.Label(info, text=val, font=("Arial", 16, "bold"), bg="white", fg="#0f172a").pack(anchor="w", pady=2)
            tk.Label(info, text=sub, font=("Arial", 8), bg="white", fg="#94a3b8").pack(anchor="w")

        table_frame = tk.Frame(dash_frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        tk.Label(table_frame, text="Recent Appointments Schedule", font=("Arial", 11, "bold"), bg="white", fg="#0f172a").pack(anchor="w", padx=5, pady=5)

        tree = ttk.Treeview(table_frame, columns=("APT", "Patient", "Dept", "Doctor", "Schedule", "Status"), show="headings", height=6)
        tree.heading("APT", text="APT ID")
        tree.heading("Patient", text="Patient Name")
        tree.heading("Dept", text="Department")
        tree.heading("Doctor", text="Consultant")
        tree.heading("Schedule", text="Schedule")
        tree.heading("Status", text="Status")
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for apt in self.appointments_list:
            tree.insert("", tk.END, values=(apt["apt_id"], apt["patient"], apt["dept"], apt["doctor"], apt["schedule"], apt["status"]))

    # ================= VIEW 2: PATIENTS =================
    def show_patients(self):
        self.highlight_nav("Patients")
        self.clear_content()
        self.lbl_title.config(text="Patient Management & Master Index")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Patient Administration & Records", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Search, register, and review patient clinical profiles indexed via AVL Tree", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        control_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=10)
        control_frame.pack(fill=tk.X, pady=5)

        tk.Label(control_frame, text="Search Patient ID:", font=("Arial", 9, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(control_frame, font=("Arial", 10), width=15)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Search", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), command=self.search_patient_action).pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Register Patient", bg="#16a34a", fg="white", font=("Arial", 9, "bold"), command=self.open_register_modal).pack(side=tk.RIGHT, padx=5)

        table_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.patient_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Age", "Contact", "Blood", "Allergies"), show="headings", selectmode="browse")
        self.patient_tree.heading("ID", text="Patient ID")
        self.patient_tree.heading("Name", text="Full Name")
        self.patient_tree.heading("Age", text="Age / Gender")
        self.patient_tree.heading("Contact", text="Contact No.")
        self.patient_tree.heading("Blood", text="Blood")
        self.patient_tree.heading("Allergies", text="Allergies")
        self.patient_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_patient_table()

        btn_frame = tk.Frame(frame, bg="#f4f6f9")
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="View Full Profile", bg="#475569", fg="white", font=("Arial", 9, "bold"), command=self.view_patient_profile).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Record", bg="#dc2626", fg="white", font=("Arial", 9, "bold"), command=self.remove_patient_record).pack(side=tk.RIGHT, padx=5)

    def refresh_patient_table(self):
        for row in self.patient_tree.get_children(): self.patient_tree.delete(row)
        for p in self.patient_avl.inorder():
            self.patient_tree.insert("", tk.END, values=(p["id"], p["name"], f"{p['age']}y / {p['gender']}", p["contact"], p["blood"], p["allergies"]))

    def search_patient_action(self):
        pid = self.search_entry.get().strip()
        node = self.patient_avl.search(pid)
        if node:
            messagebox.showinfo("Patient Found", f"ID: {node['id']}\nName: {node['name']}\nAge: {node['age']}\nBlood: {node['blood']}")
            self.audit_stack.push(f"Searched patient: {pid}")
        else: messagebox.showwarning("Not Found", f"Patient ID '{pid}' not found.")

    def view_patient_profile(self):
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient.")
            return
        pid = self.patient_tree.item(selected[0])["values"][0]
        node = self.patient_avl.search(pid)
        if node:
            messagebox.showinfo(f"Profile: {node['name']}", f"ID: {node['id']}\nName: {node['name']}\nAge: {node['age']}/{node['gender']}\nContact: {node['contact']}\nBlood: {node['blood']}\nAllergies: {node['allergies']}")

    def remove_patient_record(self):
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient to remove.")
            return
        pid = self.patient_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Remove patient {pid}?"):
            self.patient_avl.delete(pid)
            self.audit_stack.push(f"Removed patient {pid}")
            self.refresh_patient_table()

    def open_register_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Register Patient")
        modal.geometry("400x420")

        tk.Label(modal, text="Patient Registration Form", font=("Arial", 12, "bold"), fg="#2563eb").pack(pady=10)
        fields = [("Patient ID:", "id"), ("Full Name:", "name"), ("Age:", "age"), ("Gender:", "gender"), 
                  ("Contact:", "contact"), ("Blood Group:", "blood"), ("Allergies:", "allergies")]
        entries = {}
        for label_text, key in fields:
            f = tk.Frame(modal, padx=10, pady=3)
            f.pack(fill=tk.X)
            tk.Label(f, text=label_text, width=15, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(f, width=25)
            e.pack(side=tk.RIGHT)
            entries[key] = e

        def save_new():
            try:
                p = {
                    "id": entries["id"].get().strip(), "name": entries["name"].get().strip(),
                    "age": int(entries["age"].get().strip()), "gender": entries["gender"].get().strip(),
                    "contact": entries["contact"].get().strip(), "blood": entries["blood"].get().strip(),
                    "allergies": entries["allergies"].get().strip()
                }
                if self.patient_avl.insert(p):
                    self.audit_stack.push(f"Registered patient {p['id']} ({p['name']})")
                    messagebox.showinfo("Success", "Patient registered & indexed via AVL Tree!")
                    self.refresh_patient_table()
                    modal.destroy()
                else: messagebox.showerror("Error", "Patient ID already exists!")
            except ValueError: messagebox.showerror("Error", "Check age format.")

        tk.Button(modal, text="Save & Index", bg="#16a34a", fg="white", font=("Arial", 10, "bold"), command=save_new).pack(pady=15)

    # ================= VIEW 3: DOCTORS =================
    def show_doctors(self):
        self.highlight_nav("Doctors")
        self.clear_content()
        self.lbl_title.config(text="Medical Staff & Consultant Roster Management")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Consultant & Medical Staff Roster", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Manage doctor profiles, departmental affiliations, and active statuses", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        control_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=10)
        control_frame.pack(fill=tk.X, pady=5)
        tk.Button(control_frame, text="+ Add New Consultant", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), command=self.open_add_doctor_modal).pack(side=tk.RIGHT, padx=5)

        table_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.doctor_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Dept", "Specialization", "Fee", "Hours", "Status"), show="headings", selectmode="browse")
        self.doctor_tree.heading("ID", text="Doctor ID")
        self.doctor_tree.heading("Name", text="Physician Name")
        self.doctor_tree.heading("Dept", text="Department")
        self.doctor_tree.heading("Specialization", text="Specialization")
        self.doctor_tree.heading("Fee", text="Fee (₹)")
        self.doctor_tree.heading("Hours", text="Clinic Hours")
        self.doctor_tree.heading("Status", text="Status")
        self.doctor_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_doctor_table()

        btn_frame = tk.Frame(frame, bg="#f4f6f9")
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Toggle Active/Inactive", bg="#475569", fg="white", font=("Arial", 9, "bold"), command=self.toggle_doctor_status).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Doctor", bg="#dc2626", fg="white", font=("Arial", 9, "bold"), command=self.remove_doctor).pack(side=tk.RIGHT, padx=5)

    def refresh_doctor_table(self):
        for row in self.doctor_tree.get_children(): self.doctor_tree.delete(row)
        for d in self.doctors_list:
            self.doctor_tree.insert("", tk.END, values=(d["id"], d["name"], d["dept"], d["spec"], f"₹{d['fee']}", d["hours"], d["status"]))

    def open_add_doctor_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Add New Consultant")
        modal.geometry("400x380")

        tk.Label(modal, text="New Consultant Registration", font=("Arial", 12, "bold"), fg="#2563eb").pack(pady=10)
        fields = [("Doctor ID:", "id"), ("Name:", "name"), ("Department:", "dept"), 
                  ("Specialization:", "spec"), ("Fee (₹):", "fee"), ("Clinic Hours:", "hours")]
        entries = {}
        for label_text, key in fields:
            f = tk.Frame(modal, padx=10, pady=3)
            f.pack(fill=tk.X)
            tk.Label(f, text=label_text, width=15, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(f, width=25)
            e.pack(side=tk.RIGHT)
            entries[key] = e

        def save_doc():
            try:
                d = {
                    "id": entries["id"].get().strip(), "name": entries["name"].get().strip(),
                    "dept": entries["dept"].get().strip(), "spec": entries["spec"].get().strip(),
                    "fee": float(entries["fee"].get().strip()), "hours": entries["hours"].get().strip(),
                    "status": "Active"
                }
                self.doctors_list.append(d)
                self.audit_stack.push(f"Added consultant: {d['id']} ({d['name']})")
                messagebox.showinfo("Success", "Consultant added successfully!")
                self.refresh_doctor_table()
                modal.destroy()
            except ValueError: messagebox.showerror("Error", "Check fee numerical format.")

        tk.Button(modal, text="Save Consultant", bg="#16a34a", fg="white", font=("Arial", 10, "bold"), command=save_doc).pack(pady=15)

    def toggle_doctor_status(self):
        selected = self.doctor_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Select a doctor first.")
            return
        doc_id = self.doctor_tree.item(selected[0])["values"][0]
        for d in self.doctors_list:
            if d["id"] == doc_id:
                d["status"] = "Inactive" if d["status"] == "Active" else "Active"
                self.audit_stack.push(f"Toggled status of doctor {doc_id} to {d['status']}")
                messagebox.showinfo("Updated", f"Doctor status changed to {d['status']}.")
                self.refresh_doctor_table()
                break

    def remove_doctor(self):
        selected = self.doctor_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Select a doctor to remove.")
            return
        doc_id = self.doctor_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Remove doctor {doc_id}?"):
            self.doctors_list = [d for d in self.doctors_list if d["id"] != doc_id]
            self.audit_stack.push(f"Removed doctor {doc_id}")
            self.refresh_doctor_table()

    # ================= VIEW 4: APPOINTMENTS =================
    def show_appointments(self):
        self.highlight_nav("Appointments")
        self.clear_content()
        self.lbl_title.config(text="Patient Appointment Scheduling")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Appointment Booking System", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Book consultations by selecting patient, department, and doctor", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        form_frame.pack(fill=tk.X, pady=5)

        tk.Label(form_frame, text="Select Patient:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        patient_names = [p["name"] for p in self.patient_avl.inorder()]
        self.apt_patient_combo = ttk.Combobox(form_frame, values=patient_names, state="readonly", width=22)
        self.apt_patient_combo.grid(row=0, column=1, padx=5, pady=5)
        if patient_names: self.apt_patient_combo.current(0)

        tk.Label(form_frame, text="Department:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        departments = list(set([d["dept"] for d in self.doctors_list]))
        self.apt_dept_combo = ttk.Combobox(form_frame, values=departments, state="readonly", width=20)
        self.apt_dept_combo.grid(row=0, column=3, padx=5, pady=5)
        if departments: self.apt_dept_combo.current(0)

        tk.Label(form_frame, text="Consultant Doctor:", font=("Arial", 9, "bold"), bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        doctor_names = [d["name"] for d in self.doctors_list]
        self.apt_doc_combo = ttk.Combobox(form_frame, values=doctor_names, state="readonly", width=22)
        self.apt_doc_combo.grid(row=1, column=1, padx=5, pady=5)
        if doctor_names: self.apt_doc_combo.current(0)

        tk.Button(form_frame, text="+ Book Appointment", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), command=self.book_appointment_action).grid(row=1, column=3, padx=5, pady=5)

        table_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.apt_tree = ttk.Treeview(table_frame, columns=("APT", "Patient", "Dept", "Doctor", "Schedule", "Status"), show="headings")
        self.apt_tree.heading("APT", text="APT ID")
        self.apt_tree.heading("Patient", text="Patient Name")
        self.apt_tree.heading("Dept", text="Department")
        self.apt_tree.heading("Doctor", text="Consultant Doctor")
        self.apt_tree.heading("Schedule", text="Timestamp")
        self.apt_tree.heading("Status", text="Status")
        self.apt_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_appointments_table()

    def refresh_appointments_table(self):
        for row in self.apt_tree.get_children(): self.apt_tree.delete(row)
        for apt in self.appointments_list:
            self.apt_tree.insert("", tk.END, values=(apt["apt_id"], apt["patient"], apt["dept"], apt["doctor"], apt["schedule"], apt["status"]))

    def book_appointment_action(self):
        patient = self.apt_patient_combo.get()
        dept = self.apt_dept_combo.get()
        doctor = self.apt_doc_combo.get()

        if not patient or not doctor:
            messagebox.showerror("Error", "Select patient and doctor.")
            return

        apt_id = f"APT-{5000 + len(self.appointments_list) + 1}"
        schedule = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_apt = {"apt_id": apt_id, "patient": patient, "dept": dept, "doctor": doctor, "schedule": schedule, "status": "Scheduled"}
        
        self.appointments_list.append(new_apt)
        self.audit_stack.push(f"Booked appointment {apt_id} for {patient} with {doctor}")
        messagebox.showinfo("Success", f"Appointment {apt_id} booked successfully!")
        self.refresh_appointments_table()

    # ================= VIEW 5: BILLING & PAYMENTS =================
    def show_billing(self):
        self.highlight_nav("Billing & Payments")
        self.clear_content()
        self.lbl_title.config(text="Hospital Billing & Invoice Generation")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Billing & Invoice Calculator", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Calculate consultation, lab tests, and medicine charges with full-screen receipt view", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        top_split = tk.Frame(frame, bg="#f4f6f9")
        top_split.pack(fill=tk.BOTH, expand=True, pady=5)

        calc_frame = tk.Frame(top_split, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(calc_frame, text="Select Patient:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=8)
        patient_names = [p["name"] for p in self.patient_avl.inorder()]
        self.bill_patient_combo = ttk.Combobox(calc_frame, values=patient_names, state="readonly", width=22)
        self.bill_patient_combo.grid(row=0, column=1, pady=8)
        if patient_names: self.bill_patient_combo.current(0)

        tk.Label(calc_frame, text="Consultation Fee (₹):", font=("Arial", 9, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=8)
        self.e_consult_fee = tk.Entry(calc_frame, width=24)
        self.e_consult_fee.insert(0, "600")
        self.e_consult_fee.grid(row=1, column=1, pady=8)

        tk.Label(calc_frame, text="Lab Test Charges (₹):", font=("Arial", 9, "bold"), bg="white").grid(row=2, column=0, sticky="w", pady=8)
        self.e_lab_fee = tk.Entry(calc_frame, width=24)
        self.e_lab_fee.insert(0, "1200")
        self.e_lab_fee.grid(row=2, column=1, pady=8)

        tk.Label(calc_frame, text="Medicine Charges (₹):", font=("Arial", 9, "bold"), bg="white").grid(row=3, column=0, sticky="w", pady=8)
        self.e_med_fee = tk.Entry(calc_frame, width=24)
        self.e_med_fee.insert(0, "450")
        self.e_med_fee.grid(row=3, column=1, pady=8)

        tk.Button(calc_frame, text="Calculate & Generate Invoice", bg="#16a34a", fg="white", font=("Arial", 10, "bold"), command=self.generate_invoice).grid(row=4, column=0, columnspan=2, pady=20)

        inv_frame = tk.Frame(top_split, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        inv_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(inv_frame, text="Generated Official Itemized Invoice", font=("Arial", 11, "bold"), bg="white", fg="#0f172a").pack(anchor="w", pady=(0, 5))
        
        self.invoice_text = tk.Text(inv_frame, height=18, width=50, font=("Courier", 10), bg="#f8fafc", bd=0)
        self.invoice_text.pack(fill=tk.BOTH, expand=True)
        self.invoice_text.insert(tk.END, "\n\n      [ Click 'Calculate & Generate Invoice' ]\n      to view the complete receipt here.")
        self.invoice_text.config(state=tk.DISABLED)

    def generate_invoice(self):
        try:
            patient = self.bill_patient_combo.get()
            consult = float(self.e_consult_fee.get())
            lab = float(self.e_lab_fee.get())
            med = float(self.e_med_fee.get())
            total = consult + lab + med

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            invoice_content = f"""==================================================
              CAREPOINT HOSPITAL SYSTEM          
            OFFICIAL ITEMIZED INVOICE            
==================================================
Timestamp   : {timestamp}
Patient Name: {patient}
--------------------------------------------------
1. Doctor Consultation Fee    : ₹{consult:10.2f}
2. Diagnostic Lab Tests       : ₹{lab:10.2f}
3. Pharmacy & Medicines       : ₹{med:10.2f}
--------------------------------------------------
TOTAL PAYABLE AMOUNT          : ₹{total:10.2f}
==================================================
Status: VERIFIED & PAID
Thank you for trusting CarePoint Health!
"""
            self.invoice_text.config(state=tk.NORMAL)
            self.invoice_text.delete("1.0", tk.END)
            self.invoice_text.insert(tk.END, invoice_content)
            self.invoice_text.config(state=tk.DISABLED)

            self.audit_stack.push(f"Generated invoice for {patient} totaling ₹{total:.2f}")
            messagebox.showinfo("Success", f"Invoice generated successfully! Total: ₹{total:.2f}")
        except ValueError: messagebox.showerror("Error", "Enter valid numbers for fees.")

    # ================= VIEW 6: EMERGENCY & TRIAGE (DROPDOWN MENU) =================
    def show_triage(self):
        self.highlight_nav("Emergency & Triage")
        self.clear_content()
        self.lbl_title.config(text="Emergency Department Triage (Min-Heap Priority Queue)")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="ER Triage & Priority Queue", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Automatic patient prioritization managed via Custom Min-Heap data structure", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=15, pady=15)
        form_frame.pack(fill=tk.X, pady=5)

        tk.Label(form_frame, text="Patient Name:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w", padx=5)
        
        # Patient Name Dropdown populated from AVL Tree records
        patient_names = [p["name"] for p in self.patient_avl.inorder()]
        self.triage_name_combo = ttk.Combobox(form_frame, values=patient_names, state="readonly", width=22)
        self.triage_name_combo.grid(row=0, column=1, padx=5)
        if patient_names: self.triage_name_combo.current(0)

        tk.Label(form_frame, text="Severity Level:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=2, sticky="w", padx=5)
        self.triage_sev_combo = ttk.Combobox(form_frame, values=["1 - Resuscitation (Critical)", "2 - Urgent Trauma", "3 - Stable Condition"], state="readonly", width=25)
        self.triage_sev_combo.grid(row=0, column=3, padx=5)
        self.triage_sev_combo.current(0)

        tk.Button(form_frame, text="Admit to ER Heap", bg="#dc2626", fg="white", font=("Arial", 9, "bold"), command=self.add_triage_patient).grid(row=0, column=4, padx=10)
        tk.Button(form_frame, text="Treat Next (Extract Min)", bg="#f59e0b", fg="white", font=("Arial", 9, "bold"), command=self.treat_triage_patient).grid(row=0, column=5, padx=5)

        table_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.triage_tree = ttk.Treeview(table_frame, columns=("Priority", "Name", "Condition"), show="headings")
        self.triage_tree.heading("Priority", text="Min-Heap Priority Level")
        self.triage_tree.heading("Name", text="Patient Name")
        self.triage_tree.heading("Condition", text="Clinical Severity Description")
        self.triage_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_triage_table()

    def refresh_triage_table(self):
        for row in self.triage_tree.get_children(): self.triage_tree.delete(row)
        for item in self.triage_heap.view_all():
            self.triage_tree.insert("", tk.END, values=(f"Level {item[0]}", item[2], item[3]))

    def add_triage_patient(self):
        name = self.triage_name_combo.get().strip()
        sev_text = self.triage_sev_combo.get()
        if not name:
            messagebox.showerror("Error", "Select patient name from dropdown.")
            return
        priority = int(sev_text[0])
        self.triage_heap.insert(priority, name, sev_text)
        self.audit_stack.push(f"Admitted ER Min-Heap patient: {name}")
        messagebox.showinfo("Success", f"{name} inserted into Min-Heap queue!")
        self.refresh_triage_table()

    def treat_triage_patient(self):
        next_p = self.triage_heap.extract_min()
        if not next_p:
            messagebox.showinfo("Empty", "Emergency queue is clear!")
            return
        _, _, name, cond = next_p
        self.audit_stack.push(f"Treated ER Min-Heap patient: {name}")
        messagebox.showinfo("Attending Patient", f"Now treating highest priority patient:\nName: {name}\nCondition: {cond}")
        self.refresh_triage_table()

    # ================= VIEW 7: CAMPUS NAVIGATION =================
    def show_navigation(self):
        self.highlight_nav("Campus Navigation")
        self.clear_content()
        self.lbl_title.config(text="Hospital Campus Routing (Dijkstra, Floyd-Warshall & Prim's MST)")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Advanced Hospital Navigation & Infrastructure Network", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Compute point-to-point routes (Dijkstra), all-pairs matrix (Floyd-Warshall), and MST wiring (Prim's)", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        nav_notebook = ttk.Notebook(frame)
        nav_notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        tab_dij = ttk.Frame(nav_notebook)
        nav_notebook.add(tab_dij, text="1. Shortest Path (Dijkstra)")

        f_dij = tk.Frame(tab_dij, bg="white", padx=15, pady=15)
        f_dij.pack(fill=tk.BOTH, expand=True)

        locations = self.hospital_graph.departments
        tk.Label(f_dij, text="Start:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky="w")
        self.nav_start = ttk.Combobox(f_dij, values=locations, state="readonly", width=18)
        self.nav_start.grid(row=0, column=1, padx=5)
        self.nav_start.current(0)

        tk.Label(f_dij, text="Destination:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky="w")
        self.nav_end = ttk.Combobox(f_dij, values=locations, state="readonly", width=18)
        self.nav_end.grid(row=0, column=3, padx=5)
        self.nav_end.current(2)

        tk.Button(f_dij, text="Find Route", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), command=self.calc_dijkstra).grid(row=0, column=4, padx=15)
        
        self.lbl_dij_out = tk.Label(f_dij, text="Select start and destination above.", font=("Arial", 11), bg="white", justify=tk.LEFT)
        self.lbl_dij_out.grid(row=1, column=0, columnspan=5, sticky="w", pady=20)

        tab_fw = ttk.Frame(nav_notebook)
        nav_notebook.add(tab_fw, text="2. All-Pairs Matrix (Floyd-Warshall)")
        
        f_fw = tk.Frame(tab_fw, bg="white", padx=10, pady=10)
        f_fw.pack(fill=tk.BOTH, expand=True)
        tk.Button(f_fw, text="Compute All-Pairs Matrix", bg="#16a34a", fg="white", font=("Arial", 9, "bold"), command=self.calc_floyd_warshall).pack(anchor="w", pady=5)
        
        self.fw_text = tk.Text(f_fw, height=12, font=("Courier", 9), bg="#f8fafc")
        self.fw_text.pack(fill=tk.BOTH, expand=True, pady=5)

        tab_prim = ttk.Frame(nav_notebook)
        nav_notebook.add(tab_prim, text="3. Infrastructure Network (Prim's MST)")

        f_prim = tk.Frame(tab_prim, bg="white", padx=10, pady=10)
        f_prim.pack(fill=tk.BOTH, expand=True)
        tk.Button(f_prim, text="Calculate Optimal Pipeline/Wiring MST", bg="#9333ea", fg="white", font=("Arial", 9, "bold"), command=self.calc_prim).pack(anchor="w", pady=5)

        self.prim_text = tk.Text(f_prim, height=12, font=("Courier", 9), bg="#f8fafc")
        self.prim_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def calc_dijkstra(self):
        start = self.nav_start.get()
        end = self.nav_end.get()
        if start == end:
            messagebox.showwarning("Warning", "Locations must be different.")
            return
        cost, path = self.hospital_graph.dijkstra(start, end)
        path_str = " ➔ ".join(path)
        self.audit_stack.push(f"Computed Dijkstra route from {start} to {end} (Cost: {cost})")
        self.lbl_dij_out.config(text=f"📍 Shortest Path Route:\n{path_str}\n\n⏱️ Total Transit Distance Cost: {cost} meters")

    def calc_floyd_warshall(self):
        res = self.hospital_graph.floyd_warshall()
        nodes = self.hospital_graph.departments
        out = "DEPT            " + "".join([f"{n[:6]:>8}" for n in nodes]) + "\n" + "-"*80 + "\n"
        for i in nodes:
            out += f"{i[:14]:<14} |" + "".join([f"{res[i][j]:8}" for j in nodes]) + "\n"
        self.fw_text.delete("1.0", tk.END)
        self.fw_text.insert(tk.END, out)
        self.audit_stack.push("Computed Floyd-Warshall all-pairs distance matrix.")

    def calc_prim(self):
        mst = self.hospital_graph.prim_mst()
        total_cost = sum([wt for _, _, wt in mst])
        out = "=== PRIM'S MINIMUM SPANNING TREE (MST) ===\nOptimal cabling/piping layout connecting all wards:\n\n"
        for u, v, wt in mst:
            out += f"• {u} <---> {v}  [Cost: {wt} meters]\n"
        out += f"\nTotal Minimum Infrastructure Cost: {total_cost} meters"
        self.prim_text.delete("1.0", tk.END)
        self.prim_text.insert(tk.END, out)
        self.audit_stack.push("Computed Prim's Minimum Spanning Tree for hospital wiring.")

    # ================= VIEW 8: ACTION AUDIT STACK =================
    def show_audit(self):
        self.highlight_nav("System Audit")
        self.clear_content()
        self.lbl_title.config(text="System Activity Audit & History Log (Stack)")

        frame = tk.Frame(self.content_area, bg="#f4f6f9", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="System Audit Log (LIFO Stack)", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#0f172a").pack(anchor="w")
        tk.Label(frame, text="Real-time chronological stack history of clinical administrative actions", font=("Arial", 9), bg="#f4f6f9", fg="#64748b").pack(anchor="w", pady=(0, 10))

        list_frame = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.audit_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.audit_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.audit_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.audit_listbox.config(yscrollcommand=scrollbar.set)

        for action in self.audit_stack.get_all():
            self.audit_listbox.insert(tk.END, f"• {action}")

        btn_frame = tk.Frame(frame, bg="#f4f6f9")
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Refresh Audit Log", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), command=self.show_audit).pack(side=tk.LEFT)


if __name__ == "__main__":
    root = tk.Tk()
    app = CarePointApp(root)
    root.mainloop()