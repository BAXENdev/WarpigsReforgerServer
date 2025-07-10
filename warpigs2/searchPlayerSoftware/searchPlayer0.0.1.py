
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re

class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Search")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Create treeview for results
        self.results_tree = ttk.Treeview(results_frame, columns=("name", "identity"), show="headings")
        self.results_tree.heading("name", text="Player Name")
        self.results_tree.heading("identity", text="Identity (UUID)")
        self.results_tree.column("name", width=200)
        self.results_tree.column("identity", width=400)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
    
    def perform_search(self):
        """Execute the search against the API"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Invalid Input", "Please enter a player name to search for.")
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
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
