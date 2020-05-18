"""Gauss-Jordan assistant

Requires Python 3.8+ and Rich (https://github.com/willmcgugan/rich)
"""

from fractions import Fraction
import re

from rich import box

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
from rich.table import Table
from rich.console import Console

console = Console()


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


help = """Commandes reconnues

Création de matrice:

    mat m x n
    mat m x n | p  (matrice augmentée)

Opérations élémentaires permises:

   L_i  <-->  L_j

   L_i  +/-  [f] L_j  -->  L_i    (omettre f=1)

   f L_i  -->  L_i

   (f est un entier ou une fraction.)

save_latex nom_de_fichier   # à faire
save_beamer nom_de_fichier  # à faire
"""


class Assistant:
    def __init__(self):
        self.prompt = self.default_prompt = "> "
        self.matrix = None
        self.interact()

    def new_matrix(self, nb_rows, nb_cols, nb_augmented_cols=0):
        """Sets the parameters for a new matrix"""
        self.matrix = []
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols
        self.new_matrix_get_rows()

    def new_matrix_get_rows(self):
        """Gets the coefficients of a new matrix"""
        self.prompt = f"Entrez une ligne avec ({self.total_nb_cols} nombres) > "
        while True:
            done = False
            command = input(self.prompt)
            if row := re.findall(re_fract, command):
                done = self.new_matrix_add_row(row)
                if done:
                    break
            else:
                print("Format non reconnu.")
        self.prompt = self.default_prompt

    def new_matrix_add_row(self, row):
        """Adds a single row of coefficients for a new matrix"""
        try:
            row = [Fraction(str(entry)) for entry in row]
        except Exception:
            print("Le format des nombres soumis est incorrect.")
            return False
        if len(row) == self.nb_cols + self.nb_augmented_cols:
            self.matrix.append(row)
            if len(self.matrix) == self.nb_requested_rows:
                self.nb_rows = self.nb_requested_rows
                return True  # we are done
        else:
            print("Le nombre de coefficients soumis est incorrect.")
        return False

    def console_print(self):
        """Prints matrix with columns right-aligned, and at least two
           space between each column"""
        col_max_widths = [0 for x in range(self.total_nb_cols)]
        spacing = 2  # minimum space between each column
        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        col_format = ["{:>%ds}" % (width + spacing) for width in col_max_widths]

        # print()
        # for row in self.matrix:
        #     for col_idx, column in enumerate(row):
        #         if col_idx == self.nb_cols:
        #             print("  |", end="")
        #         print(col_format[col_idx].format(str(column)), end="")
        #     print()
        # print()

        table = Table(
            show_header=False,
            box=MATRIX,
            pad_edge=False,
            padding=(0, 0),
            style="deep_sky_blue1",
        )
        table.add_column(style="white")
        if not self.nb_augmented_cols:
            for row in self.matrix[:-1]:
                current_row = ""
                for col_idx, column in enumerate(row):
                    current_row += col_format[col_idx].format(str(column))
                table.add_row(current_row + spacing * " ")
                table.add_row()  # extra spacing between rows

            current_row = ""
            row = self.matrix[-1]
            for col_idx, column in enumerate(row):
                current_row += col_format[col_idx].format(str(column))
            table.add_row(current_row + spacing * " ")
        else:
            table.add_column(style="white")
            for row in self.matrix[:-1]:
                left, right = "", ""
                for col_idx, column in enumerate(row):
                    if col_idx >= self.nb_cols:
                        right += col_format[col_idx].format(str(column))
                    else:
                        left += col_format[col_idx].format(str(column))
                table.add_row(left + spacing * " ", right + spacing * " ")
                table.add_row()
            row = self.matrix[-1]
            left, right = "", ""
            for col_idx, column in enumerate(row):
                if col_idx >= self.nb_cols:
                    right += col_format[col_idx].format(str(column))
                else:
                    left += col_format[col_idx].format(str(column))
            table.add_row(left + spacing * " ", right + spacing * " ")

        console.print(table)

    def interact(self):
        while True:
            command = input(self.prompt)
            if re.search(re_quit, command):
                break

            elif re.search(re_help, command):
                print(help)
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
                print("Opération non reconnue.")
                continue

            if self.matrix is not None:
                self.console_print()

    def scale_row(self, params):
        """   f L_i  -->  L_i"""
        # TODO: add checks to make sure that row exists
        factor, orig_row, target_row = params
        if orig_row != target_row:
            print("La multiplication par un scalaire doit transformer la même ligne.")
            return
        print(
            f"Multiplication par un scalaire: {factor} L_{orig_row}  -->  L_{orig_row}"
        )

        # Convert from strings to relevant values
        row = int(orig_row) - 1
        factor = Fraction(factor)
        self.matrix[row] = [
            factor * self.matrix[row][col] for col in range(len(self.matrix[row]))
        ]

    def interchange_rows(self, params):
        """L_i  <-->  L_j"""
        # TODO: add error checking

        row_1, row_2 = params

        row_1 = int(row_1) - 1
        row_2 = int(row_2) - 1
        self.matrix[row_1], self.matrix[row_2] = self.matrix[row_2], self.matrix[row_1]

    def linear_combo_1(self, params):
        """L_i  +/- L_j -->  L_i"""
        # TODO: add error checking
        row_1, op, row_2, target_row = params

        row_1 = int(row_1) - 1
        row_2 = int(row_2) - 1

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
        factor = Fraction(factor)

        pm = 1 if op == "+" else -1

        self.matrix[row_1] = [
            x + factor * pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]


def main():
    Assistant()


if __name__ == "__main__":
    main()
