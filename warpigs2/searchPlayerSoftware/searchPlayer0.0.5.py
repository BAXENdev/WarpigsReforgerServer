import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pyperclip  # For clipboard functionality

class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Search")
        self.root.geometry("800x600")  # Increased height for the new section
        self.root.minsize(800, 600)
        
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
        command_types = ["ban", "unban", "kick"]
        command_type_dropdown = ttk.Combobox(cmd_frame, textvariable=self.command_type_var, 
                                            values=command_types, state="readonly", width=10)
        command_type_dropdown.pack(side=tk.LEFT, padx=5)
        command_type_dropdown.bind("<<ComboboxSelected>>", self.on_command_type_change)
        
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
        time_preset_dropdown = ttk.Combobox(time_selection_frame, 
                                            textvariable=self.time_preset_var,
                                            values=list(time_presets.keys()), 
                                            state="readonly", 
                                            width=15)
        time_preset_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        time_preset_dropdown.bind("<<ComboboxSelected>>", self.on_time_preset_change)
        
        # Custom time input
        vcmd_num = (self.root.register(self.validate_number), '%P')
        self.time_var = tk.StringVar(value="0")  # Default to 0 for Permanent
        time_entry = ttk.Entry(time_selection_frame, textvariable=self.time_var, 
                              validate="key", validatecommand=vcmd_num, width=10)
        time_entry.pack(side=tk.LEFT, padx=5)
        
        # Reason input
        reason_frame = ttk.Frame(input_frame)
        reason_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(reason_frame, text="Reason:").pack(anchor=tk.W)
        self.reason_var = tk.StringVar()
        reason_entry = ttk.Entry(reason_frame, textvariable=self.reason_var)
        reason_entry.pack(fill=tk.X)
        
        # Bind events to update command
        self.time_var.trace_add("write", self.update_command)
        self.reason_var.trace_add("write", self.update_command)
        
        # Initialize selected identity
        self.selected_identity = None
        
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
        search_button = ttk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.grid(row=0, column=2, padx=5, pady=5)
        
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
        
        # Initialize API endpoint
        self.api_url = "http://51.222.244.193:24024/searchPlayer"
        
        # Set focus to search entry
        self.search_entry.focus()
        
        # Bind Enter key to search
        self.root.bind('<Return>', lambda event: self.perform_search())
        
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
                self.selected_identity = values[1]
                self.update_command()
    
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
    
    def perform_search(self):
        """Execute the search against the API"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Invalid Input", "Please enter a player name to search for")
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Reset selection
        self.selected_identity = None
        self.update_command()
        
        try:
            # Make API request
            response = requests.get(f"{self.api_url}?searchName={search_term}")
            
            # Check response status
            if response.status_code != 200:
                error_message = "Unknown error"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message = error_data["error"]
                except:
                    pass
                messagebox.showerror("API Error", f"Error: {error_message}")
                return
            
            # Process successful response
            data = response.json()
            
            if "results" in data and isinstance(data["results"], list):
                results = data["results"]
                
                # Update results in the treeview
                for player in results:
                    name = player.get("name", "N/A")
                    identity = player.get("identity", "N/A")
                    self.results_tree.insert("", tk.END, values=(name, identity))
                
                # Show message if no results found
                if not results:
                    messagebox.showinfo("No Results", "No players found matching your search criteria.")
            else:
                messagebox.showerror("Invalid Response", "The API returned an unexpected response format.")
        
        except requests.RequestException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the API: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerSearchApp(root)
    root.mainloop()