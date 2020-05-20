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

dark_theme = Theme(  # suitable on a dark background
    {
        "markdown.h1.border": "deep_sky_blue1",
        "markdown.h1": "bold yellow",
        "markdown.h2": "bold yellow underline",
        "markdown.item.bullet": "bold spring_green4",
        "markdown.code": "bold yellow",
        "matrix": "deep_sky_blue1",
        "error": "bold red",
        "prompt": "spring_green4",
        "row_operation": "yellow",
    }
)

console = Console(theme=dark_theme)

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

# fmt: off
subscript = {0: "₀", 1: "₁", 2: "₂", 3: "₃", 4: "₄",
             5: "₅", 6: "₆", 7: "₇", 8: "₈", 9: "₉"}
# fmt: on

right_arrow = "🡢"
left_right_arrow = "🡠🡢"

help_fr = """# Liste des instructions

Ci-dessous, `i, j, m, n, p` sont des entiers et `f` est soit
un entier ou soit un nombre rationnel  (`m/n`).

- `mat m x n`      : création d'une matrice
- `mat m x n | p`  : création d'une matrice augmentée
- `L_i  <-->  L_j`              : échange de lignes
- `L_i  +/-  [f] L_j  -->  L_i` : combinaison linéaire (omettre f si f=1)
- `f L_i  -->  L_i`             : multiplication par un scalaire

- save_latex nom_de_fichier   # à faire
- `aide` / `help`      : imprime ceci
- `quit`[ter] / `exit` : termine les opérations

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

    def interact(self):
        """Command interpreter"""
        while True:
            command = self.user_input()
            if re.search(re_quit, command):
                break

            elif re.search(re_help, command):
                console.print(help, "\n")
                continue

            elif op := re.search(re_mat, command):
                self.new_matrix(int(op.group(1)), int(op.group(2)))

            elif op := re.search(re_aug_mat, command):
                self.new_matrix(int(op.group(1)), int(op.group(2)), int(op.group(3)))

            elif op := re.search(re_row_interchange, command):
                if not self.interchange_rows(int(op.group(1)), int(op.group(2))):
                    continue

            elif op := re.search(re_row_scaling, command):
                if not self.scale_row(
                    Fraction(op.group(1)), int(op.group(2)), int(op.group(3))
                ):
                    continue

            elif op := re.search(re_row_lin_combo_1, command):
                if not self.linear_combo_1(
                    int(op.group(1)), op.group(2), int(op.group(3)), int(op.group(4)),
                ):
                    continue

            elif op := re.search(re_row_lin_combo_2, command):
                if not self.linear_combo_2(
                    int(op.group(1)),
                    op.group(2),
                    Fraction(op.group(3)),
                    int(op.group(4)),
                    int(op.group(5)),
                ):
                    continue

            else:
                self.print_error("Opération non reconnue.")
                continue

            if self.matrix is not None:
                self.console_print()

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
        """Command interpreter active when a new matrix is created.
           Gets the elements of a new matrix, row by row."""
        self.prompt = f"Entrez une ligne avec {self.total_nb_cols} coefficients : "
        while True:
            done = False
            command = self.user_input()
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
        """Prints matrix with columns right-aligned, and some minimal
           spacing between between each column.
        """

        coeff_matrix, augmented = self.format_matrix()

        table = Table(
            show_header=False,
            box=MATRIX,
            padding=(0, 0),
            style="matrix",
            pad_edge=False,
        )
        table.add_column()
        if augmented is None:
            table.add_row(coeff_matrix)
        else:
            table.add_column()
            table.add_row(coeff_matrix, augmented)

        console.print(table)

    def format_matrix(self, spacing=2):
        """Formats matrix with columns right-aligned, and minimal number
           of spaces between each column.
        """
        ##################
        # Using rich, it would be easy to produce a grid of numbers
        # aligned and spaced "just right".  However, I want to have
        # the flexibility to style differently certain matrix elements,
        # such as the leading zeros for a given row, or the pivots.
        # For this reason, I use a more complex, but potentially
        # versatile approach.
        ##################
        col_max_widths = [0 for x in range(self.total_nb_cols)]
        padding = spacing * " "  # minimum space between each column

        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        col_format = ["{:>%ds}" % (width + spacing) for width in col_max_widths]

        coeff_matrix = Table().grid()

        coeff_matrix.add_column(style="white")

        for row_idx, row in enumerate(self.matrix):
            content = ""
            for col_idx, column in enumerate(row[0 : self.nb_cols]):
                content += col_format[col_idx].format(str(column))
            if row_idx != 0:
                coeff_matrix.add_row(" ")
            coeff_matrix.add_row(content + padding)

        if not self.nb_augmented_cols:
            return coeff_matrix, None

        augmented = Table().grid()
        augmented.add_column(style="white")

        for row_idx, row in enumerate(self.matrix):
            content = ""
            for col_idx, column in enumerate(row[self.nb_cols :]):
                content += col_format[col_idx].format(str(column))
            if row_idx != 0:
                augmented.add_row(" ")
            augmented.add_row(content + padding)

        return coeff_matrix, augmented

    @staticmethod
    def print_error(text):
        console.print("\n    [error]" + text, "\n")
        print()

    def user_input(self):
        return console.input("[prompt]" + self.prompt)

    def scale_row(self, factor, row, target_row):
        """f R_i  -->  R_i

           factor = f
           row = i
           target_row should be equal to row

           Returns True if the operation could be performed, False otherwise.
        """
        row = row - 1
        target_row = target_row - 1
        if not self.valid_scale_row(row, target_row, factor):
            return False

        self.matrix[row] = [
            factor * self.matrix[row][col] for col in range(len(self.matrix[row]))
        ]
        return True

    def valid_scale_row(self, row, target_row, factor):
        """Verifies that parameters in scaling transformation are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if row != target_row:
            self.print_error(
                "La multiplication par un scalaire doit transformer la même ligne."
            )
            return False
        if not (0 <= row < len(self.matrix)):
            self.print_error("Cette ligne n'existe pas.")
            return False
        if factor == 0:
            self.print_error("On ne peut pas multiplier une ligne par zéro.")
            return False
        return True

    def interchange_rows(self, row_1, row_2):
        """R_i <--> R_j

           row_1 = i
           row_2 = j

           Returns True if the operation could be performed, False otherwise.
        """
        row_1 = row_1 - 1
        row_2 = row_2 - 1
        if not self.valid_interchange_rows(row_1, row_2):
            return False

        self.matrix[row_1], self.matrix[row_2] = self.matrix[row_2], self.matrix[row_1]
        return True

    def valid_interchange_rows(self, row_1, row_2):
        """Verifies that parameters in row exchange transformation are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if row_1 == row_2:
            self.print_error("Cette opération est sans effet.")
            return False
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_1 + 1))
            return False
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_2 + 1))
            return False
        return True

    def linear_combo_1(self, row_1, op, row_2, target_row):
        """R_i +/- R_j --> R_i

           row_1 = i
           op = +/-
           row_2 = j
           target_row should be the same as row_1

           Returns True if the operation could be performed, False otherwise.
        """
        row_1 = row_1 - 1
        row_2 = row_2 - 1
        target_row = target_row - 1
        if not self.validate_linear_combo_1(row_1, row_2, target_row):
            return False

        pm = 1 if op == "+" else -1
        self.matrix[row_1] = [
            x + pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]
        return True

    def validate_linear_combo_1(self, row_1, row_2, target_row):
        """Verifies that parameters in linear combination '1' are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_1 + 1))
            return False
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error("La ligne %s n'existe pas." % (row_2 + 1))
            return False
        if row_1 != target_row:
            self.print_error(
                "Les lignes de départ et d'arrivée doivent être identiques."
            )
            return False
        if row_1 == row_2:
            self.print_error(
                "On ne peut pas utiliser la même ligne dans une seule combinaison linéaire"
            )
            return False
        return True

    def linear_combo_2(self, row_1, op, factor, row_2, target_row):
        """R_i  +/- f R_j -->  R_i

           row_1 = i
           op = +/-
           factor = f
           row_2 = j
           target_row should be the same as row_1

           Returns True if the operation could be performed, False otherwise.
        """
        row_1 = row_1 - 1
        row_2 = row_2 - 1
        target_row = target_row - 1

        if not self.validate_linear_combo_2(row_1, row_2, target_row, factor):
            return False

        pm = 1 if op == "+" else -1
        self.matrix[row_1] = [
            x + factor * pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]
        return True

    def validate_linear_combo_2(self, row_1, row_2, target_row, factor):
        """Verifies that parameters in linear combination '2' are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if not self.validate_linear_combo_1(row_1, row_2, target_row):
            return False
        if factor == 0:
            self.print_error("Cette opération est sans effet.")
            return False
        return True


def main():
    Assistant()


if __name__ == "__main__":
    main()
