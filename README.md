# gauss-jordan-assistant
Enabling live demonstration of Gauss-Jordan algorithm in a terminal/console

## Description

The idea of this project is to enable live demonstration of using the Gauss-Jordan algorithm to solve systems of linear equations, using a simple console. This project will be developed on Windows but should work using other operating systems.

Commands will include:
    - Defining the size of a matrix
    - Entering its row
    - Using elementary row operations to transform the matrix
    - Optionnally, save the entire process using LaTeX syntax.
    
 Dependencies: colorama
 
 By default, the language used will be French. Extension to support other languages will be done eventually.
    
 Numbers will either int or instances of fractions.Fractions. Internally, fractions.Fractions will be used for all computations
    
 To do/steps to implement:
 
 - [ ] print formatted matrix with integer entries in console
 - [ ] print formatted matrix with Fractions entries in console
 - [ ] define matrix command (possibly `mat n x m`) which prompts user for matrix entries
   - [ ] possible promt: "Entrez une ligne"
 - [ ] implement the same for augmented matrices, possibly using the notation: `mat n x m | p`
 - [ ] implement error message for command that cannot be parsed
 - [ ] (Assuming console with black background) use colorama to highlight zeros in red and vertical bar of augmented matrix in another color to be specified.
 - [ ] parse commands for row operations
   - [ ] L_i <--> L_j  (i and j are integers)
     - [ ] allow not including underscore ?
   - [ ] f L_i --> L_i   (f is an int or fraction)
   - [ ] L_i + f L_j --> L_i
 - [ ] Commmand to revert last operation (undo ?). Useful to demonstrate unproductive row operations.
 - [ ] Command to return to initial matrix (undo all ?) This could be useful to illustrate how different choices can lead to the same final answer
 - [ ] Save output in LaTeX format
   - [ ] Save single matrix
   - [ ] Save entire process
 - [ ] Enable color customization
 - [ ] Enable support for other languages
 - [ ] Possibly support by default row operation commands done using either L or R, in any language.
 - [ ] Possibly recognize `row echelon form` and `reduced row echelon form` and print a message when such form is seen for the first time in a given process.
