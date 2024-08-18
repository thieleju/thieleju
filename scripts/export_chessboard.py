import datetime
import os
import sys

import chess
import chess.pgn
from PIL import Image, ImageDraw, ImageFont

# Settings for the chessboard
settings = {
    "width": 500,
    "height": 500,
    "styling": {
        "background": "#52796f",
        "dark": "#52796f",
        "light": "#cad2c5",
        "border_size": 2,
        "border_color": "#161618",
        "annotation_color": "#161618",
        # hardcoded until I figure out how to calculate this
        "annotation_offset_numbers": 28,
        "annotation_offset_letters": 20,
    },
    "pieces_path": "pieces/",
    "games_dir": "games/",
    "output_path": "chessboard.png",
    "piece_size_ratio": 0.125,
    "piece_offset_ratio": 0.5,
    "env_file": ".env",
    "start_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
}

settings["cell_size"] = min(settings["width"], settings["height"]) // 8


def get_piece_path(piece):
    """Returns the path of the chess piece image file based on its type and color.

    Args:
        piece (chess.Piece): The chess piece object.

    Returns:
        str: The file path of the chess piece image.
    """
    color = "b" if piece.color == chess.BLACK else "w"
    symbol = piece.symbol().lower()
    return f"{settings['pieces_path']}{color}{symbol}.png"


def resize_piece(piece_image):
    """Resizes the chess piece image to match the cell size.

    Args:
        piece_image (PIL.Image.Image): The image of the chess piece.

    Returns:
        PIL.Image.Image: The resized chess piece image.
    """
    return piece_image.resize((settings["cell_size"], settings["cell_size"]))


def create_chessboard():
    """Creates a chessboard image."""
    image = Image.new(
        "RGB",
        (settings["width"], settings["height"]),
        settings["styling"]["background"],
    )
    draw = ImageDraw.Draw(image)
    return image, draw


def draw_board_squares(draw):
    """Draws the squares of the chessboard."""
    for i in range(8):
        for j in range(8):
            x1, y1 = i * settings["cell_size"], j * settings["cell_size"]
            x2, y2 = x1 + settings["cell_size"], y1 + settings["cell_size"]
            color = (
                settings["styling"]["dark"]
                if (i + j) % 2 == 0
                else settings["styling"]["light"]
            )
            draw.rectangle((x1, y1, x2, y2), fill=color)


def place_pieces(image, board, is_white_bottom):
    """Places the chess pieces on the board based on the position of the bottom player.

    Args:
        image (PIL.Image.Image): The chessboard image.
        board (chess.Board): The chess board object.
        is_white_bottom (bool): Flag indicating if the white player is at the bottom.
    """
    for i in range(8):
        for j in range(8):
            square = (
                chess.square(i, 7 - j) if is_white_bottom else chess.square(7 - i, j)
            )
            piece = board.piece_at(square)

            if piece is None:
                continue

            piece_path = get_piece_path(piece)

            if not os.path.exists(piece_path):
                continue

            piece_image = Image.open(piece_path)
            piece_image = piece_image.convert("RGBA")
            piece_image = resize_piece(piece_image)

            image_width, image_height = piece_image.size
            offset_x = (settings["cell_size"] - image_width) // 2
            offset_y = (settings["cell_size"] - image_height) // 2

            x1, y1 = i * settings["cell_size"], j * settings["cell_size"]
            draw_x = x1 + offset_x
            draw_y = (
                y1 + offset_y
                if (piece.color == chess.WHITE and is_white_bottom)
                or (piece.color == chess.BLACK and not is_white_bottom)
                else y1 + settings["cell_size"] - offset_y - image_height
            )
            image.paste(piece_image, (draw_x, draw_y), piece_image)


def add_border(draw):
    """Adds a border to the chessboard."""
    draw.rectangle(
        (0, 0, settings["width"] - 1, settings["height"] - 1),
        outline=settings["styling"]["border_color"],
        width=settings["styling"]["border_size"],
    )


