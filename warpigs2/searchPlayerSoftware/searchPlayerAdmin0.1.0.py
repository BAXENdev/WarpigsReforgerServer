

# @Author BAXENATOR
# @License http://baxendev.com/warpigs-license-v1.0.html

import tkinter as tk
from tkinter import ttk, messagebox, font
import pyperclip  # For clipboard functionality
import psycopg2
from bercon import BERconClient, BERconResponse
import asyncio
import requests
from datetime import datetime
import json
import os
from pathlib import Path
import time

class AdminSearchApp:
	def __init__(self, root: tk.Tk):
		self.db_config = {
			"dbname": "armaReforger",
			"user": "",
			"password": "",
			"host": "148.113.163.200",
			"port": "35432"
		}
		self.settings_folder: Path = Path.home() / "AppData" / "Local" / "WarpigsSearchPlayer"
		self.settings_file: Path = self.settings_folder / "admin_settings.json"
		self.isLoggedIn = False
		# id, name, username
		self.admins: list[tuple[int, str, str]] = []
		self.adminActions: list[AdminAction] = []

		self.root = root
		self.root.title("Player Search")
		self.root.geometry("1500x630")  # Increased height for the new section
		self.root.minsize(1500, 630)
		self.root.maxsize(1500, 630)

		main_frame = tk.Frame(root)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		left_frame = tk.Frame(main_frame, width=400)
		left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		frame_createAdmin = tk.LabelFrame(left_frame, text="Create Admin", font=("Helvetica", 14, "bold"), padx=5, pady=5)
		frame_createAdmin.pack(padx=5, pady=5, fill=tk.BOTH)
		ttk.Label(frame_createAdmin, text="Name:").grid(row=0, column=0, sticky="e", pady=5, padx=2)
		self.adminName_var = tk.StringVar()
		entry_name = ttk.Entry(frame_createAdmin, textvariable=self.adminName_var)
		entry_name.grid(row=0, column=1, pady=5)
		ttk.Label(frame_createAdmin, text="Username:").grid(row=1, column=0, sticky="e", pady=5, padx=2)
		self.username_var = tk.StringVar()
		entry_name = ttk.Entry(frame_createAdmin, textvariable=self.username_var)
		entry_name.grid(row=1, column=1, pady=5)
		ttk.Label(frame_createAdmin, text="Password:").grid(row=2, column=0, sticky="e", pady=5, padx=2)
		self.password_var = tk.StringVar()
		entry_name = ttk.Entry(frame_createAdmin, textvariable=self.password_var)
		entry_name.grid(row=2, column=1, pady=5)
		button_createAdmin = ttk.Button(frame_createAdmin, text="Create Admin", command=self.createAdmin)
		button_createAdmin.grid(row=3, column=0, columnspan=2, sticky="ew")
		
		tree_title = tk.LabelFrame(left_frame, text="Admin Users", font=("Helvetica", 14, "bold"),  padx=5, pady=5)
		tree_title.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
		self.tree_admins = ttk.Treeview(tree_title, columns=("Name", "Username"), show="headings")
		self.tree_admins.heading("Name", text="Name")
		self.tree_admins.heading("Username", text="Username")
		self.tree_admins.bind("<<TreeviewSelect>>", self.selectAdmin)
		self.tree_admins.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

		button_disableAdmin = ttk.Button(tree_title, text="Disable Admin", command=self.disableAdmin)
		button_disableAdmin.pack(fill=tk.X, padx=5)

		right_frame = tk.Frame(main_frame, width=1100)
		right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

		tree_title = tk.LabelFrame(right_frame, text="Admin Actions", font=("Helvetica", 14, "bold"),  padx=5, pady=5)
		tree_title.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
		
		# t1."name" as "adminName", t1."actionTime", t1."actionType", t1."adminId", t1."reason", t2."name" as "playerName"
		self.tree_adminActions = ttk.Treeview(tree_title, columns=("Admin Name", "Admin Action", "Player Name", "Reason", "Action Time"), show="headings")
		self.tree_adminActions.heading("Admin Name", text="Admin Name")
		self.tree_adminActions.heading("Admin Action", text="Admin Action")
		self.tree_adminActions.heading("Player Name", text="Player Name")
		self.tree_adminActions.heading("Reason", text="Reason")
		self.tree_adminActions.heading("Action Time", text="Action Time")
		self.tree_adminActions.column("Admin Name", stretch=True, width=180, anchor=tk.W)
		self.tree_adminActions.column("Admin Action", stretch=True, width=180, anchor=tk.W)
		self.tree_adminActions.column("Player Name", stretch=True, width=140, anchor=tk.W)
		self.tree_adminActions.column("Reason", stretch=True, width=340, anchor=tk.W)
		self.tree_adminActions.column("Action Time", stretch=True, width=160, anchor=tk.W)
		self.tree_adminActions.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

		frame_filter = tk.Frame(tree_title)
		frame_filter.pack(fill=tk.X, pady=5)
		tk.Label(frame_filter, text="Filter for Selected Admin: ").pack(side=tk.LEFT)
		self.filterToggle_var = tk.BooleanVar()
		checkbutton_filter = tk.Checkbutton(frame_filter, variable=self.filterToggle_var, command=self.applyActionFilter)
		checkbutton_filter.pack(side=tk.LEFT)

		self.login_win: tk.Toplevel = None
		self.login()

	def login(self):
		if not os.path.exists(self.settings_folder):
			os.makedirs(self.settings_folder)

		if not os.path.exists(self.settings_file):
			self.openLoginMenu()
			return
		
		with open(self.settings_file, "r") as f:
			try:
				settings: dict[str, str] = json.load(f)
			except Exception as e:
				self.openLoginMenu()
				return
		
		if not "user" in settings or not "password" in settings:
			self.openLoginMenu()
			return
		
		if not self.testLogin(**settings):
			self.openLoginMenu()
			return
		
		self.db_config.update(settings)
		self.postLogin()

	def postLogin(self):
		self.isLoggedIn = True
		self.updateAdminsList()
		self.updateAdminActions()

	def openLoginMenu(self):
		if self.login_win and self.login_win.winfo_exists():
			self.login_win.lift()
			return
		
		window_width = 300
		window_height = 200
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		x = int((screen_width / 2) - (window_width / 2))
		y = int((screen_height / 2) - (window_height / 2))

		login_win = tk.Toplevel(self.root)
		# login_win.overrideredirect(True)
		login_win.title("Login")
		login_win.geometry(f"300x200+{x}+{y}")
		login_win.protocol("WM_DELETE_WINDOW", lambda : self.root.destroy())
		login_win.attributes('-topmost', True)
		login_win.after(100, lambda: self.login_win.attributes('-topmost', False))
		login_win.resizable(False, False)
		self.login_win: tk.Toplevel = login_win

		ttk.Label(login_win, text="LOGIN", font=("Segoe UI", 16, "bold")).pack(pady=(10, 0), anchor="w", padx=10)
		ttk.Label(login_win, text="Username:").pack(pady=(10, 0), anchor="w", padx=10)
		self.username_entry = ttk.Entry(login_win)
		self.username_entry.pack(fill='x', padx=10)
		ttk.Label(login_win, text="Password:").pack(pady=(10, 0), anchor="w", padx=10)
		self.password_entry = ttk.Entry(login_win, show="*")
		self.password_entry.pack(fill='x', padx=10)

		def attemptLogin():
			user = self.username_entry.get()
			password = self.password_entry.get()
			if self.testLogin(user, password):
				settings = {"user": user, "password": password}
				with open(self.settings_file, "w") as f:
					json.dump(settings, f)
				self.login_win.destroy()
				self.login()
			else:
				messagebox.showerror("Invalid Login", "Invalid username and/or password. Try Again")
				self.password_entry.delete(0, tk.END)
				self.login_win.lift()

		ttk.Button(login_win, text="Login", command=attemptLogin).pack(pady=15)
		self.login_win.lift()

	def testLogin(self, user: str, password: str) -> bool:
		db_config_copy = self.db_config.copy()
		db_config_copy["user"] = user
		db_config_copy["password"] = password
		
		try:
			with psycopg2.connect(**db_config_copy) as conn:
				# with conn.cursor() as cursor:
				#     cursor.execute('SELECT rolcreaterole FROM pg_roles WHERE rolname = current_user')
					pass # Connect and do nothing. No need for verification
		except Exception as e:
			return False

		return True
	
	def show_license_popup(self):
		license_text = """Warpigs Software License v1.0

Summary
This summary is for informational purposes only and is not legally binding.
This license grants limited rights for the use, modification, and distribution of the software to the online group known as Warpigs, accessible via https://discord.gg/bqEd4rfS5m.

In essence, this license:
- Restricts usage and distribution to hardware owned or rented by Warpigs members.
- Prohibits any commercial use.
- Allows derivative works, but only within the same group under the same license.
- Offers no warranty or support.
- Is not transferable to any other person or entity.

I. Grant of Use
Permission is granted to the group known as Warpigs, including its current members, to use, modify, and distribute the software under the following conditions:
1. Distribution is limited to hardware (owned, rented, or otherwise controlled) by members of Warpigs.
2. The software may not be shared, licensed, or distributed outside of the Warpigs group.

II. Prohibited Uses
The software, whether original or modified, may not be used for any form of monetary gain, including but not limited to:
1. Selling or reselling the software.
2. Offering services that rely on or are powered by the software.
3. Monetizing access, usage, or functionality of the software in any form.

III. Derivative Works
Derivative works are allowed and encouraged under the following terms:
1. All derivative works must be distributed solely within the Warpigs group.
2. All such works remain subject to this exact license.
3. No derivative may be re-licensed under different terms.

IV. Warranty Disclaimer
The software is provided "as is," without warranty of any kind, express or implied.
There is no guarantee of:
1. Functionality or fitness for any purpose.
2. Continued support, updates, or maintenance.

V. Non-Transferability
This license is granted exclusively to the Warpigs group and is not transferable to any other group, individual, organization, or entity.

VI. Versioning
This is Warpigs Software License v1.0. Future versions, if released, will be versioned independently.
Existing software remains bound by the version in effect at the time of its distribution.

© 2025 by Reclaim Development LLC. All rights reserved."""

		popup = tk.Toplevel(self.root)
		popup.title("License")
		popup.geometry("600x500")
		
		text_frame = ttk.Frame(popup)
		text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		scrollbar = ttk.Scrollbar(text_frame)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
		text_widget.insert(tk.END, license_text)
		text_widget.config(state=tk.DISABLED)  # Make it read-only
		text_widget.pack(fill=tk.BOTH, expand=True)

		scrollbar.config(command=text_widget.yview)

		close_button = ttk.Button(popup, text="Close", command=popup.destroy)
		close_button.pack(pady=5)
		# messagebox.showinfo("License", license_text)

	def updateAdminsList(self):
		try:
			with psycopg2.connect(**self.db_config) as conn:
				with conn.cursor() as cursor:
					cursor.execute('select "id", "name", "username" from "Admins"')
					results = cursor.fetchall()
		except Exception as e:
			messagebox.showwarning("Database Error", f"An error occured related to the database. Notify BAXENATOR for help\n{e}")
			return
		
		for item in self.tree_admins.get_children():
			self.tree_admins.delete(item)

		self.admins = results
		for result in results:
			id, name, username = result
			# print(result)
			self.tree_admins.insert("", "end", iid=id, values=(name, username))

	def updateAdminActions(self):
		try:
			with psycopg2.connect(**self.db_config) as conn:
				with conn.cursor() as cursor:
					cursor.execute('''
					select t1."name" as "adminName", t1."actionTime", t1."actionType", t1."adminId", t1."reason", t2."name" as "playerName" from
					(select * from (select * from "AdminActions") aa join (select * from "Admins") a on aa."adminId" = a.id ) t1
					join
					(select "identity", "name" from "Players") t2
					on t1."playerIdentity" = t2."identity"
					order by t1."actionTime" desc
					''')
					results = cursor.fetchall()
		except Exception as e:
			messagebox.showwarning("Database Error", f"An error occured related to the database. Notify BAXENATOR for help\n{e}")
			return
		
		for item in self.tree_adminActions.get_children():
			self.tree_adminActions.delete(item)
		
		self.adminActions = [AdminAction(x) for x in results]
		for adminAction in self.adminActions:
			self.tree_adminActions.insert("", "end", values=(
				adminAction.adminName,
				adminAction.actionType,
				adminAction.playerName,
				adminAction.reason,
				adminAction.actionTime.strftime("%m/%d/%y   %H:%M")
			))
		# print([str(x) for x in self.adminActions])
		self.filterToggle_var.set(False)
	
	def selectAdmin(self, event):
		if self.filterToggle_var.get():
			self.applyActionFilter()

	def applyActionFilter(self):
		selectedIids = self.tree_admins.selection()
		if not selectedIids:
			messagebox.showerror("", "Select an admin")
			self.filterToggle_var.set(False)
			return
		
		selectedIids = [int(x) for x in selectedIids]
		for item in self.tree_adminActions.get_children():
			self.tree_adminActions.delete(item)
		for adminAction in self.adminActions:
			print(selectedIids, str(adminAction))
			print(adminAction.adminId in selectedIids)
			if not self.filterToggle_var.get() or adminAction.adminId in selectedIids:
				self.tree_adminActions.insert("", "end", values=(
					adminAction.adminName,
					adminAction.actionType,
					adminAction.playerName,
					adminAction.reason,
					adminAction.actionTime.strftime("%m/%d/%y   %H:%M")
				))

	def createAdmin(self):
		if not self.isLoggedIn:
			messagebox.showerror("", "Login to use")
			return

		adminName = self.adminName_var.get()
		adminUsername = self.username_var.get()
		adminPassword = self.password_var.get()

		if not (adminName and adminUsername and adminPassword):
			messagebox.showerror("Invalid Operation", "Enter required information")
			return
		
		if (adminUsername in [username for (adminId, name, username) in self.admins]):
			messagebox.showerror("Username already exists")
			return

		try:
			with psycopg2.connect(**self.db_config) as conn:
				with conn.cursor() as cursor:
					cursor.execute("select public.create_admin_user(%s::text, %s::text, %s::text)", (adminUsername, adminPassword, adminName))
		except Exception as e:
			messagebox.showwarning("Database Error", f"An error occured related to the database. Notify BAXENATOR for help\n{e}")
			return
		
		self.updateAdminsList()
	
	def disableAdmin(self):
		selectedIids = self.tree_admins.selection()
		if not selectedIids:
			messagebox.showerror("", "Select an admin")
			return
		adminName, adminUsername = self.tree_admins.item(selectedIids[0], "values")

		if adminUsername == "warpigs_bot":
			messagebox.showerror("", "You can not disable the warpigs bot account")
			return
		
		if adminUsername == "disabled":
			messagebox.showerror("", "Account is already disabled")
			return

		if not messagebox.askokcancel(f"Disable Admin: {adminName}", f"Are you sure you want to disable the admin account: {adminName}"):
			return
		
		try:
			with psycopg2.connect(**self.db_config) as conn:
				with conn.cursor() as cursor:
					cursor.execute("select public.disable_admin_user(%s::text)", (adminUsername,))
		except Exception as e:
			messagebox.showwarning("Database Error", f"An error occured related to the database. Notify BAXENATOR for help\n{e}")
			return
		
		self.updateAdminsList()

class AdminAction():
	def __init__(self, adminActionQueryResult):
		# t1."name" as "adminName", t1."actionTime", t1."actionType", t1."adminId", t1."reason", t2."name" as "playerName"
		self.adminName: str = adminActionQueryResult[0]
		self.actionTime: datetime = adminActionQueryResult[1]
		self.actionType: str = adminActionQueryResult[2]
		self.adminId: int = adminActionQueryResult[3]
		self.reason: str = adminActionQueryResult[4]
		self.playerName: str = adminActionQueryResult[5]
	
	def __str__(self):
		return str((self.adminName, str(self.actionTime), self.actionType, self.adminId, self.reason, self.playerName))

if __name__ == "__main__":
	root = tk.Tk()
	app = AdminSearchApp(root)
	root.mainloop()