# boggler-flask
A [Flask](https://flask.palletsprojects.com) web app for solving the Boggle word game

## Live-demo
It's still a work in progress, but a live demo can be found -> [here](https://boggler.cblankenbuehler.com)

## Issues
Please feel free to submit an [issue](https://github.com/cblanken/boggler-flask/issues) if
you notice any bugs while exploring the app. Thanks!

## Usage
1. Submit the board
    - Fill out the board on the home page by click on a cell and entering the
corresponding letter in your boggle board.  
    - The `TAB` key can also be used to navigate between cells.
    - Once the board is filled, click the `Solve` button at the bottom of the board.
    ![boggle1](https://user-images.githubusercontent.com/19908880/195197478-8ebd4a0f-7094-491d-974a-8f202ded5678.png)
2. Board and Table Interaction
    - The solved board page will display a table of found words. Click on the 
  table row to show the path on the Boggle board
    - Individual board cells can also be clicked to filter the table to words that pass
  through that specific cell. The cell will be highlighted in red.
    - To remove the filter, click the button with the filter icon below the board.
    ![boggle3](https://user-images.githubusercontent.com/19908880/195198375-206ac6ff-0e1f-430d-88ca-8d81b9cf78d0.png)
