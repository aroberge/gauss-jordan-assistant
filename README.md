# Gauss-Jordan Assistant (gja)

Enabling live demonstration of the Gauss-Jordan algorithm in a terminal/console.

## Description

The idea of this project is to enable live demonstration of using the Gauss-Jordan algorithm to solve systems of linear equations, using a simple console. This project is developed on Windows but should work using other operating systems.

![Example of row operation](screenshot.png "Example of row operation")

## Why?

I teach an introductory course in Linear Algebra to non-math majors using
videoconference. Students are not required to do any proofs. Instead they
must be able to do various calculations, almost all of which require
the use of the Gauss-Jordan algorithm.

As I teach remotely, I share the content of my screen.
My hand-writing (either using a mouse or a tablet) is absolutely atrocious
in that context.  Using slides with all the content written up in advance
is not a good way to maintain student engagement.

As a result, I have developed this tool which allows me to do
live computations on my screen in a legible way.  Using this tool,
it will be easy to ask students to guide me in finding a solution to
particular numerical problems.

## Requirements

- Python 3.8+
- Rich (https://pypi.org/project/rich/)

To work properly on Windows (which is what I use), you need the following:

- Windows Terminal (https://github.com/Microsoft/Terminal)

![Available commands](help.png "Available commands")

