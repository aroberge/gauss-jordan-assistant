"""Gauss-Jordan assistant

Requires Python 3.8+ and Rich (https://github.com/willmcgugan/rich)
"""

__version__ = "0.1"

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
        "markdown.item.bullet": "spring_green4",
        "markdown.code": "bold yellow",
        "matrix": "deep_sky_blue1",
        "error": "bold red",
        "prompt": "spring_green4",
        "row_operation": "yellow",
    }
)

console = Console(theme=dark_theme)

light_theme = Theme(  # suitable on a light background
    {
        "markdown.h1.border": "deep_sky_blue1",
        "markdown.h1": "blue",
        "markdown.h2": "blue underline",
        "markdown.item.bullet": "spring_green4",
        "markdown.code": "purple",
        "matrix": "deep_sky_blue1",
        "error": "red",
        "prompt": "spring_green4",
        "row_operation": "spring_green4",
    }
)

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

RIGHT_ARROW = "-->"
LANG = "en"
translations = {"en": {}, "fr": {}}


def _(text):
    """Mimicking gettext translations with simple dict"""
    if LANG in translations:
        return translations[LANG][text]
    else:
        return translations["en"][text]


help_en = """# Available commands

- `fr`  : change la langue au français
- light : change theme colours for light background
- dark  : change theme colours for dark background (default)

## Matrix operations

Below, `i, j, m, n, p` are integers and `f` is either
an integer or a fraction (`m/n`).

First, define a matrix:

- `mat m x n`      : Coefficient matrix
- `mat m x n | p`  : Augmented matrix with `p` extra columns.

Then, perform some elementary row operations:

- `R_i  <-->  R_j`              : row exchange
- `R_i  +/-  [f] R_j  -->  R_i` : linear combination (do not write `f` if `f=1`)
- `f R_i  -->  R_i`             : multiplication par a scalar

## Other commands

- save_latex filename   # todo
- `help` / `aide`      : prints this
- `quit` / `exit`
"""

help_fr = """# Liste des commandes

- `en`  : changes language to English
- light : change les couleurs pour un arrière-plan pâle
- dark  : change les couleurs pour un arrière-plan foncé (défaut)

## Opérations sur les matrices

Ci-dessous, `i, j, m, n, p` sont des entiers et `f` est soit
un entier ou soit un nombre rationnel  (`m/n`).

En premier, définir votre matrice

- `mat m x n`      : matrice des coefficients
- `mat m x n | p`  : matrice augmentée avec `p` colonnes supplémentaires

Ensuite, faites des opérations élémentaires sur les lignes:

- `L_i  <-->  L_j`              : échange de lignes
- `L_i  +/-  [f] L_j  -->  L_i` : combinaison linéaire (omettre `f` si `f=1`)
- `f L_i  -->  L_i`             : multiplication par un scalaire

## Autres commandes

- save_latex nom_de_fichier   # à faire
- `aide` / `help`      : imprime ceci
- `quit`[ter] / `exit` : termine les opérations
"""


translations["en"]["help"] = Markdown(help_en)
translations["fr"]["help"] = Markdown(help_fr)

translations["en"]["R_or_L"] = "R"
translations["fr"]["R_or_L"] = "L"

translations["en"]["Unknown operation"] = "Unknown operation"
translations["fr"]["Unknown operation"] = "Opération non reconnue."

translations["en"]["Add matrix line"] = "Enter a line with %d matrix elements: "
translations["fr"]["Add matrix line"] = "Entrez une ligne avec %d coefficients : "

translations["en"]["Data entry stopped."] = "Data entry stopped."
translations["fr"]["Data entry stopped."] = "Entrée des données interrompue."

translations["en"]["Wrong format"] = "The matrix element format is incorrect."
translations["fr"]["Wrong format"] = "Le format des coefficients soumis est incorrect."

translations["en"]["Wrong number"] = "Wrong number of matrix elements."
translations["fr"]["Wrong number"] = "Le nombre de coefficients soumis est incorrect."

translations["en"][
    "Scalar multiplication on same line"
] = "Scalar multiplication must operate on a single line."
translations["fr"][
    "Scalar multiplication on same line"
] = "La multiplication par un scalaire doit transformer la même ligne."

translations["en"]["Row does not exist"] = "Row %d does not exist."
translations["fr"]["Row does not exist"] = "La ligne %s n'existe pas."


translations["en"]["Cannot multiply by zero"] = "A row cannot be multiplied by zero."
translations["fr"][
    "Cannot multiply by zero"
] = "On ne peut pas multiplier une ligne par zéro."

translations["en"]["No effect"] = "This row operation does nothing"
translations["fr"]["No effect"] = "Cette opération ne change rien."

translations["en"]["Must be the same line"] = "Start and end row must be the same."
translations["fr"][
    "Must be the same line"
] = "Les lignes de départ et d'arrivée doivent être identiques."


