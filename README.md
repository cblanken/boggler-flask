# boggler-flask
A [Flask](https://flask.palletsprojects.com) web app for solving the Boggle word game.

## Live-demo
It's still a work in progress, but you can check out the live site at [https://boggler.cblanken.dev](https://boggler.cblanken.dev).

## Issues
If you notice any bugs while exploring the app please file an [issue](https://github.com/cblanken/boggler-flask/issues), so I can fix it. Thanks!

## Usage
1. Submit the board
    - Fill out the board on the home page by clicking on a cell and entering the
corresponding letter in your boggle board.  
    - The <kbd>TAB</kbd> key can used to move to the next cell and <kbd>SHIFT + TAB</kbd> navigates to the previous cell.
    - Once the board is filled, click the `Solve` button at the bottom of the board.
    ![boggle1](https://user-images.githubusercontent.com/19908880/195197478-8ebd4a0f-7094-491d-974a-8f202ded5678.png)
2. Board and Table Interaction
    - The solved board page will display a table of found words. Click on the 
  table row to show the path on the Boggle board
    - Individual board cells can also be clicked to filter the table to words that pass
  through that specific cell. The cell will be highlighted in red.
    - To remove the filter, click the button with the filter icon below the board.
    ![boggle3](https://user-images.githubusercontent.com/19908880/195198375-206ac6ff-0e1f-430d-88ca-8d81b9cf78d0.png)
    - Click on words in the table to show their path on the board.

## Development
2. Run one of the the startup scripts.
Launches the app in debug mode
```console
$ ./boot-dev.sh
```

Launches the app with gunicorn in production mode
```console
$ ./boot.sh
```

Navigate to the app at `http://localhost:5000`.

### Docker
If you don't care about live reload you can run the fully containerized app with:
```console
$ sudo FLASK_CONFIG=development docker-compose up 
```
Then the app should be available at `http://localhost`
This is only really recommended this for deployment.

