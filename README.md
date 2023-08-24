# boggler-flask
A [Flask](https://flask.palletsprojects.com) web app for solving the Boggle word game

## Live-demo
It's still a work in progress, but a live demo can be found -> [here](https://boggler.cblanken.dev)

## Issues
Please feel free to submit an [issue](https://github.com/cblanken/boggler-flask/issues) if
you notice any bugs while exploring the app. Thanks!

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

## Development
### With live reload
A few services are required to run the full application. The easiest way to get up running
is to follow these steps:
1. Spin up the redis instance. You may want to run this without the `-d` to monitor the `redis` logs live for any errors.
    ```console
    $ docker-compose up redis -d
    ```
2. Run the startup script. This start the gunicorn server and the backend celery process for queuing multiple board solve tasks
    ```console
    $ ./boot.sh
    ```
Navigate to the app at `http://localhost:5000`

### No live reload
If you don't care about live reload you can run the fully containerized app with:
```console
$ sudo FLASK_CONFIG=development docker-compose up 
```
Then the app should be available at `http://localhost`

## Deployment
### Renew HTTPs Certs
- To renew Let's Encrypt cert, shutdown the app (`sudo docker compose down`), then run
`sudo certbot --nginx renew`. Stop `nginx.service` with `sudo systemctl stop nginx.service`
(it may be necessary to restart the host) then restart the app with `sudo FLASK_CONFIG=production docker compose up -d`.
