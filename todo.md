# To do/steps to implement:

## First make it work in the console

 - [x] print formatted matrix with integer entries in console
 - [x] print formatted matrix with Fractions entries in console
 - [x] define matrix command (possibly `mat n x m`) which prompts user for matrix entries
   - [x] possible prompt: "Entrez une ligne avec m nombres"
 - [x] implement the same for augmented matrices, possibly using the notation: `mat n x m | p`
 - [x] implement error message for command that cannot be parsed
 - [x] parse commands for row operations
   - [x] L_i <--> L_j  (i and j are integers)
     - [x] allow not including underscore ?
   - [x] f L_i --> L_i   (f is an int or fraction)
   - [x] L_i + f L_j --> L_i
- [x] implement the various row operations as matrix transformations.
 - [ ] Do not implement undo last command; use inverse row operation instead (useful for teaching purpose)
- [ ] Command to return to initial matrix (recommencer?) This could be useful to illustrate how different choices can lead to the same final answer
- Keep track of history

 - [ ] Implement error messages for operations that are either useless (exchanging a
   row ith itself) or not a proper elementary row operation.

## Next, we have two options which can be done in any order


### Make it look nicer in the console

- [x] Use Rich to surround numbers by colored brackets and inserting a
      vertical bar for augmented matrices.


### Make it work for LaTeX

 - [ ] Record history of elementary row operations for producing LaTeX output
 - [ ] Save output in LaTeX format
   - [ ] Save single matrix
   - [ ] Save entire process
   - [ ] Save for slides and for normal document. Slides output only show initial matrix, elementary operation, result, resuming on following slide with result as initial.

- [ ] Possibly use something like https://tex.stackexchange.com/questions/532632/elementary-row-operation-labels-for-matrices instead of my standard version.


## Potential additions for later

 - [ ] Possibly enable color customization
 - [ ] Enable support for languages other than French
 - [ ] Possibly support by default row operation commands done using either L or R, in any language.
 - [ ] Possibly recognize `row echelon form` and `reduced row echelon form` and print a message when such form is seen for the first time in a given process;
 this would apply in the console only.

 - [ ] Identify pivots (white background in console, circled characters in LaTeX?)

 - [ ] Enable multiple row operations done in one step. This might be
 particularly useful for LaTeX output.

 - [ ] Use Rich to highlight leading zeros and pivots in a different colour.

