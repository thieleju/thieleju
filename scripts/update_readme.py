import sys


def update_readme(chess_moves, image_url, valid_moves):
    """
    Updates the README.md file with a new table containing the last 10 chess moves and an image.

    Args:
    - chess_moves (str): String containing chess moves separated by '|'.
    - image_url (str): URL of the image to be displayed in the table.
    - valid_moves (str): String containing valid chess moves.
    """
    with open("README.md", "r", encoding="utf8") as file:
        readme = file.readlines()

    # Find start and end of the existing table
    table_start = next((i for i, line in enumerate(readme) if "<table" in line), -1)
    table_end = next((i for i, line in enumerate(readme) if "</table>" in line), -1)

    # Replace the old table with the new table
    if table_start != -1 and table_end != -1:
        new_table = generate_table(chess_moves, valid_moves, image_url).splitlines(keepends=True)
        readme[table_start:table_end + 1] = new_table

    with open("README.md", "w", encoding="utf8") as file:
        file.writelines(readme)


def generate_table(chess_moves, valid_moves, image_url):
    """
    Generates a table containing the last 10 chess moves and an image.

    Args:
    - chess_moves (str): String containing chess moves separated by '|'.
    - valid_moves (str): String containing valid chess moves.
    - image_url (str): URL of the image to be displayed in the table.

    Returns:
    - str: The HTML code for the table.
    """
    table = []

    # Start the table
    table.append('<table border="1" style="width:100%; border-collapse:collapse;">\n')

    # First row: image and placeholder for moves
    table.append('<tr>\n')
    table.append(
        f'  <td><img src="{image_url}" alt="Chessboard" width="600"/></td>\n'
    )
    
    # Placeholder for the last 10 moves
    table.append(
        '  <td>\n'
        '    <h4>Last 10 Moves</h4>\n'
    )
    
    # Format last 10 moves
    moves = chess_moves.split("|")[-10:]  # Select only the last 10 moves
    moves_text = ""
    for move in moves:
        move_number, white_move, black_move = "", "", ""
        
        move_parts = move.split(", ")
        
        if len(move_parts) > 0:
            move_number = move_parts[0].split(".")[0].strip()
            white_move = move_parts[0].split(".")[1].strip() if "." in move_parts[0] else ""

        if len(move_parts) > 1:
            black_move = move_parts[1].strip()

        # Helper function to format move with player link
        def format_move(move):
            parts = move.split(" ")
            move_piece = parts[0] if parts else ""
            player = parts[1] if len(parts) > 1 else ""
            player_link = f'<a href="https://github.com/{player}">{player}</a>' if player else ""
            return f"{move_piece} {player_link}"

        # Format the move into the HTML text
        moves_text += f"{move_number}. {format_move(white_move)} {format_move(black_move)}<br>\n"

    table.append(f'    {moves_text}\n')
    table.append('  </td>\n')
    table.append('</tr>\n')

    # Last row: Legal Moves
    table.append('<tr>\n')
    valid_moves_with_links = [
        f'<a href="https://github.com/thieleju/thieleju/issues/new?body=Click+%27Submit+new+Issue%27+to+play+the+move&labels=chess&title={move}" target="_blank">{move}</a>'
        for move in valid_moves.split(", ")
    ]
    table.append(
        '  <td colspan="2">\n'
        '    <h4>♟️ Click a move to play</h4>\n'
        f'    {", ".join(valid_moves_with_links)}\n'
        '     <br/><br/>\n'
        '  </td>\n'
    )
    table.append('</tr>\n')

    # Close the table
    table.append('</table>\n')

    return "".join(table)


if __name__ == "__main__":
    update_readme(sys.argv[1], sys.argv[2], sys.argv[3])
