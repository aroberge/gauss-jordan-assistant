"""Gauss-Jordan assistant

Requires Python 3.8+
"""

from fractions import Fraction
import re

re_quit = re.compile(r"(quit|exit).*", re.IGNORECASE)

re_help = re.compile(r"(help|aide).*", re.IGNORECASE)

# mat 3 x 4
re_mat = re.compile(r"""\s*     # ignore spaces
                        mat
                        \s*
                        (\d+)   # one or more digits
                        \s*
                        x
                        \s*
                        (\d+)
                        \s*
                        $       # to the end of the line
                        """, re.VERBOSE | re.IGNORECASE)

# mat 3 x 4 | 1
re_aug_mat = re.compile(r"""\s* # ignore spaces
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
                        """, re.VERBOSE | re.IGNORECASE)

# matches integers or fractions as in 1 22 2/33 , etc.
re_fract = re.compile(r"(\d+/?\d*)")  # /?  means zero or 1 /

# We limit the number of rows at 9 or fewer
# The following matches L_2 <--> L_3 and similar operations
re_row_interchange = re.compile(r"""
                                \s*
                                L_?    # zero or one underscore
                                (\d)   # single digit for row number
                                \s*
                                <-+>   # one or more - between < >
                                \s*
                                L_?
                                (\d)
                                \s*
                                $""", re.VERBOSE)
# This matches something like 1/2 L_3 --> L_3
re_row_scaling = re.compile(r"\s*(\d+/?\d*)\s*L_?(\d)\s*-+>\s*L_?(\d)\s*$")
# This matches something like L_2 - L_3 --> L_2
re_row_lin_combo_1 = re.compile(
    r"\s*L_?(\d)\s*-+>\s*L_?(\d)\s*(\+|-)\s*L_?(\d)\s*$"
)
# This matches something like L_2 + 1/2 L_3 --> L_2
re_row_lin_combo_2 = re.compile(
    r"\s*L_?(\d)\s*-+>\s*L_?(\d)\s*(\+|-)\s*(\d+/?\d*)\s*L_?(\d)\s*$"
)

CREATE_NEW_MATRIX = "new mat"


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

    def new_matrix(self, nb_rows, nb_cols, nb_augmented_cols=0):
        self.matrix = []
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols

        self.rows = None
        self.col_indx = None
        self.augm_col_indx = None

    def add_row(self, row):
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

        print()
        for row in self.matrix:
            for col_idx, column in enumerate(row):
                if col_idx == self.nb_cols:
                    print("  |", end="")
                print(col_format[col_idx].format(str(column)), end="")
            print()
        print()

    def interact(self):
        while True:
            command = input(self.prompt)
            self.mode = self.parse(command)
            if self.mode == "quit":
                break
            elif self.mode == CREATE_NEW_MATRIX:
                self.get_rows()

    def get_rows(self):
        self.prompt = f"Entrez une ligne avec ({self.matrix.total_nb_cols} nombres) > "
        while True:
            done = False
            command = input(self.prompt)
            if row := re.findall(re_fract, command):
                done = self.matrix.add_row(row)
                if done:
                    self.matrix.console_print()
                    break
            else:
                print("Format non reconnu.")
        self.prompt = self.default_prompt

    def parse(self, command):
        if re.search(re_quit, command):
            return "quit"
        elif re.search(re_help, command):
            print(help)
        elif match := re.search(re_mat, command):
            self.matrix = Matrix(int(match.group(1)), int(match.group(2)))
            return CREATE_NEW_MATRIX
        elif match := re.search(re_aug_mat, command):
            self.matrix = Matrix(
                int(match.group(1)), int(match.group(2)), int(match.group(3))
            )
            return CREATE_NEW_MATRIX
        elif op := re.search(re_row_interchange, command):
            print(f"Interchange de lignes: L_{op.group(1)} <--> L_{op.group(2)}")
        elif op := re.search(re_row_scaling, command):
            print(f"Multiplication par un scalaire: {op.group(1)} L_{op.group(2)}  -->  L_{op.group(3)}")
        elif op := re.search(re_row_lin_combo_1, command):
            print(
                f"Combinaison linéaire: L_{op.group(1)} L_{op.group(2)} {op.group(3)} -->  L_{op.group(4)}"
            )
        elif op := re.search(re_row_lin_combo_2, command):
            print(
                f"Combinaison linéaire: L_{op.group(1)} L_{op.group(2)} {op.group(3)} L_{op.group(4)}  -->  L_{op.group(5)}"
            )
        else:
            print("Opération non reconnue.")


class Matrix:
    def __init__(self, nb_rows, nb_cols, nb_augmented_cols=0):
        self.matrix = []
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols
        self.total_nb_cols = nb_cols + nb_augmented_cols

        self.rows = None
        self.col_indx = None
        self.augm_col_indx = None

    def add_row(self, row):
        try:
            row = [Fraction(str(entry)) for entry in row]
        except Exception:
            print("Le format des nombres soumis est incorrect")
            return False
        if len(row) == self.nb_cols + self.nb_augmented_cols:
            self.matrix.append(row)
            if len(self.matrix) == self.nb_requested_rows:
                self.nb_rows = self.nb_requested_rows
                return True  # we are done
        else:
            print("Le nombre de coefficient soumis est incorrect")
        return False

    def console_print(self):
        """Prints matrix with columns right-aligned, and at least two
           space between each column"""
        col_max_widths = [0 for x in range(self.total_nb_cols)]
        spacing = 3  # minimum space between each column
        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        col_format = ["{:>%ds}" % (width + spacing) for width in col_max_widths]

        print()
        for row in self.matrix:
            for col_idx, column in enumerate(row):
                if col_idx == self.nb_cols:
                    print("  |", end="")
                print(col_format[col_idx].format(str(column)), end="")
            print("")
        print("\n")


def main():
    a = Assistant()
    a.interact()


if __name__ == "__main__":
    main()
