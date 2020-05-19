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
- [ ] print last performed row operation, with nice format.

- [ ] Command to return to initial matrix (recommencer?) This could be useful to illustrate how different choices can lead to the same final answer

 - [ ] Implement error messages for operations that are either useless (exchanging a
   row ith itself) or not a proper elementary row operation.

## Next, we have two options which can be done in any order


### Make it look nicer in the console

- [x] Use Rich to surround numbers by colored brackets and inserting a
      vertical bar for augmented matrices.


### Make it work for LaTeX

 - [ ] Record history of elementary row operations for producing LaTeX output
 - [ ] Save output in LaTeX format

- [ ] Possibly use something like https://tex.stackexchange.com/questions/532632/elementary-row-operation-labels-for-matrices instead of my standard version.

## More

 - [ ] Enable multiple row operations done in one step. This might be
 particularly useful for LaTeX output.
 - [ ] Use Rich to highlight leading zeros and pivots in a different colour.
 - [ ] Automatically identify pivots in LaTeX ?  (or only for row echelon form and reduced form?)

## Potential additions for later

 - [ ] Possibly enable color customization
 - [ ] Enable support for languages other than French
 - [ ] Possibly support by default row operation commands done using either L or R, in any language.


