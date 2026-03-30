15-Puzzle Master with AI Solver:

Description:  
This is a 4x4 sliding puzzle game (15-Puzzle) that you can play through an interactive desktop app. In addition, you can use the Artificial Intelligence solver included with the app to calculate and show the best way to solve any board configuration using the A* search algorithm.  

Features: 
Manual Gameplay: Smooth tile swapping via mouse clicks.  
Smart Shuffle: Guarantees that every randomized board is mathematically solvable.  
A Auto-Solver:* Watches the AI calculate the best path and animate the solution step-by-step.  
Hint System: Highlights the best possible next move to help you out if you get stuck.  
Undo Functionality: Revert your previous manual moves.  
Instant Solve: Snaps the board directly to the winning state.  
Win Detection: Automatically recognizes when you've ordered the tiles correctly.  

Technologies Used: 
Your Core Programming Language is Python 3.x.  
Your Graphical User Interface is Created Using Tkinter, the Built-In Python Library.  
Heapq and Threading are Standard Python Modules that Allow You to Optimize the A* Algorithm Priority Queue and Prevent The Solver From Freezing The GUI.  

How to Run the Project: 
Verify that you already have Python installed in order to continue to the next step.  
Obtain or download/install the required file 4x4_Puzzle.py from your computer.  
Use your terminal/command line application and change into the directory that contains the 4x4_Puzzle.py file.  

Run the following command:
bash  
python 4x4_Puzzle.py  
The game window will open automatically.   
Controls / Usage Instructions  
Moving Tiles: Click any tile directly next to the empty space to slide it over.  
Undo: Click to take back your last move.  
Hint: Click to highlight the best tile to move next in yellow.  
Shuffle: Scrambles the board to start a new game.  
Auto-Solve: Calculates the shortest path to victory and animates the tiles moving on their own.  
Instant Solve: Bypasses the animation and immediately completes the puzzle.  
