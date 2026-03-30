import tkinter as tk
from tkinter import messagebox
import random
import heapq
import threading

class PuzzleSolver:
    """Class to solving the 15-puzzle using the A* search algorithm."""
    
    @staticmethod
    def get_manhattan_distance(board):
        """Calculates the Manhattan distance heuristic for the current board state."""
        dist = 0
        for i in range(16):
            val = board[i]
            if val != 0:
                # Calculate correct row and column (1-indexed conceptually)
                target_r = (val - 1) // 4
                target_c = (val - 1) % 4
                
                curr_r = i // 4
                curr_c = i % 4
                
                dist += abs(target_r - curr_r) + abs(target_c - curr_c)
        return dist

    @staticmethod
    def get_neighbors(board, blank_pos):
        """Returns all valid reachable states from the current board."""
        neighbors = []
        r, c = blank_pos // 4, blank_pos % 4
        # Down, Up, Right, Left adjacent directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 4 and 0 <= nc < 4:
                n_blank = nr * 4 + nc
                n_board = list(board)
                # Swap blank tile with the adjacent tile
                n_board[blank_pos], n_board[n_blank] = n_board[n_blank], n_board[blank_pos]
                neighbors.append((tuple(n_board), n_blank))
                
        return neighbors

    @staticmethod
    def solve(start_board, start_blank, check_flag=lambda: True):
        """Executes the A* search algorithm.
        Returns the optimal path (list of blank tile positions) to solve the puzzle."""
        start_state = tuple(start_board)
        
        # Priority queue stores tuples of: 
        # (f_score, g_score, current_board_state, blank_position, path_taken)
        pq = []
        heapq.heappush(pq, (PuzzleSolver.get_manhattan_distance(start_state), 0, start_state, start_blank, []))
        visited = set()

        goal_state = tuple(range(1, 16)) + (0,)

        while pq:
            # Check the running flag to allow thread cancellation
            if not check_flag():
                return None 

            priority, cost, current_board, current_blank, path = heapq.heappop(pq)

            # Reached goal state
            if current_board == goal_state:
                return path

            if current_board in visited:
                continue
            visited.add(current_board)

            for n_board, n_blank in PuzzleSolver.get_neighbors(current_board, current_blank):
                if n_board not in visited:
                    new_cost = cost + 1
                    new_priority = new_cost + PuzzleSolver.get_manhattan_distance(n_board)
                    heapq.heappush(pq, (new_priority, new_cost, n_board, n_blank, path + [n_blank]))
        
        return None


class PuzzleGame:
    """Manages the internal state, history, and actions for the puzzle game."""
    def __init__(self):
        self.board = list(range(1, 16)) + [0]
        self.blank_pos = 15
        self.history = []
        
    def move(self, idx):
        """Attempts to move the tile at the given index. Returns True if successful."""
        r1, c1 = idx // 4, idx % 4
        r2, c2 = self.blank_pos // 4, self.blank_pos % 4
        
        # Determine if tiles are adjacent (Manhattan distance = 1)
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            # Save state for undo functionality
            self.history.append((list(self.board), self.blank_pos))
            # Swap
            self.board[idx], self.board[self.blank_pos] = self.board[self.blank_pos], self.board[idx]
            self.blank_pos = idx
            return True
        return False

    def undo(self):
        """Reverts to the most recent board state stored in history."""
        if self.history:
            self.board, self.blank_pos = self.history.pop()
            return True
        return False
        
    def shuffle(self):
        """Randomizes the board by executing a sequence of valid moves from a solved state."""
        self.board = list(range(1, 16)) + [0]
        self.blank_pos = 15
        self.history.clear()
        
        prev_blank = -1
        # Perform 50 random valid moves to shuffle the board adequately
        for _ in range(50):
            neighbors = PuzzleSolver.get_neighbors(self.board, self.blank_pos)
            # Avoid immediately reversing the previous move
            valid_moves = [n for n in neighbors if n[1] != prev_blank]
            if not valid_moves:
                valid_moves = neighbors
            
            chosen_board, new_blank = random.choice(valid_moves)
            prev_blank = self.blank_pos
            self.board = list(chosen_board)
            self.blank_pos = new_blank

    def is_solved(self):
        """Checks if the 1-15 sequence is cleanly ordered."""
        return self.board == list(range(1, 16)) + [0]