def add_annotations(draw, is_white_bottom):
    """Adds annotations (letters and numbers) to the chessboard based on the position
    of the bottom player.

    Args:
        draw (PIL.ImageDraw.Draw): The drawing context.
        is_white_bottom (bool): Flag indicating if the white player is at the bottom.
    """
    for i in range(8):
        idx = i if is_white_bottom else 7 - i
        if idx % 2 == 0:
            text_color = settings["styling"]["dark"]
            bg_color = settings["styling"]["light"]
        else:
            text_color = settings["styling"]["light"]
            bg_color = settings["styling"]["dark"]

        draw.text(
            (
                i * settings["cell_size"]
                + settings["cell_size"] // 2
                + settings["styling"]["annotation_offset_letters"],
                settings["height"] - 20,
            ),
            chr(97 + i) if is_white_bottom else chr(97 + 7 - i),
            fill=text_color if is_white_bottom else bg_color,
            font=ImageFont.load_default(),
        )
        draw.text(
            (
                5,
                i * settings["cell_size"]
                + settings["cell_size"] // 2
                - settings["styling"]["annotation_offset_numbers"],
            ),
            str(8 - i) if is_white_bottom else str(i + 1),
            fill=bg_color if is_white_bottom else text_color,
            font=ImageFont.load_default(),
        )


def export_chessboard(board, is_white_bottom=True, custom_path=None):
    """Generates and exports a chessboard image based on the provided board
    and the position of the bottom player.

    Args:
        board (chess.Board): The chess board object.
        is_white_bottom (bool, optional): Flag indicating if the white player
        is at the bottom. Defaults to True.
    """
    image, draw = create_chessboard()

    if not is_white_bottom:
        flipped_board = chess.Board(board.fen())
        flipped_board.turn = chess.BLACK
        board = flipped_board

    draw_board_squares(draw)
    place_pieces(image, board, is_white_bottom)
    add_border(draw)
    add_annotations(draw, is_white_bottom)

    if custom_path:
        image.save(custom_path)
    else:
        image.save(settings["output_path"])


def make_move(board, san_move):
    """Executes a move on the board in Standard Algebraic Notation (SAN) if it's legal.

    Args:
        board (chess.Board): The chess board object.
        san_move (str): The move to be executed in SAN format (e.g., "e4").

    Returns:
        bool: True if the move was executed successfully, False otherwise.
    """
    try:
        parsed_move = board.parse_san(san_move)
        if not parsed_move in board.legal_moves:
            return False

        board.push(parsed_move)
        return True

    except ValueError:
        return False


def reset_game(game_number):
    """Resets the game to the starting position."""
    board = chess.Board(settings["start_fen"])

    initialize_pgn(game_number)
    export_chessboard(board)

    save_env_variables_to_file(
        GAME_STATUS="in_progress",
        MOVE_STATUS="valid",
        WHICH_TURN="white",
        GAME_NUMBER=game_number,
        VALID_MOVES=", ".join([board.san(move) for move in board.legal_moves]),
        GAME_HISTORY=""
    )

def get_valid_moves_from_fen(fen):
    """Gets the valid moves from a FEN string.

    Args:
        fen (str): The FEN string.

    Returns:
        list: The list of valid moves.
    """
    board = chess.Board(fen)
    return [board.san(move) for move in board.legal_moves]


def game_end_status(board):
    """Returns the status of the game if it has ended.

    Args:
        board (chess.Board): The chess board object.

    Returns:
        str or None: The status of the game ('white_wins', 'black_wins', 'draw',
        'stalemate', 'insufficient_material', 'threefold_repetition') or "in_progress"
        if the game is ongoing.
    """
    if board.is_game_over():
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return "black_wins"
            return "white_wins"
        if board.is_stalemate():
            return "stalemate"
        if board.is_insufficient_material():
            return "insufficient_material"
        return "draw"

    if board.can_claim_threefold_repetition():
        return "threefold_repetition"

    return "in_progress"


def initialize_pgn(game_number):
    """Initializes the PGN file with default headers for a new game."""
    try:
        game = chess.pgn.Game()
        game.headers["Event"] = "Chess Game"
        game.headers["Site"] = "https://github.com/thieleju"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = f"Game {game_number}"
        game.headers["White"] = "Player 1"
        game.headers["Black"] = "Player 2"

        # create directory if it doesn't exist
        if not os.path.exists(settings["games_dir"]):
            os.makedirs(settings["games_dir"])

        # creat directory for game if it doesn't exist
        if not os.path.exists(f'{settings["games_dir"]}game{game_number}'):
            os.makedirs(f'{settings["games_dir"]}game{game_number}')

        path = get_pgn_path(game_number)
        with open(path, "w", encoding="utf8") as file:
            file.write(str(game))

        print(f"PGN file initialized for game {game_number} at {path}")
    except Exception as e:
        print(f"Error initializing PGN file: {e}")