translations["en"][
    "Cannot use a single line"
] = "A linear combination requires two different rows."
translations["fr"][
    "Cannot use a single line"
] = "Une combinaison linéaire requiert deux lignes différentes."


re_quit = re.compile(r"(quit|exit).*", re.IGNORECASE)

re_help = re.compile(r"(help|aide).*", re.IGNORECASE)

# matches integers or fractions as in 1 22 2/33 , etc.
re_fract = re.compile(r"(-?\d+/?\d*)")  # /?  means zero or 1 /

# This is the most complicated regex used;
# for this reason, I have shown the main steps.
# This matches something like R_2 + 1/2 R_3 --> R_2
# For simplicity, instead of R for row, we can use L (ligne, en français):
#    either L or R will work in any context.
# Also for simplicity, R_2 is identical to R2
# Finally, we limit the row number to be a single digit.

re_row_lin_combo_2 = re.compile(
    r"""^         # line begins
        \s*
        [LR]_?(\d)  # original row; can use either L or R to denote a row
        \s*
        (\+|-)    # plus or minus
        \s*
        (\d+/?\d*)  # integer or fraction
        \s*
        [LR]_?(\d)   # other row
        \s*
        -+>        # arrow -->
        \s*
        [LR]_?(\d)   # target line
        \s*
        $          # end of line
        """,
    re.VERBOSE,
)


# mat 3 x 4
re_mat = re.compile(r"^\s*mat\s*(\d+)\s*x\s*(\d+)\s*$", re.IGNORECASE)

# mat 3 x 4 | 1
re_aug_mat = re.compile(r"^\s*mat\s*(\d+)\s*x\s*(\d+)\s*\|\s*(\d+)\s*$", re.IGNORECASE,)

# The following matches R_2 <--> R_3 and similar operations
re_row_interchange = re.compile(r"""^\s*[LR]_?(\d)\s*<-+>\s*[LR]_?(\d)\s*$""")

# This matches something like 1/2 R_3 --> R_3
re_row_scaling = re.compile(r"^\s*(\d+/?\d*)\s*[LR]_?(\d)\s*-+>\s*[LR]_?(\d)\s*$")

# This matches something like R_2 - R_3 --> R_2
re_row_lin_combo_1 = re.compile(
    r"^\s*[LR]_?(\d)\s*(\+|-)\s*[LR]_?(\d)\s*-+>\s*[LR]_?(\d)\s*$"
)


