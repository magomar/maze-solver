import logging

import typer

from maze_solver import __version__
from maze_solver.solver import solve_maze

app = typer.Typer()


@app.callback()
def main(
):
    logging.basicConfig(filename='maze-solver.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    typer.echo(f'Running Maze Solver version {__version__}')


@app.command()
def solve(
        maze_example: int,
):
    typer.echo(f'Solving maze by using Dijkstra’s search algorithm')
    solve_maze(maze_example)


if __name__ == '__main__':
    app()
