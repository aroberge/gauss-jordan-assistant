"""Gauss-Jordan assistant

Requires Python 3.8+ and Rich (https://github.com/willmcgugan/rich)
"""

from fractions import Fraction
import re

from rich import box, print
from rich.console import Console
from rich.markdown import Markdown

from rich.table import Table
from rich.theme import Theme

custom_theme = Theme(
    {
        "markdown.h1.border": "deep_sky_blue1",
        "markdown.h1": "bold yellow",
        "markdown.h2": "bold yellow underline",
        "markdown.item.bullet": "bold spring_green4",
        "markdown.code": "bold yellow",
        "matrix": "deep_sky_blue1",
        "error": "bold red",
        "prompt": "spring_green4",
        "row_operation": "yellow"
    }
)
console = Console(theme=custom_theme)

MATRIX = box.Box(
    """\
╭  ╮
│ ││
│ ││
│ ││
│ ││
│ ││
│ ││
╰  ╯
"""
)

subscript = {
    0: "₀",
    1: "₁",
    2: "₂",
    3: "₃",
    4: "₄",
    5: "₅",
    6: "₆",
    7: "₇",
    8: "₈",
    9: "₉",
}

right_arrow = "🡢"
left_right_arrow = "🡠🡢"

help_fr = """# Liste des instructions

## Création de matrice:

- `mat m x n`
- `mat m x n | p`  (matrice augmentée)

## Opérations élémentaires permises:

- `L_i  <-->  L_j`

- `L_i  +/-  [f] L_j  -->  L_i`    (omettre f=1)

- `f L_i  -->  L_i`

f est un entier ou une fraction.

##  LaTeX

- save_latex nom_de_fichier   # à faire

## Autres:

- `aide` / `help`: imprime ceci
- `quit`[ter] / `exit`: termine les opérations

"""
help = Markdown(help_fr)

re_quit = re.compile(r"(quit|exit).*", re.IGNORECASE)

re_help = re.compile(r"(help|aide).*", re.IGNORECASE)

# mat 3 x 4
re_mat = re.compile(
    r"""^\s* # at line beginning but ignore spaces
        mat
        \s*
        (\d+)   # one or more digits
        \s*
        x
        \s*
        (\d+)
        \s*
        $       # to the end of the line
        """,
    re.VERBOSE | re.IGNORECASE,
)

# mat 3 x 4 | 1
re_aug_mat = re.compile(
    r"""^\s* # at line beginning but ignore spaces
        mat
        \s*
        (\d+)   # one or more digits
        \s*
        x       # x
        \s*
        (\d+)   #
        \s*
        \|      # vertical bar needs escaping
        \s*
        (\d+)   #
        \s*
        $       # to the end of the line
        """,
    re.VERBOSE | re.IGNORECASE,
)

# matches integers or fractions as in 1 22 2/33 , etc.
re_fract = re.compile(r"(-?\d+/?\d*)")  # /?  means zero or 1 /

# We limit the number of rows at 9 or fewer
# The following matches L_2 <--> L_3 and similar operations
re_row_interchange = re.compile(
    r"""^\s*
        L_?    # zero or one underscore
        (\d)   # single digit for row number
        \s*
        <-+>   # one or more - between < >
        \s*
        L_?
        (\d)
        \s*
        $""",
    re.VERBOSE,
)
# This matches something like 1/2 L_3 --> L_3
re_row_scaling = re.compile(
    r"""^\s*
        (\d+/?\d*)  # integer or fraction
        \s*
        L_?(\d)  # original line number
        \s*
        -+>      # arrow -->
        \s*L_?(\d)  # target line number
        \s*$""",
    re.VERBOSE,
)
# This matches something like L_2 - L_3 --> L_2
re_row_lin_combo_1 = re.compile(
    r"""^\s*
        L_?(\d)  # original line
        \s*
        (\+|-)  # plus or minus
        \s*
        L_?(\d)   # other line
        \s*
        -+>   # arrow -->
        \s*
        L_?(\d)  # target line
        \s*$""",
    re.VERBOSE,
)
# This matches something like L_2 + 1/2 L_3 --> L_2
re_row_lin_combo_2 = re.compile(
    r"""^\s*
        L_?(\d)  # original line
        \s*
        (\+|-)  # plus or minus
        \s*
        (\d+/?\d*)  # integer or fraction
        \s*
        L_?(\d)   # other line
        \s*
        -+>  # arrow -->
        \s*
        L_?(\d)  # target line
        \s*$""",
    re.VERBOSE,
)


