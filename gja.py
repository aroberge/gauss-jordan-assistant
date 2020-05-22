"""Gauss-Jordan assistant

Enabling user-driven live demonstration of the Gauss-Jordan algorithm
in a terminal/console.

Source: https://github.com/aroberge/gauss-jordan-assistant

Requires Python 3.8+ and Rich (https://github.com/willmcgugan/rich)

All the content is in this single file, for those that do not want
to install from Pypi and simply copy and possibly modify to suit
their individual needs.

The organisation is as follows:

1. Rich specific definitions
2. Translations (French and English)
3. String parsing using regular expressions
4. Various LaTeX templates
5. The main code

"""

__version__ = "0.2"

import re
import tkinter
from tkinter import filedialog

from fractions import Fraction


from rich.box import Box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.theme import Theme

# Since we already use Rich, we might as well get pretty tracebacks. :-)
from rich.traceback import install

install(extra_lines=1)


# ===============================================
# Rich specific definitions
# ===============================================

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
        "row_operation": "bold yellow",
    }
)

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

console = Console(theme=dark_theme)

# Design our style of "box" to be used by rich

MATRIX = Box(
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

# ===============================================
# String translations
# ===============================================

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

- `latex` : saves as a LaTeX file.
- `help` / `aide`
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

- `latex` : sauvegarde dans un fichier LaTeX.
- `aide` / `help`
- `quit`[ter] / `exit`
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

translations["en"]["No effect"] = "This operation causes no change."
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

translations["en"]["Nothing to save"] = "Nothing to save: no matrix defined."
translations["fr"]["Nothing to save"] = "Il n'y a aucune matrice de définie."


# ===============================================
# String parsing using regular expressions
# ===============================================


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


# ===============================================
# LaTeX templates
#
# For LaTeX output, we use the beamer document class,
# with each individual transformation intended to be shown
# on a separate frame (aka slide).
#
# We also include a LaTeX command, \GJAfrac, with
# two possible definitions, giving the possibility to
# easily change how fractions are represented.
#
# Coefficient and augmented matrices are shown with
# square brackets using the "bmatrix" environment.
# Round brackets can be used instead if one replaces
# "bmatrix" by "pmatrix".
# ===============================================


LaTeX_begin_document = """
\\documentclass{beamer}
%
% augmented matrix from http://tex.stackexchange.com/questions/2233
\\makeatletter
\\renewcommand*\\env@matrix[1][*\\c@MaxMatrixCols r]{%
    \\hskip -\\arraycolsep
    \\let\\@ifnextchar\\new@ifnextchar
    \\array{#1}}
\\makeatother

%\\newcommand{\\GJAfrac}[2]{#1/#2}
\\newcommand{\\GJAfrac}[2]{\\frac{#1}{#2}}

\\begin{document}
"""

LaTeX_end_document = "\\end{document}"


LaTeX_begin_frame = """
\\begin{frame}{Frame %d}
\\[
\\begin{matrix}[ccc]
"""

LaTeX_end_frame = """\\end{matrix}
\\]
\\end{frame}

%===========================================
"""

LaTeX_begin_bmatrix = "\\begin{bmatrix}[%s%s]"

LaTeX_end_bmatrix = "\\end{bmatrix}\n"

LaTeX_begin_row_op_matrix = "\\begin{matrix}[r]"

LaTeX_end_row_op_matrix = "\\end{matrix}\n"


# ===============================================


RIGHT_ARROW = "-->"  # used in printing row operations
# Warning: using unicode arrows instead could mess up the alignment


class Assistant:
    """Enables user-driven live demonstration of Gauss-Jordan algorithm."""

    def __init__(self):
        self.prompt = self.default_prompt = "> "
        self.matrix = None

        # The following is used both for printing matrix element in
        # console and in LaTeX source file
        self.spacing = 2  # spacing between columns
        self.padding = self.spacing * " "

        print("lang =", LANG)

        self.interact()

    def interact(self):
        """Command interpreter"""
        while True:
            command = self.user_input()

            if re.search(re_quit, command):
                break

            result = self.parse(command)

            if result and self.matrix is not None:
                self.console_print()
                self.update_latex_content()
                self.current_row_operations.clear()

    def parse(self, command):
        """Parses command controlling the information displayed.
           To show the latest matrix update, an operation must return True.
        """
        global console, LANG

        lowercase = command.lower()

        if lowercase == "light":
            console = Console(theme=light_theme)

        elif lowercase == "dark":
            console = Console(theme=dark_theme)

        elif lowercase in ["en", "fr"]:
            if lowercase == LANG:
                console.print(_("No effect"))
            else:
                LANG = lowercase
                print("lang =", LANG)

        elif command.lower() == "latex":
            self.save_latex()

        elif re.search(re_help, command):
            console.print(_("help"), "\n")

        elif op := re.search(re_mat, command):
            return self.new_matrix(int(op.group(1)), int(op.group(2)))

        elif op := re.search(re_aug_mat, command):
            return self.new_matrix(int(op.group(1)), int(op.group(2)), int(op.group(3)))

        elif op := re.search(re_row_interchange, command):
            return self.interchange_rows(int(op.group(1)), int(op.group(2)))

        elif op := re.search(re_row_scaling, command):
            return self.scale_row(
                Fraction(op.group(1)), int(op.group(2)), int(op.group(3))
            )

        elif op := re.search(re_row_lin_combo_1, command):
            return self.linear_combo_1(
                int(op.group(1)), op.group(2), int(op.group(3)), int(op.group(4)),
            )

        elif op := re.search(re_row_lin_combo_2, command):
            return self.linear_combo_2(
                int(op.group(1)),
                op.group(2),
                Fraction(op.group(3)),
                int(op.group(4)),
                int(op.group(5)),
            )

        else:
            self.print_error(_("Unknown operation"))

    def new_matrix(self, nb_rows, nb_cols, nb_augmented_cols=0):
        """Sets the parameters for a new matrix.

        This is called after a command like

            mat m x n
            mat m x n | p

        """
        self.matrix = []
        self.previously_formatted_matrix = None
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols
        self.current_row_operations = {}

        self.latex_slide_no = 1
        self.latex_content = [LaTeX_begin_document]
        self.latex_previously_formatted_matrix = None
        return self.new_matrix_get_rows()

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
                    self.prompt = self.default_prompt
                    return True
            elif re.search(re_quit, command):
                self.print_error(_("Data entry stopped."))
                self.matrix = None
                self.prompt = self.default_prompt
                return False
            else:
                self.print_error(_("Wrong format"))

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
            display = Table().grid()
            display.add_column()
            display.add_column()
            display.add_column()
            display.add_row(self.previously_formatted_matrix, operations, matrix)
            console.print(display)
        else:
            console.print(matrix)

        self.previously_formatted_matrix = matrix

    def update_latex_content(self):
        matrix = self.latex_format_matrix()
        # operations = self.latex_format_row_operations()

        self.latex_content.append(LaTeX_begin_frame % self.latex_slide_no)
        if self.latex_previously_formatted_matrix is None:
            self.latex_content.append(matrix)
        else:
            operations = self.latex_format_row_operations()
            self.latex_content.append(
                self.latex_previously_formatted_matrix
                + " &\n"
                + operations
                + " &\n"
                + matrix
            )
        self.latex_content.append(LaTeX_end_frame)
        self.latex_slide_no += 1
        self.latex_previously_formatted_matrix = matrix

    def latex_format_matrix(self):
        if self.nb_augmented_cols:
            matrix = [
                LaTeX_begin_bmatrix
                % (("r" * self.nb_cols), ("|" + "r" * self.nb_augmented_cols))
            ]
        else:
            matrix = [LaTeX_begin_bmatrix % (("r" * self.nb_cols), "")]

        for row in self.matrix:
            row_content = []
            for col in row:
                row_content.append(self.latex_format_frac(col))
            matrix.append("  &  ".join(row_content) + r" \\")

        matrix.append(LaTeX_end_bmatrix)

        return "\n".join(matrix)

    def latex_format_frac(self, number):
        """If number is an integer, it is returned as a string;
           if number is a fraction, it is returned as a pre-defined
           LaTeX command.
        """
        if number.denominator == 1:
            return str(number.numerator)
        else:
            return "\\GJAfrac{%d}{%d}" % (number.numerator, number.denominator)

    def latex_format_row_operations(self):
        """Formats row operations to align them with the changed line
           in the matrix.
        """
        if not self.current_row_operations:
            return None

        matrix = [LaTeX_begin_row_op_matrix]

        for row_idx, row in enumerate(self.matrix):
            if row_idx in self.current_row_operations:
                matrix.append(
                    "\\scriptstyle "
                    + self.current_row_operations[row_idx].replace(
                        RIGHT_ARROW, "\\longrightarrow"
                    )
                    + r"\\"
                )
            else:
                matrix.append(r"\\")
        matrix.append(LaTeX_end_row_op_matrix)

        return "\n".join(matrix)

    def get_column_format(self):
        """Custom format for columns"""
        col_max_widths = [0 for x in range(self.total_nb_cols)]

        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        return ["{:>%ds}" % (width + self.spacing) for width in col_max_widths]

    def format_submatrix(self, start, end):
        """Formats the elements of a submatrix in right-justified columns.
           By submatrix, we mean either the coefficient matrix, or the
           elements on the right-hand side of the vertical bar for an
           augmented matrix.
        """
        ##################################
        # Using rich, it would be easy to produce a grid of numbers
        # aligned and spaced "just right".  However, I want to have
        # the flexibility to style differently certain matrix elements,
        # such as the leading zeros for a given row, or the pivots.
        # For this reason, I use a more complex, but potentially
        # more versatile approach.
        #
        col_format = self.get_column_format()

        matrix = Table().grid()
        matrix.add_column(style="white")

        for row_idx, row in enumerate(self.matrix):
            content = ""
            for col_idx, column in enumerate(row[start:end], start):
                content += col_format[col_idx].format(str(column))
            if row_idx != 0:
                matrix.add_row(" ")
            matrix.add_row(content + self.padding)
        return matrix

    def format_matrix(self, spacing=2):
        """Formats matrix for printing in console.
        """
        coeff_matrix = self.format_submatrix(0, self.nb_cols)

        matrix = Table(show_header=False, box=MATRIX, style="matrix", pad_edge=False,)
        matrix.add_column()
        if not self.nb_augmented_cols:
            matrix.add_row(coeff_matrix)
            return matrix
        else:
            augm = self.format_submatrix(self.nb_cols, self.total_nb_cols + 1)
            matrix.add_column()
            matrix.add_row(coeff_matrix, augm)
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

        operations = Table().grid(padding=(0, 0, 0, 3))
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
        if not self.validate_scale_row(row, target_row, factor):
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

    def validate_scale_row(self, row, target_row, factor):
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
        if not self.validate_interchange_rows(row_1, row_2):
            self.current_row_operations.clear()
            return False

        self.matrix[row_1], self.matrix[row_2] = self.matrix[row_2], self.matrix[row_1]

        R = _("R_or_L")
        self.current_row_operations[
            row_2
        ] = f"{R}_{row_1+1} {RIGHT_ARROW} {R}_{row_2+1}"
        self.current_row_operations[
            row_1
        ] = f"{R}_{row_2+1} {RIGHT_ARROW} {R}_{row_1+1}"

        return True

    def validate_interchange_rows(self, row_1, row_2):
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

    def save_latex(self, event=None):
        """Saves the entire operations done on current matrix as a
           LaTeX file.
        """
        if self.matrix is None:
            self.print_error(_("Nothing to save"))
            return
        filename = None

        app = tkinter.Tk()

        try:
            filename = filedialog.asksaveasfilename(filetypes=(("LaTeX", "*.tex"),))
        except FileNotFoundError:
            pass
        app.destroy()
        if filename is not None:
            self.latex_content.append(LaTeX_end_document)
            text = "\n".join(self.latex_content)
            with open(filename, "w") as f:
                f.write(text)


if __name__ == "__main__":
    Assistant()
