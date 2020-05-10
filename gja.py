'''Gauss-Jordan assitant
'''

from fractions import Fraction


class Matrix:
    def __init__(self):
        self.matrix = []
        self.rows = None
        self.col_indx = None
        self.augm_col_indx = None

    def add_row(self, row):
        row = [Fraction(str(entry)) for entry in row]
        self.matrix.append(row)

    def render_console(self):
        '''Prints matrix with columns right-aligned, and at least two
           space between each column'''
        # Assume single-digit integers for now
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
                print(col_format[col_idx].format(str(column)), end='')
            print()
        print()


def main():
    m = Matrix()
    m.add_row([1, Fraction(0.5), -3])
    m.add_row([3, 4, 5])
    m.add_row([6, 17, 8])
    m.render_console()


if __name__ == '__main__':
    main()