class PuzzleGUI:
    """Tkinter-based interface for displaying and controlling the Puzzle game."""
    def __init__(self, root):
        self.root = root
        self.root.title("15-Puzzle Master")
        self.root.configure(bg="#2F3640")
        self.root.resizable(False, False)
        
        self.game = PuzzleGame()
        self.buttons = []
        self.is_animating = False
        self.hint_tile = None
        
        self.create_widgets()
        self.game.shuffle()
        self.update_ui()
        
    def create_widgets(self):
        """Initializes all Tkinter frames, labels, and buttons."""
        # Top Header Area
        header = tk.Frame(self.root, bg="#2F3640", pady=10)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="15-Puzzle", font=("Segoe UI", 26, "bold"), bg="#2F3640", fg="#FBC531").pack()
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to play!")
        tk.Label(header, textvariable=self.status_var, font=("Segoe UI", 12), bg="#2F3640", fg="#4CD137").pack()
        
        # Main Game Grid
        self.grid_frame = tk.Frame(self.root, bg="#353B48", bd=8, relief=tk.FLAT)
        self.grid_frame.pack(pady=10, padx=20)
        
        for i in range(16):
            btn = tk.Button(
                self.grid_frame, text="", font=("Segoe UI", 22, "bold"), 
                width=4, height=2, relief=tk.RAISED, bd=3,
                command=lambda idx=i: self.on_tile_click(idx)
            )
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
            self.buttons.append(btn)
            
        # Top Row of Control Buttons
        controls1 = tk.Frame(self.root, bg="#2F3640", pady=5)
        controls1.pack(fill=tk.X)
        
        self.undo_btn = self.create_control_btn(controls1, "Undo", "#E84118", self.undo_move)
        self.undo_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.hint_btn = self.create_control_btn(controls1, "Hint", "#FBC531", self.show_hint, fg="#2F3640")
        self.hint_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.shuffle_btn = self.create_control_btn(controls1, "Shuffle", "#4CD137", self.shuffle_board)
        self.shuffle_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        # Bottom Row of Control Buttons
        controls2 = tk.Frame(self.root, bg="#2F3640", pady=5)
        controls2.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 15))
        
        self.auto_solve_btn = self.create_control_btn(controls2, "Auto-Solve", "#00A8FF", self.start_auto_solve)
        self.auto_solve_btn.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)
        
        self.instant_solve_btn = self.create_control_btn(controls2, "Instant Solve", "#9C88FF", self.instant_solve)
        self.instant_solve_btn.pack(side=tk.RIGHT, padx=20, expand=True, fill=tk.X)

        self.control_buttons = [self.undo_btn, self.hint_btn, self.shuffle_btn, 
                                 self.auto_solve_btn, self.instant_solve_btn]

    def create_control_btn(self, parent, text, bg_color, command, fg="white"):
        """Helper to create standardized control buttons."""
        return tk.Button(parent, text=text, font=("Segoe UI", 12, "bold"), bg=bg_color, fg=fg,
                         activebackground=bg_color, relief=tk.FLAT, pady=5, command=command)

    def update_ui(self):
        """Redraws the board based on the current internal sequence."""
        for i in range(16):
            val = self.game.board[i]
            if val == 0:
                self.buttons[i].config(text="", bg="#353B48", state=tk.DISABLED, relief=tk.FLAT)
            else:
                # Dynamic coloring: distinguish placed tiles from displaced tiles
                bg_color = "#00A8FF" if val == i + 1 else "#DCDDE1"
                fg_color = "white" if val == i + 1 else "#2F3640"
                
                # Apply visual hint highlight if applicable
                if self.hint_tile == i:
                    bg_color = "#FBC531"
                    fg_color = "#2F3640"
                    
                self.buttons[i].config(text=str(val), bg=bg_color, fg=fg_color, state=tk.NORMAL, relief=tk.RAISED)
        
        self.hint_tile = None # Clear hint flag after rendering once
                
        # Trigger Win sequence if the board is solved and no animations are actively walking
        if self.game.is_solved() and not self.is_animating:
            self.status_var.set("Puzzle Solved! 🎉")
            messagebox.showinfo("Congratulations!", "You have solved the puzzle!")
            self.game.history.clear()

    def on_tile_click(self, idx):
        """Handles manual tile interactions."""
        if self.is_animating:
            return
        if self.game.move(idx):
            self.status_var.set("Moves: " + str(len(self.game.history)))
            self.update_ui()

    def undo_move(self):
        """Hooks the undo action to the GUI."""
        if self.is_animating:
            return
        if self.game.undo():
            self.status_var.set("Moves: " + str(len(self.game.history)))
            self.update_ui()
            
    def shuffle_board(self):
        """Hooks the shuffle action to the GUI."""
        if self.is_animating:
            return
        self.game.shuffle()
        self.status_var.set("Board shuffled. Good luck!")
        self.update_ui()
        
    def show_hint(self):
        """Fetches the next best optimal move via an A* thread without freezing."""
        if self.is_animating or self.game.is_solved():
            return
            
        self.status_var.set("Calculating hint...")
        self.set_controls_state(tk.DISABLED)
        self.is_animating = True # repurpose lock
        
        thread = threading.Thread(target=self._run_hint_thread)
        thread.daemon = True
        thread.start()

    def _run_hint_thread(self):
        path = PuzzleSolver.solve(self.game.board, self.game.blank_pos)
        self.root.after(0, self._apply_hint, path)

    def _apply_hint(self, path):
        self.is_animating = False
        self.set_controls_state(tk.NORMAL)
        if path and len(path) > 0:
            self.hint_tile = path[0]
            self.status_var.set("Hint applied! Move the yellow tile.")
            self.update_ui()
        else:
            self.status_var.set("Already solved or no path!")

    def instant_solve(self):
        """Snaps the board directly into the winning state."""
        if self.is_animating or self.game.is_solved():
            return
            
        self.game.board = list(range(1, 16)) + [0]
        self.game.blank_pos = 15
        self.status_var.set("Puzzle Instantly Solved!")
        self.update_ui()

    def start_auto_solve(self):
        """Initiates the A* step-by-step bot execution."""
        if self.is_animating or self.game.is_solved():
            return
            
        self.is_animating = True
        self.status_var.set("Solving with A*... Please wait.")
        self.set_controls_state(tk.DISABLED)
        
        thread = threading.Thread(target=self._run_solver_thread)
        thread.daemon = True
        thread.start()
        
    def _run_solver_thread(self):
        """Background thread executing the core A* algorithm."""
        path = PuzzleSolver.solve(self.game.board, self.game.blank_pos, lambda: self.is_animating)
        
        if path:
            self.root.after(0, self.animate_solution, path, 0)
        else:
            self.root.after(0, self.solving_failed)

    def animate_solution(self, path, step):
        """Iterates through the discovered solution visually via UI callbacks."""
        if step < len(path):
            self.status_var.set(f"Auto-Move: {step+1} / {len(path)}")
            next_pos = path[step]
            self.game.move(next_pos)
            self.update_ui()
            # Recursively animate the next tile movement after a 1.2-second delay
            self.root.after(1200, self.animate_solution, path, step + 1)
        else:
            self.is_animating = False
            self.set_controls_state(tk.NORMAL)
            self.update_ui() # Triggers win sequence
            
    def solving_failed(self):
        """Backup fallback message if the solver exceeds parameters or encounters an issue."""
        self.is_animating = False
        self.set_controls_state(tk.NORMAL)
        self.status_var.set("Failed to find solution.")
        
    def set_controls_state(self, state):
        """Toggles interface interactability to safeguard against overlapping requests."""
        for btn in self.control_buttons:
            btn.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
