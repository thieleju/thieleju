import sys


def update_readme(chess_moves, image_url, issue_link, valid_moves):
    """
    Updates the README.md file with a new table containing the last 10 chess moves and an image.

    Args:
    - chess_moves (str): String containing chess moves separated by '|'.
    - image_url (str): URL of the image to be displayed in the table.
    - issue_link (str): URL to link when the image in the table is clicked.
    - valid_moves (str): String containing valid chess moves.
    """
    with open("README.md", "r", encoding="utf8") as file:
        readme = file.readlines()

    # Find the start and end index of the table
    table_start = next(
        (i for i, line in enumerate(readme) if '<table border="1">' in line), -1
    )
    table_end = next((i for i, line in enumerate(readme) if "</table>" in line), -1)

    if table_start != -1 and table_end != -1:
        new_table = [
            '<table border="1">\n',
            f'<th rowspan="20"><a href="{issue_link}"><img width="480" src="{image_url}" /></a></th>\n',
            '<th colspan="3">Last 10 moves</th>\n',
            "<tr>\n<th>#</th>\n<th>White</th>\n<th>Black</th>\n</tr>\n",
        ]

        moves = chess_moves.split("|")[-10:]  # Select only the last 10 moves
        for move in moves:
            move_parts = move.split(", ")
            move_number = move_parts[0].split(".")[0]
            if len(move_parts) == 2:
                white_move, black_move = (
                    move_parts[0].split(".")[1].strip(),
                    move_parts[1],
                )
            else:
                white_move, black_move = move_parts[0].split(".")[1].strip(), ""

            white_parts, black_parts = white_move.split(" "), black_move.split(" ")
            white_username = f'<a href="https://github.com/{white_parts[1][1:]}">{white_parts[1]}</a>'
            black_username = (
                f'<a href="https://github.com/{black_parts[1][1:]}">{black_parts[1]}</a>'
                if len(black_parts) > 1
                else ""
            )

            new_table.append(
                f"<tr>\n<td>{move_number}</td>\n<td>{white_parts[0]} {white_username}</td>\n<td>{black_parts[0]} {black_username}</td>\n</tr>\n"
            )

        new_table.append("</table>\n")

        # Update the README content
        readme[table_start : table_end + 1] = new_table

        # Update the chess game link and legal moves in the README
        for i, line in enumerate(readme):
            if "### ✨ Play chess by commenting on [this issue!]" in line:
                readme[
                    i
                ] = f"### ✨ Play chess by commenting on [this issue!]({issue_link}) (WIP)\n"

            if "### ♟️ Legal Moves" in line:
                readme[i] = "### ♟️ Legal Moves\n"
                # delete everything after ### legal moves
                readme[i + 1 :] = []
                # add legal moves
                readme.extend([f"> {line}" for line in valid_moves.split("|")])

        with open("README.md", "w", encoding="utf8") as file:
            file.writelines(readme)
    else:
        print("Could not find table in README.md")


def generate_table(chess_moves, image_url, image_link):
    """
    Generates a table containing the last 10 chess moves and an image.

    Args:
    - chess_moves (str): String containing chess moves separated by '|'.
    - image_url (str): URL of the image to be displayed in the table.
    - image_link (str): URL to link when the image in the table is clicked.

    Returns:
    - str: The HTML code for the table.
    """
    table = []

    table.append('<table border="1">\n')
    table.append(
        f'<th rowspan="20"><a href="{image_link}"><img src="{image_url}" /></a></th>\n'
    )
    table.append('<th colspan="3">Last 10 moves</th>\n')
    table.append("<tr>\n<th>#</th>\n<th>White</th>\n<th>Black</th>\n</tr>\n")

    moves = chess_moves.split("|")[-10:]  # Select only the last 10 moves
    for move in moves:
        move_parts = move.split(", ")
        move_number = move_parts[0].split(".")[0]
        white_move = move_parts[0].split(".")[1].strip()
        black_move = move_parts[1]
        table.append(
            f"<tr>\n<td>{move_number}</td>\n<td>{white_move}</td>\n<td>{black_move}</td>\n</tr>\n"
        )

    table.append("</table>\n")

    return "".join(table)


if __name__ == "__main__":
    update_readme(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
