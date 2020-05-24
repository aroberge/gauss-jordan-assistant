# About


The content includes the following:

- Explain why I created this tool.
- Describe why I chose [rich](https://pypi.org/project/rich/) and explain the various way I use it for this project.
- Explain some design decisions.

## Why I created this tool

I teach an introductory course in Linear Algebra to non-math majors using
videoconference. As I teach remotely, I share the content of my screen.
Many of the examples require, at one stage or another, that
Gaussian elimination on a matrix be performed.

My hand-writing (either using a mouse or a tablet) on a computer screen
is absolutely atrocious.  In my experience, using slides with all the content
written up in advance (which is what I have mostly done until now)
is not a good way to maintain student engagement.

I have also found that a small fraction of students do not seem to understand
the basic step of Gaussian elimination, even when I attempt to
provide additional explanations via email.

This tool, which I named the Gauss-Jordan Assistant (or GJA),
allows me to do live computations on my screen in a legible way.
I have tried to design it so that each computation includes some
visual clues reinforcing some aspects of Gaussian elimination,
as I describe further below.

Using the GJA, I can ask students to suggest what should be the
next step in the computation, just as easily as I could
do it in a traditional classroom with a blackboard, type in their
suggestion, observe the result, adding relevant explanations when things
go wrong.

## Why Rich
