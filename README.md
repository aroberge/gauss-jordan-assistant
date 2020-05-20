# Gauss-Jordan Assistant (gja)

Enabling live demonstration of the Gauss-Jordan algorithm in a terminal/console.

Note: this is a very early version.

## Description

The idea of this project is to enable live demonstration of using the Gauss-Jordan algorithm to solve systems of linear equations, using a simple console. This project is developed on Windows but should work using other operating systems.

![Example of row operation](screenshot.png "Example of row operation")

## Why?

I teach an introductory course in Linear Algebra to non-math majors using
videoconference. Students are not required to do any proofs. Instead they
must be able to do various calculations, many of which require
to use Gaussian elimination.

As I teach remotely, I share the content of my screen.
My hand-writing (either using a mouse or a tablet) is absolutely atrocious
with these tools.  In my experience, using slides with all the content
written up in advance (which is what I most often end up doing)
is not a good way to maintain student engagement.

As a result, I have developed this tool which allows me to do
live computations on my screen in a legible way.  Using this tool,
it can ask students to guide me in finding a solution to any
numerical problem that we are looking at, just as easily as I could
do it in a traditional classroom with a blackboard.

## Bonus (to come)

It will be possible to save the result of all the steps using LaTeX
format, for easy inclusion (without typos!) in any LaTeX document.

## Requirements

- Python 3.8+
- Rich (https://pypi.org/project/rich/).  Rich is a fantastic project.

To work properly on Windows (which is what I use), you need the following:

- Windows Terminal (https://github.com/Microsoft/Terminal), which you can
  get from the Microsoft Store.

![Available commands](help.png "Available commands")

