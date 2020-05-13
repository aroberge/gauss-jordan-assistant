"""Gauss-Jordan assistant

Requires Python 3.8+
"""

from fractions import Fraction
import re


# The following regex are defined with the re.I flag, which means to ignore
# case, and are completely permissive in the amount of space
# they allow between each token.
# Useful resource for testing: https://regex101.com/

re_quit = re.compile(r"(quit|exit).*", re.I)

# mat 3 x 4
re_mat = re.compile(r"mat\s*(\d+)\s*x\s*(\d+)\s*$", re.I)

# mat 3 x 4 | 1
re_aug_mat = re.compile(r"mat\s*(\d+)\s*x\s*(\d+)\s*\|\s*(\d+)\s*$", re.I)

# matches integers or fractions as in 1 22 2/33 , etc.
re_fract = re.compile(r"(\d+/*\d*)")


class Assistant:
    def __init__(self):
        self.prompt = self.default_prompt = "> "
        self.matrix = None

    def interact(self):
        while True:
            command = input(self.prompt)
            self.mode = self.parse(command)
            if self.mode == "quit":
                break
            elif self.mode == "new mat":
                self.get_rows()

    def get_rows(self):
        self.prompt = f"Entrez une ligne avec ({self.matrix.nb_cols} nombres) >"
        while True:
            done = False
            command = input(self.prompt)
            if row := re.findall(re_fract, command):
                done = self.matrix.add_row(row)
            if done:
                self.matrix.console_print()
                break
        self.prompt = self.default_prompt

    def parse(self, command):
        if re.search(re_quit, command):
            return "quit"
        elif match := re.search(re_mat, command):
            self.matrix = Matrix(int(match.group(1)), int(match.group(2)))
            return "new mat"
        elif match := re.search(re_aug_mat, command):
            print(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        else:
            print("Je ne reconnais pas cette commande")


class Matrix:
    def __init__(self, nb_rows, nb_cols, nb_augmented_cols=0):
        self.matrix = []
        self.nb_requested_rows = nb_rows
        self.nb_rows = 0
        self.nb_cols = nb_cols
        self.nb_augmented_cols = nb_augmented_cols

        self.rows = None
        self.col_indx = None
        self.augm_col_indx = None

    def add_row(self, row):
        try:
            row = [Fraction(str(entry)) for entry in row]
        except Exception:
            print("Le format des nombres soumis est incorrect")
            return False
        if len(row) == self.nb_cols:
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
        col_max_widths = [0, 0, 0]
        spacing = 2  # minimum space between each column
        # determine maximum width of each column
        for row in self.matrix:
            for col_idx, col_info in enumerate(zip(col_max_widths, row)):
                max_width, entry = col_info
                if len(str(entry)) > max_width:
                    col_max_widths[col_idx] = len(str(entry))

        col_format = ["{:>%ds}" % (width + spacing) for width in col_max_widths]

        for row in self.matrix:
            for col_idx, column in enumerate(row):
                print(col_format[col_idx].format(str(column)), end="")
            print()
        print()


def main():
    a = Assistant()
    a.interact()
    # m = Matrix()
    # m.add_row([1, Fraction(0.5), -3])
    # m.add_row([3, 4, 5])
    # m.add_row([6, 17, 8])
    # m.render_console()


if __name__ == "__main__":
    main()
