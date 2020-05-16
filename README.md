# gauss-jordan-assistant
Enabling live demonstration of Gauss-Jordan algorithm in a terminal/console

## Description

The idea of this project is to enable live demonstration of using the Gauss-Jordan algorithm to solve systems of linear equations, using a simple console. This project will be developed on Windows but should work using other operating systems.

Commands will include:
    - Defining the size of a matrix; number of rows limited to 9.
    - Entering its row
    - Using elementary row operations to transform the matrix
    - Optionnally, save the entire process using LaTeX syntax.

 Dependencies: colorama

 By default, the language used will be French. Extension to support other languages will be done eventually.

 Numbers will either `int` or instances of `fractions.Fractions`. Internally, `fractions.Fractions` will be used for all computations



## Requirements

Python 3.8+
