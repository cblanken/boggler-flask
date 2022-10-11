# boggler-flask
A [Flask](https://flask.palletsprojects.com) web app for solving the Boggle word game

## Issues
Please feel free to submit an [issue](https://github.com/cblanken/boggler-flask/issues) if
you notice any bugs while exploring the app. Thanks!

## Usage
1. Submit the board
    - Fill out the board on the home page by click on a cell and entering the
corresponding letter in your boggle board.  
    - The `TAB` key can also be used to navigate between cells.
    - Once the board is filled, click the `Solve` button at the bottom of the board.
2. Board and Table Interaction
    - The solved board page will display a table of found words. Click on the 
  table row to show the path on the Boggle board
    - Individual board cells can also be clicked to filter the table to words that pass
  through that specific cell. The cell will be highlighted in red.
    - To remove the filter, click the button with the filter icon below the board
