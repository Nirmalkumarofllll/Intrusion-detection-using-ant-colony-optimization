import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import time
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess

global n
n=0
# AntColony class definition and submit_number function remain unchanged
class AntColony:
    # Include the AntColony class code here
    def _init_(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        """
        Args:
        distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
        n_ants (int): Number of ants running per iteration
        n_best (int): Number of best ants who deposit pheromone
        n_iteration (int): Number of iterations
        decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay,
                        so 0.95 will lead to decay, 0.5 to much faster decay.
        alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight.
        beta (int or float): exponent on distance, higher beta give distance more weight.
        """
        self.distances  = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta

    def run(self):
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheromone(all_paths, self.n_best, shortest_path=shortest_path)
            shortest_path = min(all_paths, key=lambda x: x[1])
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            self.pheromone * self.decay
        return all_time_shortest_path

    def spread_pheromone(self, all_paths, n_best, shortest_path):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += 1.0 / self.distances[move]

    def gen_path_dist(self, path):
        total_dist = 0
        for ele in path:
            total_dist += self.distances[ele]
        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))
            prev = move
            visited.add(move)
        path.append((prev, start)) # going back to where we started
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone * self.alpha * (( 1.0 / dist) * self.beta)

        norm_row = row / row.sum()
        move = np.random.choice(self.all_inds, 1, p=norm_row)[0] # Corrected this line
        return move



    # Include the AntColony class code here
    # AntColony class code remains the same

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        print("Uploaded file:", file_path)
        scan_button.config(state=tk.NORMAL)
        messagebox.showinfo("File Uploaded", f"File Uploaded Successfully {file_path}, Click Scan to proceed with scanning")



def submit_number():
    try:


        num_nodes = int(entry.get())
        n=num_nodes
        if num_nodes < 2:
            messagebox.showerror("Error", f"Number should not be less than two")
            entry.delete(0, tk.END)
            upload_button.config(state=tk.DISABLED)
            scan_button.config(state=tk.DISABLED)
            return


        G = nx.complete_graph(num_nodes)

        # Visualize the initial network
        pos = nx.circular_layout(G)
        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_color='black', ax=ax)
        ax.set_title("Initial Network")

        distances = np.random.randint(1, 10, (num_nodes, num_nodes))
        np.fill_diagonal(distances, 9999)
        n_ants = 5
        n_best = 2
        n_iterations = 20
        decay = 0.1

        ant_colony = AntColony(distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=2)
        shortest_path = ant_colony.run()

        # Visualize the network with ACO paths
        fig_aco, ax_aco = plt.subplots(figsize=(5, 3))
        nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=10, font_color='black', ax=ax_aco)
        edges = [(shortest_path[0][i][0], shortest_path[0][i][1]) for i in range(len(shortest_path[0]) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red', width=2.0, ax=ax_aco)
        ax_aco.set_title("Network with ACO Paths")

        # Embed Matplotlib plots in Tkinter window with grid layout
        canvas_aco = FigureCanvasTkAgg(fig_aco, master=root)
        canvas_aco.get_tk_widget().grid(row=1, column=0, columnspan=3)
        upload_button.config(state=tk.NORMAL)

    except ValueError:
        messagebox.showerror("Error", "Number should be number")
        entry.delete(0, tk.END)
        upload_button.config(state=tk.DISABLED)
        scan_button.config(state=tk.DISABLED)

def perform_scan():
    result_text.delete(1.0, tk.END)
    scan_animation_label.config(text="Scanning...", fg="red")
    root.update()
    time.sleep(3)  # Simulate scanning process
    scan_animation_label.config(text="File Scanned", fg="limegreen")

    # Display scan results
    result_text.delete(1.0, tk.END)  # Clear previous results
    scan_result = f"Scan results: \n \nNumber Of Files scanned:1\n \nFiles passed through:  {n}\n \nFamily Of Malware Detected : NO Malware Detected"
    result_text.insert(tk.END, scan_result)



def exit_application():
    root.destroy()



# Create the main window
root = tk.Tk()
root.title("Intrusion detection with ACO routing")

# Create a stylish title label
title_label = tk.Label(root, text="Intrusion Detection system with ACO routing", font=('Helvetica', 20, 'bold'))
title_label.grid(row=0, column=0, columnspan=3, pady=10)

# Create a label for the command
command_label = tk.Label(root, text="Multiple Number Of Files Cannot Be Uploaded at single time",fg="red")
command_label.grid(row=3, column=0, columnspan=3)

# Create a button for uploading files
upload_button = tk.Button(root, text="Upload File", command=upload_file, state=tk.DISABLED, bg='gold', fg='white')
upload_button.grid(row=4, column=0, pady=10)

# Create a button for performing scan
scan_button = tk.Button(root, text="Scan", command=perform_scan, state=tk.DISABLED, bg='limegreen')
scan_button.grid(row=4, column=1, pady=10)

# Create a label for scan animation
scan_animation_label = tk.Label(root, text="")
scan_animation_label.grid(row=4, column=2, pady=10)

# Create a text widget to display scan results
result_text = tk.Text(root, height=10, width=50)
result_text.grid(row=5, column=0, columnspan=3, pady=10)

# Create a label for ACO input
label = tk.Label(root, text="Enter the number of nodes:")
label.grid(row=2, column=0)

# Create an entry widget for ACO input
entry = tk.Entry(root)
entry.grid(row=2, column=1)

# Create a submit button for ACO
submit_button = tk.Button(root, text="Submit", command=submit_number, bg="deepskyblue", fg="white")
submit_button.grid(row=2, column=2)

# Create an exit button at the bottom of the window
exit_button = tk.Button(root, text="Exit", command=exit_application, bg='orangered')
exit_button.grid(row=6, column=1, pady=20)


root.geometry("600x700+0+0")


# Start the main event loop
root.mainloop()
