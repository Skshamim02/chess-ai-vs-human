import tkinter as tk
from tkinter import messagebox
import chess
import time


class ChessApp:
    def __init__(self, root):
        # Window setup
        self.root = root
        self.root.title("Enhanced Chess Game: AI vs Player")
        self.root.geometry("900x1000")
        self.root.resizable(False, False)

        # Game variables
        self.board = chess.Board()
        self.selected_square = None
        self.ai_difficulty = None
        self.player_color = chess.WHITE
        self.highlighted_squares = []
        self.last_move_squares = []
        self.start_time = None
        self.white_time = 0
        self.black_time = 0
        self.move_history = []

        # UI Elements
        self.create_board_frame()
        self.create_info_panel()
        self.create_timer_panel()
        self.choose_time_control()

    def choose_time_control(self):
        """Choose time control and difficulty level."""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Game Setup")
        setup_window.geometry("300x300")

        tk.Label(setup_window, text="Select Time Control:", font=("Arial", 14)).pack(pady=10)

        self.time_control = tk.StringVar(value="Blitz")
        for time_format in ["Blitz (3 mins)", "Rapid (15 mins)", "Classical (30 mins)"]:
            tk.Radiobutton(
                setup_window,
                text=time_format,
                variable=self.time_control,
                value=time_format.split(" ")[0],
                font=("Arial", 12),
            ).pack(anchor="w", padx=10)

        tk.Button(
            setup_window,
            text="Start Game",
            font=("Arial", 12),
            command=lambda: self.set_time_control(setup_window),
        ).pack(pady=20)

    def set_time_control(self, window):
        """Set the selected time control."""
        if "Blitz" in self.time_control.get():
            self.white_time = self.black_time = 180
        elif "Rapid" in self.time_control.get():
            self.white_time = self.black_time = 900
        else:
            self.white_time = self.black_time = 1800

        self.start_time = time.time()
        window.destroy()
        self.new_game()

    def create_board_frame(self):
        """Create the chessboard interface."""
        self.board_frame = tk.Frame(self.root, height=480, width=480)
        self.board_frame.pack(pady=10)
        self.squares = []
        self.square_size = 64

        for row in range(8):
            row_squares = []
            for col in range(8):
                color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"
                square = tk.Canvas(
                    self.board_frame, width=self.square_size, height=self.square_size, bg=color
                )
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda e, r=row, c=col: self.on_square_click(r, c))
                row_squares.append(square)
            self.squares.append(row_squares)

    def create_info_panel(self):
        """Create an information panel below the chessboard."""
        self.info_panel = tk.Frame(self.root)
        self.info_panel.pack()

        self.status_label = tk.Label(self.info_panel, text="Your Turn: White", font=("Arial", 14))
        self.status_label.pack(side=tk.TOP, pady=5)

        tk.Button(self.info_panel, text="New Game", command=self.new_game, font=("Arial", 10)).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(self.info_panel, text="Replay Game", command=self.replay_game, font=("Arial", 10)).pack(
            side=tk.LEFT, padx=5
        )

    def create_timer_panel(self):
        """Create a timer panel to track time for each player."""
        self.timer_panel = tk.Frame(self.root)
        self.timer_panel.pack(pady=10)

        self.white_timer_label = tk.Label(
            self.timer_panel, text=f"White: {self.format_time(self.white_time)}", font=("Arial", 12)
        )
        self.white_timer_label.grid(row=0, column=0, padx=20)

        self.black_timer_label = tk.Label(
            self.timer_panel, text=f"Black: {self.format_time(self.black_time)}", font=("Arial", 12)
        )
        self.black_timer_label.grid(row=1, column=0, padx=20)

    def format_time(self, seconds):
        """Format time in MM:SS."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        """Update the timer for the current player."""
        elapsed = time.time() - self.start_time

        if self.board.turn == chess.WHITE:
            self.white_time -= elapsed
            self.white_timer_label.config(
                text=f"White: {self.format_time(int(self.white_time))}"
            )
        else:
            self.black_time -= elapsed
            self.black_timer_label.config(
                text=f"Black: {self.format_time(int(self.black_time))}"
            )

        self.start_time = time.time()
        self.check_time_expired()

    def check_time_expired(self):
        """Check if time has expired for any player."""
        if self.white_time <= 0:
            self.end_game("Time's up! Black wins.")
        elif self.black_time <= 0:
            self.end_game("Time's up! White wins.")

    def on_square_click(self, row, col):
        """Handle piece selection and move execution."""
        self.update_timer()
        square = chess.square(col, 7 - row)

        if self.selected_square is not None:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.last_move_squares = [move.from_square, move.to_square]
                self.move_history.append(self.board.san(move))
                self.selected_square = None
                self.update_board()

                if self.board.is_checkmate():
                    self.end_game("Checkmate! Player wins!")
                elif self.board.is_stalemate():
                    self.end_game("Stalemate!")
                else:
                    self.make_ai_move()
            else:
                messagebox.showerror("Invalid Move", "This move would put your king in check.")
        elif self.board.piece_at(square) and self.board.piece_at(square).color == self.board.turn:
            self.selected_square = square
            self.highlight_legal_moves(square)

    def highlight_legal_moves(self, square):
        """Highlight legal moves for the selected piece."""
        self.highlighted_squares = [
            move.to_square for move in self.board.legal_moves if move.from_square == square
        ]
        self.update_board()

    def make_ai_move(self):
        """AI makes a move."""
        move = next(iter(self.board.legal_moves))  # Placeholder for AI logic
        self.board.push(move)
        self.last_move_squares = [move.from_square, move.to_square]
        self.move_history.append(self.board.san(move))
        self.update_board()

    def update_board(self):
        """Refresh the chessboard."""
        for row in range(8):
            for col in range(8):
                square = self.squares[row][col]
                square.delete("all")
                color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"
                if chess.square(col, 7 - row) in self.last_move_squares:
                    color = "#00FF00"
                square.config(bg=color)

                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    square.create_text(
                        self.square_size // 2,
                        self.square_size // 2,
                        text=piece.symbol(),
                        font=("Arial", 24),
                    )

    def replay_game(self):
        """Replay the completed game."""
        print("Move History:")
        for move in self.move_history:
            print(move)

    def end_game(self, message):
        """End the game and show a message."""
        messagebox.showinfo("Game Over", message)
        self.board.reset()
        self.update_board()

    def new_game(self):
        """Start a new game."""
        self.board.reset()
        self.move_history.clear()
        self.last_move_squares = []
        self.start_time = time.time()
        self.update_board()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
