
# @Author BAXENATOR
# @License http://baxendev.com/warpigs-license-v1.0.html

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # For clipboard functionality
import psycopg2
from bercon import BERconClient, BERconResponse
import asyncio
import requests
import datetime

class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Search")
        self.root.geometry("800x630")  # Increased height for the new section
        self.root.minsize(800, 630)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 3. Command Section
        command_frame = ttk.LabelFrame(main_frame, text="Command", padding="10")
        command_frame.pack(fill=tk.X, pady=10)
        
        # First row - Command type, preview and copy button
        cmd_frame = ttk.Frame(command_frame)
        cmd_frame.pack(fill=tk.X, pady=5)
        
        # Command type dropdown
        ttk.Label(cmd_frame, text="Action:").pack(side=tk.LEFT, padx=5)
        self.command_type_var = tk.StringVar(value="ban")
        # command_types = ["ban", "unban", "kick"]
        command_types = ["ban", "unban"]
        self.command_type_dropdown = ttk.Combobox(cmd_frame, textvariable=self.command_type_var, 
                                            values=command_types, state="readonly", width=10)
        self.command_type_dropdown.pack(side=tk.LEFT, padx=5)
        self.command_type_dropdown.bind("<<ComboboxSelected>>", self.on_command_type_change)
        
        ttk.Label(cmd_frame, text="Command:").pack(side=tk.LEFT, padx=5)
        self.command_var = tk.StringVar()
        self.command_var.set("#ban create IDENTITY")
        command_entry = ttk.Entry(cmd_frame, textvariable=self.command_var, width=50, state="readonly")
        command_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        copy_button = ttk.Button(cmd_frame, text="Copy", command=self.copy_command)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # Second row - Time and Reason inputs
        input_frame = ttk.Frame(command_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Time input (dropdown and custom)
        time_frame = ttk.Frame(input_frame)
        time_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(time_frame, text="Ban Time:").pack(anchor=tk.W)
        
        time_selection_frame = ttk.Frame(time_frame)
        time_selection_frame.pack(fill=tk.X)
        
        # Time dropdown
        self.time_preset_var = tk.StringVar(value="Permanent")
        time_presets = {
            "Permanent": 0,
            "5 Minutes": 300,  # 5 * 60
            "1 Hour": 3600,    # 60 * 60
            "12 Hours": 43200, # 12 * 60 * 60
            "1 Day": 86400,    # 24 * 60 * 60
            "1 Week": 604800,  # 7 * 24 * 60 * 60
            "1 Month": 2592000 # 30 * 24 * 60 * 60
        }
        self.time_presets_dict = time_presets
        self.time_preset_dropdown = ttk.Combobox(time_selection_frame, 
                                            textvariable=self.time_preset_var,
                                            values=list(time_presets.keys()), 
                                            state="readonly", 
                                            width=15)
        self.time_preset_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.time_preset_dropdown.bind("<<ComboboxSelected>>", self.on_time_preset_change)
        
        # Custom time input
        vcmd_num = (self.root.register(self.validate_number), '%P')
        self.time_var = tk.StringVar(value="0")  # Default to 0 for Permanent
        self.time_entry = ttk.Entry(time_selection_frame, textvariable=self.time_var, 
                              validate="key", validatecommand=vcmd_num, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        
        # Reason input
        reason_frame = ttk.Frame(input_frame)
        reason_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(reason_frame, text="Reason:").pack(anchor=tk.W)
        self.reason_var = tk.StringVar()
        self.reason_entry = ttk.Entry(reason_frame, textvariable=self.reason_var)
        self.reason_entry.pack(fill=tk.X)
        
        # Bind events to update command
        self.time_var.trace_add("write", self.update_command)
        self.reason_var.trace_add("write", self.update_command)
        
        # Initialize selected identity
        self.selected_identity = None
        self.selected_name = None

        # Execute Ban Frame
        execute_frame = ttk.Frame(command_frame)
        execute_frame.pack(fill=tk.X, pady=5)

        execute_button = ttk.Button(execute_frame, text="Execute Command", command=self.execute_command)
        execute_button.pack(side=tk.LEFT, padx=5)

        server1_frame = execute_frame = ttk.Frame(execute_frame)
        server1_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(server1_frame, text="Server 1: ").pack(side=tk.LEFT)
        self.server1_execute_output = ttk.Label(server1_frame, text="---", foreground="grey")
        self.server1_execute_output.pack(side=tk.LEFT)
        
        server2_frame = execute_frame = ttk.Frame(execute_frame)
        server2_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(server2_frame, text="Server 2: ").pack(side=tk.LEFT)
        self.server2_execute_output = ttk.Label(server2_frame, text="---", foreground="grey")
        self.server2_execute_output.pack(side=tk.LEFT)
        
        server3_frame = execute_frame = ttk.Frame(execute_frame)
        server3_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(server3_frame, text="Server 3: ").pack(side=tk.LEFT)
        self.server3_execute_output = ttk.Label(server3_frame, text="---", foreground="grey")
        self.server3_execute_output.pack(side=tk.LEFT)
        
        # 1. Search Section
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="10")
        search_frame.pack(fill=tk.X, pady=10)
        
        # Search input with validation
        ttk.Label(search_frame, text="Player Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        vcmd = (self.root.register(self.validate_input), '%P')
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, validate="key", validatecommand=vcmd)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Search button
        self.search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)
        
        # 2. Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a frame to hold the treeview and scrollbar
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for results with single selection mode
        self.results_tree = ttk.Treeview(tree_frame, columns=("name", "identity"), show="headings", selectmode="browse")
        self.results_tree.heading("name", text="Player Name")
        self.results_tree.heading("identity", text="Identity (UUID)")
        self.results_tree.column("name", width=200)
        self.results_tree.column("identity", width=400)
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Position the treeview and scrollbars using grid
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure the grid to expand properly
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.results_tree.bind("<<TreeviewSelect>>", self.on_select)
        
        license_button = ttk.Button(main_frame, text="License", command=self.show_license_popup)
        license_button.pack(anchor="w", pady=5)
        
        # Set focus to search entry
        self.search_entry.focus()
        
        # Bind Enter key to search
        self.root.bind('<Return>', lambda event: self.perform_search())

        # BerconClients
        self.server1_bercon = BERconClient("148.113.163.200", 19021, "Warpigs1245")
        self.server2_bercon = BERconClient("148.113.163.200", 19022, "Warpigs1245")
        self.server3_bercon = BERconClient("148.113.163.200", 19023, "Warpigs1245")
        
    def validate_input(self, value):
        """Validate that input contains only letters and numbers"""
        if value == "" or value.isalnum():
            return True
        return False
    
    def validate_number(self, value):
        """Validate that input contains only numbers"""
        if value == "" or value.isdigit():
            return True
        return False
    
    def on_command_type_change(self, event):
        """Handle change of command type"""
        self.update_command()
        
        # Show/hide time and reason based on command type
        # command_type = self.command_type_var.get()
        # if command_type == "ban":
        #     # Enable time and reason for ban
        #     for widget in self.winfo_children():
        #         if hasattr(widget, 'time_entry'):
        #             widget.config(state="normal")
        #         if hasattr(widget, 'reason_entry'):
        #             widget.config(state="normal")
        # else:
        #     # Disable and clear time and reason for unban/kick
        #     self.time_var.set("")
        #     self.reason_var.set("")
    
    def on_time_preset_change(self, event):
        """Update the time value when a preset is selected"""
        preset = self.time_preset_var.get()
        seconds = self.time_presets_dict.get(preset, 0)
        self.time_var.set(str(seconds))
    
    def on_select(self, event):
        """Handle selection of an item in the treeview"""
        selected_items = self.results_tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.results_tree.item(item, "values")
            if values and len(values) >= 2:
                self.selected_name = values[0]
                self.selected_identity = values[1]
                self.update_command()
        self.server1_execute_output.config(text="---", foreground="grey")
        self.server2_execute_output.config(text="---", foreground="grey")
        self.server3_execute_output.config(text="---", foreground="grey")
    
    def update_command(self, *args):
        """Update the command text based on selected identity and inputs"""        
        command_type = self.command_type_var.get()
        
        if command_type == "ban":
            if self.selected_identity:
                command = f"#ban create {self.selected_identity}"
                
                time = self.time_var.get().strip()
                reason = self.reason_var.get().strip()
                
                if time:
                    command += f" {time}"
                
                if reason and not time:
                    command += f" 0 {reason}"
                elif reason:
                    command += f" {reason}"
            else:
                command = "#ban create IDENTITY"
                
        elif command_type == "unban":
            if self.selected_identity:
                command = f"#ban remove {self.selected_identity}"
            else:
                command = "#ban remove IDENTITY"

        else:  # kick
            if self.selected_identity:
                command = f"#kick {self.selected_identity}"
            else:
                command = "#kick IDENTITY"
        
        self.command_var.set(command)
    
    def copy_command(self):
        """Copy the command to clipboard"""
        command = self.command_var.get()
        try:
            if not self.selected_identity:
                raise Exception("Please select a player first")
            pyperclip.copy(command)
            messagebox.showinfo("Copied", "Command copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy command: {str(e)}")
    
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

    def perform_search(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Invalid Input", "Please enter a player name to search for")
            return
        
        self.server1_execute_output.config(text="---", foreground="grey")
        self.server2_execute_output.config(text="---", foreground="grey")
        self.server3_execute_output.config(text="---", foreground="grey")
        
        results: list[tuple[str, str]] = []
        # try:
        with psycopg2.connect(**{
            "dbname": "armaReforger",
            "user": "playerSearcher",
            "password": "108j31!@3089ud#!d12@091428u",
            "host": "135.148.150.144",
            "port": "35432"
        }) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'select \"name\", \"identity\" from public.\"Players\" where name ilike %s',
                    (f"%{search_term}%",)
                )
                results = cur.fetchall()
        # except Exception as error:
        #     messagebox.showwarning("Database Error", "An error occured related to the database. Notify BAXENATOR for help")
        #     print(str(error))
        #     return
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.selected_identity = None
        self.selected_name = None
        self.update_command()

        if not results:
            messagebox.showinfo("No Results", "No players found matching your search criteria.")

        for player in results:
            name = player[0]
            identity = player[1]
            self.results_tree.insert("", tk.END, values=(name, identity))
    
    def disable_inputs(self):
        self.command_type_dropdown.config(state=tk.DISABLED)
        self.time_preset_dropdown.config(state=tk.DISABLED)
        self.time_entry.config(state=tk.DISABLED)
        self.reason_entry.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        self.results_tree.config(selectmode="none")
    
    def enable_inputs(self):
        self.command_type_dropdown.config(state="readonly")
        self.time_preset_dropdown.config(state="readonly")
        self.time_entry.config(state=tk.NORMAL)
        self.reason_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.results_tree.config(selectmode="browse")

    def execute_command(self):
        if not self.selected_identity:
            messagebox.showerror("Execution Error", "Select a user to execute command")
            return
        
        self.server1_execute_output.config(text="???", foreground="orange")
        self.server2_execute_output.config(text="???", foreground="orange")
        self.server3_execute_output.config(text="???", foreground="orange")
        
        self.disable_inputs()

        asyncio.get_event_loop().run_in_executor(None, self.execute_command_blocking)
    
    def execute_command_blocking(self):
        command = self.command_var.get()
        response1: BERconResponse = self.server1_bercon.sendCommand(command)
        response2: BERconResponse = self.server2_bercon.sendCommand(command)
        response3: BERconResponse = self.server3_bercon.sendCommand(command)

        errorOutput = ""
        results: list[str] = []
        if response1.success:
            results.append("Success")
        else:
            results.append("Failed")
            errorOutput += f"Server1: {response1}\n"
        if response2.success:
            results.append("Success")
        else:
            results.append("Failed")
            errorOutput += f"Server2: {response2}\n"
        if response3.success:
            results.append("Success")
        else:
            results.append("Failed")
            errorOutput += f"Server3: {response3}\n"

        self.root.after(0, lambda: self.execute_command_results(results, errorOutput))
    
    def execute_command_results(self, results: list[str], errorOutput: str):
        if results[0] == "Success":
            self.server1_execute_output.config(text="Success", foreground="green")
        else:
            self.server1_execute_output.config(text="Failed", foreground="red")
        if results[1] == "Success":
            self.server2_execute_output.config(text="Success", foreground="green")
        else:
            self.server2_execute_output.config(text="Failed", foreground="red")
        if results[2] == "Success":
            self.server3_execute_output.config(text="Success", foreground="green")
        else:
            self.server3_execute_output.config(text="Failed", foreground="red")

        if errorOutput:
            messagebox.showerror("BERcon Error", errorOutput)
        
        self.postInDiscord()
        self.enable_inputs()

    def postInDiscord(self):
        if self.command_type_var.get() == "ban":
            ban_duration = int(self.time_entry.get())
            ban_days = ban_duration // 86400
            ban_hours = (ban_duration % 86400) // 3600
            ban_duration_str = ""
            if ban_duration == 0:
                ban_duration_str = "Permanent"
            elif ban_duration < 3600:
                ban_duration_str = "Temporary (1 hours or less)"
            else:
                ban_duration_str = f"{ban_days} {'Days' if ban_days > 1 else 'Day' } {ban_hours} {'Hours' if ban_hours > 1 else 'Hour'}"
            ban_title = f"{self.selected_name} Banned for: {self.reason_entry.get()}"
            ban_description = (f"**Banned on:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H-%M")} UTC\n**Ban Duration:** {ban_duration_str}")
            response = requests.post(
                "https://discord.com/api/webhooks/1361087913772843099/PRZMSrAaojV0xoNFBY6oDvnQV6I5Itg06sOD6VjYp4aKXqBHSH1Mg2WokYgdgy2kdUqZ",
                json={
                    "username": "BanLogger",
                    "embeds": [
                        {
                            "title": ban_title,
                            "description": ban_description,
                            "color": 0xff0000
                        }
                    ]
                }
            )
        else:
            ban_title = f"{self.selected_name} Unbanned"
            ban_description = (f"**Unbanned on:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H-%M")} UTC")
            response = requests.post(
                "https://discord.com/api/webhooks/1361087913772843099/PRZMSrAaojV0xoNFBY6oDvnQV6I5Itg06sOD6VjYp4aKXqBHSH1Mg2WokYgdgy2kdUqZ",
                json={
                    "username": "BanLogger",
                    "embeds": [
                        {
                            "title": ban_title,
                            "description": ban_description,
                            "color": 0xff0000
                        }
                    ]
                }
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerSearchApp(root)
    root.mainloop()