def update_pgn_with_move(san_move, username, game_number):
    """Updates the PGN file with the provided move in SAN notation and the
    username as a comment for the move.

    Args:
        san_move (str): The move in Standard Algebraic Notation (SAN).
        username (str): The username of the player making the move.
        game_number (int): The number of the game to update.
    """
    try:
        path = get_pgn_path(game_number)

        if not os.path.exists(path):
            initialize_pgn(game_number)

        print(f"Updating PGN file for game {game_number} at {path}")
        with open(path, "r+", encoding="utf8") as file:
            game = chess.pgn.read_game(file)
            if game is None:
                file.seek(0)
                file.truncate()
                initialize_pgn(game_number)
                file.seek(0)
                game = chess.pgn.read_game(file)

            node = game
            while node.variations:
                node = node.variation(0)

            parsed_move = node.board().parse_san(san_move)
            node = node.add_variation(parsed_move)
            node.comment = username

            file.seek(0)
            file.write(str(game))
            file.truncate()
    except Exception as e:
        print(f"Error updating PGN: {e}")


def load_game_from_pgn(game_number):
    """Loads a game from a PGN file and returns the board object.

    Args:
        game_number (int): The number of the game to load.

    Returns:
        chess.Board: The chess board object representing the game.
    Raises:
        ValueError: If the PGN content is invalid.
    """
    try:
        path = get_pgn_path(game_number)
        if not os.path.exists(path):
            initialize_pgn(game_number)

        with open(path, "r", encoding="utf8") as file:
            game = chess.pgn.read_game(file)
            if game is None:  # Invalid PGN content
                raise ValueError("Invalid PGN content")
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
            return board
    except Exception as e:
        print(f"Error loading from PGN: {e}")
        return chess.Board()


def get_moves_and_users_from_pgn(game_number):
    """
    Returns the moves and users from the PGN file.

    Args:
        game_number (int): The number of the game to load.

    Returns:
        list: The list of moves in the format (move_number, san_move, username)
    """
    moves_with_users = []
    try:
        path = get_pgn_path(game_number)
        with open(path, "r", encoding="utf8") as file:
            game = chess.pgn.read_game(file)
            node = game
            move_number = 0

            while node:
                comment = node.comment
                if comment:
                    move = node.move
                    san_move = node.parent.board().san(move)
                    moves_with_users.append((move_number, san_move, comment))
                if node.board().turn == chess.WHITE:
                    move_number += 1
                node = node.next()
    except Exception as e:
        print(f"Error loading from PGN: {e}")
        sys.exit(1)
    return moves_with_users


def format_moves(moves_list):
    """
    Formats the moves in the following format:

    Args:
        moves_list (list): The list of moves in the format (move_number, san_move, username)

    Returns:
        str: The formatted moves in the format:
            1. e4 @user1, e5 @user2
            2. Nf3 @user3, Nc6 @user4
    """
    move_numbers = set(move[0] for move in moves_list)
    formatted_moves = []

    for move_number in move_numbers:
        moves_with_same_number = [move for move in moves_list if move[0] == move_number]
        moves_text = ", ".join(
            [f"{move[1]} @{move[2]}" for move in moves_with_same_number]
        )
        formatted_moves.append(f"{move_number}. {moves_text}")

    return "|".join(formatted_moves)


def save_env_variables_to_file(**kwargs):
    """Saves environment variables to a file.

    Args:
        **kwargs: Keyword arguments representing environment variables.
                  Example: GAME_STATUS='in_progress', MOVE_STATUS='valid'
    """
    try:
        file_path = settings["env_file"]
        with open(file_path, "w", encoding="utf8") as env_file:
            for key, value in kwargs.items():
                env_file.write(f"{key}={value}\n")
                print(f"{key}\t", value)
        print(f"Environment variables saved to {file_path} successfully.")
    except Exception as e:
        print(f"Error saving environment variables: {e}")


