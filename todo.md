# To do/steps to implement:

## First make it work in the console

 - [x] print formatted matrix with integer entries in console
 - [x] print formatted matrix with Fractions entries in console
 - [ ] define matrix command (possibly `mat n x m`) which prompts user for matrix entries
   - [ ] possible prompt: "Entrez une ligne"
 - [ ] implement the same for augmented matrices, possibly using the notation: `mat n x m | p`
 - [ ] implement error message for command that cannot be parsed
 - [ ] parse commands for row operations
   - [ ] L_i <--> L_j  (i and j are integers)
     - [ ] allow not including underscore ?
   - [ ] f L_i --> L_i   (f is an int or fraction)
   - [ ] L_i + f L_j --> L_i
 - [ ] Do not implement undo last command; use inverse row operation instead (useful for teaching purpose)
 - [ ] Command to return to initial matrix (recommencer?) This could be useful to illustrate how different choices can lead to the same final answer

## Next, we have two options which can be done in any order


### Make it look nicer in the console

 - [ ] Assuming console with black background, use colorama to highlight zeros in red and vertical bar of augmented matrix in another color to be specified, with coefficients on other side of vertical bar a different color.

  - [ ] See if using smaller fonts for subscript might be useful, something like `subscript = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}`


### Make it work for LaTeX

 - [ ] Record history of elementary row operations for producing LaTeX output
 - [ ] Save output in LaTeX format
   - [ ] Save single matrix
   - [ ] Save entire process
   - [ ] Save for slides and for normal document. Slides output only show initial matrix, elementary operation, result, resuming on following slide with result as initial.



## Potential additions for later

 - [ ] Enable color customization
 - [ ] Enable support for other languages
 - [ ] Possibly support by default row operation commands done using either L or R, in any language.
 - [ ] Possibly recognize `row echelon form` and `reduced row echelon form` and print a message when such form is seen for the first time in a given process;
 this would apply in the console only.

 - [ ] Identify pivots (white background in console, circled characters in LaTeX?)