class Assistant:
    def __init__(self):
        self.prompt = self.default_prompt = "> "
        self.matrix = None
        self.interact()

    def interact(self):
        """Command interpreter"""
        global console, LANG

        while True:
            command = self.user_input()

            if re.search(re_quit, command):
                break

            elif command.lower() == "light":
                console = Console(theme=light_theme)

            elif command.lower() == "dark":
                console = Console(theme=dark_theme)

            elif command.lower() == "en":
                LANG = "en"

            elif command.lower() == "fr":
                LANG = "fr"

            elif re.search(re_help, command):
                console.print(_("help"), "\n")

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
                self.print_error(_("Unknown operation"))
                continue

            if self.matrix is not None:
                self.console_print()
                self.current_row_operations.clear()

    def new_matrix(self, nb_rows, nb_cols, nb_augmented_cols=0):
        """Sets the parameters for a new matrix.

        This is called after a command like

            mat m x n
            mat m x n | p

        """
        self.matrix = []
        self.previously_formatted = None
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols
        self.current_row_operations = {}
        self.new_matrix_get_rows()

    def new_matrix_get_rows(self):
        """Command interpreter active when a new matrix is created.
           Gets the elements of a new matrix, row by row.
        """

        self.prompt = _("Add matrix line") % self.total_nb_cols
        while True:
            done = False
            command = self.user_input()
            if row := re.findall(re_fract, command):
                done = self.new_matrix_add_row(row)
                if done:
                    break
            elif re.search(re_quit, command):
                self.print_error(_("Data entry stopped."))
                self.matrix = None
                break
            else:
                self.print_error(_("Wrong format"))
        self.prompt = self.default_prompt

    def new_matrix_add_row(self, row):
        """Adds a single row of coefficients for a new matrix."""
        try:
            row = [Fraction(str(entry)) for entry in row]
        except Exception:
            self.print_error(_("Wrong format"))
            return False
        if len(row) == self.nb_cols + self.nb_augmented_cols:
            self.matrix.append(row)
            if len(self.matrix) == self.nb_requested_rows:
                self.nb_rows = self.nb_requested_rows
                return True  # we are done
        else:
            self.print_error(_("Wrong number"))
        return False

    def console_print(self):
        """Prints matrix with columns right-aligned, and some minimal
           spacing between between each column.
        """

        matrix = self.format_matrix()
        operations = self.format_row_operations()

        if operations is not None:
            display = Table().grid(padding=(0, 3))
            display.add_column()
            display.add_column()
            display.add_column()
            display.add_row(self.previously_formatted, operations, matrix)
            console.print(display)
        else:
            console.print(matrix)

        self.previously_formatted = matrix

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
            matrix = Table(
                show_header=False,
                box=MATRIX,
                padding=(0, 0),
                style="matrix",
                pad_edge=False,
            )
            matrix.add_column()
            matrix.add_row(coeff_matrix)
            return matrix

        augmented = Table().grid()
        augmented.add_column(style="white")

        for row_idx, row in enumerate(self.matrix):
            content = ""
            for col_idx, column in enumerate(row[self.nb_cols :], self.nb_cols):
                content += col_format[col_idx].format(str(column))
            if row_idx != 0:
                augmented.add_row(" ")
            augmented.add_row(content + padding)

        matrix = Table(
            show_header=False,
            box=MATRIX,
            padding=(0, 0),
            style="matrix",
            pad_edge=False,
        )
        matrix.add_column()
        matrix.add_column()
        matrix.add_row(coeff_matrix, augmented)
        return matrix

    def format_row_operations(self):
        """Formats row operations to align them with the changed line
           in the matrix.
        """
        if not self.current_row_operations:
            return None

        max_str_length = 0
        for op in self.current_row_operations:
            length = len(self.current_row_operations[op])
            if length > max_str_length:
                max_str_length = length

        fmt = "{:>%d}" % max_str_length

        operations = Table().grid()
        operations.add_column(style="row_operation")

        operations.add_row()
        for row_idx, row in enumerate(self.matrix):
            if row_idx in self.current_row_operations:
                operations.add_row(fmt.format(self.current_row_operations[row_idx]))
            else:
                operations.add_row()
            operations.add_row()

        return operations

    @staticmethod
    def print_error(text):
        console.print("\n    [error]" + text)
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
            self.current_row_operations.clear()
            return False

        self.matrix[row] = [
            factor * self.matrix[row][col] for col in range(len(self.matrix[row]))
        ]
        R = _("R_or_L")
        self.current_row_operations[
            target_row
        ] = f"{factor} {R}_{row+1} {RIGHT_ARROW} {R}_{row+1}"
        return True

    def valid_scale_row(self, row, target_row, factor):
        """Verifies that parameters in scaling transformation are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if row != target_row:
            self.print_error(_("Scalar multiplication on same line"))
            return False
        if not (0 <= row < len(self.matrix)):
            self.print_error(_("Row does not exist") % (row + 1))
            return False
        if factor == 0:
            self.print_error(_("Cannot multiply by zero"))
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
            self.current_row_operations.clear()
            return False

        self.matrix[row_1], self.matrix[row_2] = self.matrix[row_2], self.matrix[row_1]

        R = _("R_or_L")
        self.current_row_operations[row_2] = f"{R}_{row_1+1} {RIGHT_ARROW} {R}_{row_2+1}"
        self.current_row_operations[row_1] = f"{R}_{row_2+1} {RIGHT_ARROW} {R}_{row_1+1}"

        return True

    def valid_interchange_rows(self, row_1, row_2):
        """Verifies that parameters in row exchange transformation are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if row_1 == row_2:
            self.print_error(_("No effect"))
            return False
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error(_("Row does not exist") % (row_1 + 1))
            return False
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error(_("Row does not exist") % (row_2 + 1))
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
            self.current_row_operations.clear()
            return False

        pm = 1 if op == "+" else -1
        self.matrix[row_1] = [
            x + pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]
        R = _("R_or_L")
        self.current_row_operations[
            target_row
        ] = f"{R}_{row_1+1} {op} {R}_{row_2+1} {RIGHT_ARROW} {R}_{target_row+1}"

        return True

    def validate_linear_combo_1(self, row_1, row_2, target_row):
        """Verifies that parameters in linear combination '1' are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if not (0 <= row_1 < len(self.matrix)):
            self.print_error(_("Row does not exist") % (row_1 + 1))
            return False
        if not (0 <= row_2 < len(self.matrix)):
            self.print_error(_("Row does not exist") % (row_2 + 1))
            return False
        if row_1 != target_row:
            self.print_error(_("Must be the same line"))
            return False
        if row_1 == row_2:
            self.print_error(_("Cannot use a single line"))
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
            self.current_row_operations.clear()
            return False

        pm = 1 if op == "+" else -1
        self.matrix[row_1] = [
            x + factor * pm * y for x, y in zip(self.matrix[row_1], self.matrix[row_2])
        ]
        R = _("R_or_L")
        self.current_row_operations[
            target_row
        ] = f"{R}_{row_1+1} {op} {factor} {R}_{row_2+1} {RIGHT_ARROW} {R}_{target_row+1}"

        return True

    def validate_linear_combo_2(self, row_1, row_2, target_row, factor):
        """Verifies that parameters in linear combination '2' are valid.
           Returns False if invalid parameters, True otherwise.
        """
        if not self.validate_linear_combo_1(row_1, row_2, target_row):
            return False
        if factor == 0:
            self.print_error(_("No effect"))
            return False
        return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        LANG = sys.argv[1]

    Assistant()