class Assistant:
    def __init__(self):
        self.prompt = self.default_prompt = "> "
        self.matrix = None
        self.interact()

    def new_matrix(self, nb_rows, nb_cols, nb_augmented_cols=0):
        """Sets the parameters for a new matrix.

        This is called after a command like

            mat m x n
            mat m x n | p

        """
        self.matrix = []
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols
        self.new_matrix_get_rows()

    def new_matrix_get_rows(self):
        """Gets the elements of a new matrix, row by row"""
        self.prompt = f"Entrez une ligne avec {self.total_nb_cols} coefficients : "
        while True:
            done = False
            command = self.user_input(self.prompt)
            if row := re.findall(re_fract, command):
                done = self.new_matrix_add_row(row)
                if done:
                    break
            elif re.search(re_quit, command):
                self.print_error("Entrée des données interrompue.")
                self.matrix = None
                break
            else:
                self.print_error("Format non reconnu.")
        self.prompt = self.default_prompt

    def new_matrix_add_row(self, row):
        """Adds a single row of coefficients for a new matrix"""
        try:
            row = [Fraction(str(entry)) for entry in row]
        except Exception:
            self.print_error("Le format des coefficients soumis est incorrect.")
            return False
        if len(row) == self.nb_cols + self.nb_augmented_cols:
            self.matrix.append(row)
            if len(self.matrix) == self.nb_requested_rows:
                self.nb_rows = self.nb_requested_rows
                return True  # we are done
        else:
            self.print_error("Le nombre de coefficients soumis est incorrect.")
        return False

    def console_print(self):
        """Prints matrix with columns right-aligned, and at least two
           space between each column"""
        col_max_widths = [0 for x in range(self.total_nb_cols)]
        spacing = 2
        padding = spacing * " "  # minimum space between each column
        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        col_format = ["{:>%ds}" % (width + spacing) for width in col_max_widths]

        table = Table(
            show_header=False,
            box=MATRIX,
            pad_edge=False,
            padding=(1, 0),
            collapse_padding=True,
            style="matrix",
        )
        table.add_column(style="white")
        if self.nb_augmented_cols:
            table.add_column(style="white")

        for row in self.matrix:
            main, augmented = "", ""
            for col_idx, column in enumerate(row):
                if col_idx >= self.nb_cols:
                    augmented += col_format[col_idx].format(str(column))
                else:
                    main += col_format[col_idx].format(str(column))
            if self.nb_augmented_cols:
                table.add_row(main + padding, augmented + padding)
            else:
                table.add_row(main + padding)

        console.print(table)

    @staticmethod
    def print_error(text):
        console.print("\n    [error]" + text)
        print()

    @staticmethod
    def user_input(text):
        console.print("[prompt]" + text, end=" ")
        return input()

    def interact(self):
        while True:
            command = self.user_input(self.prompt)
            if re.search(re_quit, command):
                break

            elif re.search(re_help, command):
                console.print(help)
                continue

            elif op := re.search(re_mat, command):
                self.new_matrix(int(op.group(1)), int(op.group(2)))

            elif op := re.search(re_aug_mat, command):
                self.new_matrix(int(op.group(1)), int(op.group(2)), int(op.group(3)))

            elif op := re.search(re_row_interchange, command):
                self.interchange_rows(op.groups())

            elif op := re.search(re_row_scaling, command):
                self.scale_row(op.groups())

            elif op := re.search(re_row_lin_combo_1, command):
                self.linear_combo_1(op.groups())

            elif op := re.search(re_row_lin_combo_2, command):
                self.linear_combo_2(op.groups())

            else:
                self.print_error("Opération non reconnue.")
                continue

            if self.matrix is not None:
                self.console_print()

    def scale_row(self, params):
        """   f L_i  -->  L_i"""
        # TODO: add checks to make sure that row exists
        factor, orig_row, target_row = params
        if orig_row != target_row:
            self.print_error(
                "La multiplication par un scalaire doit transformer la même ligne."
            )
            return
        # Convert from strings to relevant values
        row = int(orig_row) - 1
        if not (0 <= row < len(self.matrix)):
            self.print_error("Cette ligne n'existe pas.")
            return

        factor = Fraction(factor)
        if factor == 0:
            self.print_error("On ne peut pas multiplier une ligne par zéro.")
        self.matrix[row] = [
            factor * self.matrix[row][col] for col in range(len(self.matrix[row]))
        ]

    def interchange_rows(self, params):
        """L_i  <-->  L_j"""
        # TODO: add error checking

        row_1, row_2 = params
        row_1 = int(row_1) - 1
        row_2 = int(row_2) - 1

        if row_1 == row_2:
            self.print_error("Cette opération est sans effet.")
            return
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_1 + 1))
            return
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_2 + 1))
            return

        self.matrix[row_1], self.matrix[row_2] = self.matrix[row_2], self.matrix[row_1]

    def linear_combo_1(self, params):
        """L_i  +/- L_j -->  L_i"""
        # TODO: add error checking
        row_1, op, row_2, target_row = params

        row_1 = int(row_1) - 1
        row_2 = int(row_2) - 1
        target_row = int(target_row) - 1
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_1 + 1))
            return
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_2 + 1))
            return
        if row_1 != target_row:
            self.print_error("Les lignes de départ et d'arrivée doivent être identiques.")
            return
        if row_1 == row_2:
            self.print_error("On ne peut pas utiliser la même ligne dans une seule combinaison linéaire")
            return

        pm = 1 if op == "+" else -1
        self.matrix[row_1] = [
            x + pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]

    def linear_combo_2(self, params):
        """L_i  +/- f L_j -->  L_i"""
        # TODO: add error checking
        row_1, op, factor, row_2, target_row = params
        row_1 = int(row_1) - 1
        row_2 = int(row_2) - 1
        target_row = int(target_row) - 1
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_1 + 1))
            return
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_2 + 1))
            return
        if row_1 != target_row:
            self.print_error("Les lignes de départ et d'arrivée doivent être identiques.")
            return
        if row_1 == row_2:
            self.print_error("On ne peut pas utiliser la même ligne dans une seule combinaison linéaire")
            return

        factor = Fraction(factor)
        if factor == 0:
            self.print_error("Cette opération est sans effet.")
            return

        pm = 1 if op == "+" else -1

        self.matrix[row_1] = [
            x + factor * pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]


def main():
    Assistant()


if __name__ == "__main__":
    main()
