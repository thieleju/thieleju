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
        "background": "#d18b47",
        "dark": "#b58863",
        "light": "#f0d9b5",
        "border_size": 2,
        "border_color": "#161618",
        "annotation_color": "#161618",
        # hardcoded until I figure out how to calculate this
        "annotation_offset_numbers": 28,
        "annotation_offset_letters": 20,
    },
    "pieces_path": "images/pieces/",
    "output_path": "images/chessboard.png",
    "piece_size_ratio": 0.125,
    "piece_offset_ratio": 0.5,
    "fen_file_path": "fen.txt",
    "pgn_file_path": "pgn.txt",
    "start_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1",
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
    """Adds annotations (letters and numbers) to the chessboard based on the position of the bottom player.

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



def save_fen_to_file(board, file_path):
    """Saves the FEN of the board to a text file.

    Args:
        board (chess.Board): The chess board object.
        file_path (str): The file path to save the FEN to.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(board.fen())


def load_fen_from_file(file_path):
    """Loads the FEN from a text file. If the file doesn't exist, writes the start FEN to the file.

    Args:
        file_path (str): The file path to load the FEN from.

    Returns:
        str: The FEN string loaded from the file or the start FEN if the file doesn't exist.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(settings["start_fen"])
        return settings["start_fen"]

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def export_chessboard(board, is_white_bottom=True):
    """Generates and exports a chessboard image based on the provided board and the position of the bottom player.

    Args:
        board (chess.Board): The chess board object.
        is_white_bottom (bool, optional): Flag indicating if the white player is at the bottom. Defaults to True.
    """
    image, draw = create_chessboard()

    is_white_bottom = board.turn == chess.WHITE

    if not is_white_bottom:
        flipped_board = chess.Board(board.fen())
        flipped_board.turn = chess.BLACK
        board = flipped_board

    draw_board_squares(draw)
    place_pieces(image, board, is_white_bottom)
    add_border(draw)
    add_annotations(draw, is_white_bottom)

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
        if parsed_move in board.legal_moves:
            board.push(parsed_move)
            print(
                f"{'white' if board.turn != chess.WHITE else 'black'}: move {san_move}"
            )
            return True

        print("Invalid move!")
        sys.exit(1)
    except ValueError:
        print("Invalid move format!")
        sys.exit(1)


def reset_game():
    """Resets the game to the starting position."""
    board = chess.Board(settings["start_fen"])

    save_fen_to_file(board, settings["fen_file_path"])
    export_chessboard(board)


if __name__ == "__main__":
    # If no parameter is passed, reset the game
    if len(sys.argv) < 2:
        reset_game()
        sys.exit(0)

    # Load the FEN from the fen.txt file
    loaded_fen = load_fen_from_file(settings["fen_file_path"])

    # initialize the board with the loaded FEN
    current_board = chess.Board(loaded_fen)

    # make move based on the parameter passed
    comment_body = sys.argv[1]
    make_move(current_board, comment_body)

    # save the FEN to the fen.txt file
    save_fen_to_file(current_board, settings["fen_file_path"])

    # Export the chessboard image
    export_chessboard(current_board)