def save_board_image(board, username, game_number):
    """Saves the chessboard image in the game directory and names it based
    on the move number and player.

    Args:
        board (chess.Board): The chess board object.
        username (str): The username of the player making the move.
        game_number (int): The number representing the game.
    """
    games_dir_settings = settings["games_dir"]
    game_dir = f"{games_dir_settings}/game{game_number}"

    # create games directory subfolder
    os.makedirs(game_dir, exist_ok=True)

    # Get the correct orientation of the board based on the player
    was_whites_turn = board.turn == chess.WHITE

    # Export the chessboard image with the appropriate orientation to the default location
    export_chessboard(board, was_whites_turn)

    # Define the filename based on move number and player
    if was_whites_turn:
        move_number = board.fullmove_number - 1
    else:
        move_number = board.fullmove_number
    
    player = "0" if not was_whites_turn else "1"
    move_number = str(move_number).zfill(3)
    file_name = f"move-{move_number}-{player}-{username}.png"

    # Copy the generated image to the game directory
    image_path = os.path.join(game_dir, file_name)

    # generate second board image if it was black's turn for later gifs
    # or copy already created image to image_path
    if not was_whites_turn:
        export_chessboard(board, True, custom_path=image_path)
    else:
        Image.open(settings["output_path"]).save(image_path)


def create_gif_from_images(input_folder, output_gif):
    """Creates a GIF from images in a folder.

    Args:
        input_folder (str): The path to the folder containing images.
        output_gif (str): The path to save the output GIF.
    """
    images = []
    # Load all images in the folder
    for filename in sorted(os.listdir(input_folder)):
        if filename.startswith("move") and filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            images.append(Image.open(image_path))

    # Save as a GIF
    images[0].save(
        output_gif, save_all=True, append_images=images[1:], duration=800, loop=1
    )


def get_pgn_path(game_number):
    """Returns the path to the PGN file for the given game number.

    Args:
        game_number (int): The number representing the game.

    Returns:
        str: The path to the PGN file.
    """
    return f'{settings["games_dir"]}game{game_number}/pgn.txt'


def generate_images_for_all_moves(game_number):
    """Generates images for all moves in the game.

    Args:
        game_number (int): The number representing the game.
    """
    board = chess.Board()
    moves_with_users = get_moves_and_users_from_pgn(game_number)

    print(moves_with_users)
    for move_number, san_move, username in moves_with_users:
        print(move_number, san_move, username)
        make_move(board, san_move)

        was_whites_turn = board.turn == chess.WHITE
        game_dir = f'{settings["games_dir"]}game{game_number}'
        player = "0" if not was_whites_turn else "1"
        move_number_2 = str(move_number).zfill(3)
        file_name = f"move-{move_number_2}-{player}-{username}.png"

        print(file_name)
        image_path = os.path.join(game_dir, file_name)

        export_chessboard(board, True, custom_path=image_path)


if __name__ == "__main__":
    # If one argument is passed, reset the game and set game number to parameter
    if len(sys.argv) == 2:
        reset_game(sys.argv[1])
        sys.exit(0)

    MOVE = sys.argv[1]
    USERNAME = sys.argv[2]

    # Get the game number from the /games directory
    GAME_NUMBER = 0
    for root, dirs, files in os.walk(settings["games_dir"]):
        for dir in dirs:
            if dir.startswith("game"):
                GAME_NUMBER = int(dir[4:])

    # initialize the board with the moves from the pgn
    current_board = load_game_from_pgn(GAME_NUMBER)

    # make move based on the parameter passed
    IS_MOVE_VALID = make_move(current_board, MOVE)

    MOVES = ", ".join([current_board.san(move) for move in current_board.legal_moves])
    TURN = "white" if current_board.turn == chess.WHITE else "black"
    MOVE_STATUS = "valid" if IS_MOVE_VALID else "invalid"
    GAME_STATUS = game_end_status(current_board)

    # save PGN to file
    if IS_MOVE_VALID:
        update_pgn_with_move(MOVE, USERNAME, GAME_NUMBER)

    game_history = get_moves_and_users_from_pgn(GAME_NUMBER)
    GAME_HISTORY_FORMATTED = format_moves(game_history)

    # set the environment variables
    save_env_variables_to_file(
        GAME_STATUS=GAME_STATUS,
        MOVE_STATUS=MOVE_STATUS,
        WHICH_TURN=TURN,
        GAME_NUMBER=GAME_NUMBER,
        VALID_MOVES=MOVES,
        GAME_HISTORY=GAME_HISTORY_FORMATTED,
    )

    # Export the chessboard image
    if IS_MOVE_VALID:
        save_board_image(current_board, USERNAME, GAME_NUMBER)

        # create gif from images
        base_path = settings["games_dir"] + f"/game{GAME_NUMBER}"
        create_gif_from_images(
            base_path,
            f"{base_path}/game.gif",
        )
