import tkinter as tk

# Create the main window
window = tk.Tk()

# Set window title
window.title("My First GUI Window")

# Set window size (width x height)
window.geometry("400x300")

# Add a label
label = tk.Label(window, text="Welcome to Python GUI!", font=("Arial", 16))
label.pack(pady=20)

# Run the application
window.mainloop()
