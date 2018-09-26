from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

import re

def create_db_session():
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    return DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    edit_url_regex = re.compile('/restaurants/[\d]+/edit/?$')
    delete_url_regex = re.compile('/restaurants/[\d]+/delete/?$')

    def do_GET(self):
        # ********************* HOME PAGE *********************
        if self.path.endswith('/restaurants'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            page_html = '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>Restaurants</title>
                        <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400" rel="stylesheet">
                    </head>
                    <body style="font-family: 'Open Sans', sans-serif; font-weight: 300; padding: 10px 20px;">
                        <h1>Restaurants</h1>
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants/new">
                            Add new restaurant
                        </a>
                        <ul style="padding: 0;">
                            {restaurants}
                        </ul>
                    </body>
                </html>
            '''

            restaurant_html = '''
                <li style="
                    list-style-type: none;
                    margin: 20px 0;
                    box-shadow: 0 0 5px 0 rgba(17,21,0,.2), 0 4px 8px 0 rgba(17,22,0,0.01), 0 8px 50px 0 rgba(17,22,0,.01);
                    border-radius: 3px;
                    padding: 10px;"
                >
                    <span style="font-size: 20px; margin-bottom: 5px;">{restaurant_name}</span>
                    <span style="display: block;">
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants/{restaurant_id}/edit">Edit</a>
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants/{restaurant_id}/delete">Delete</a>
                    </span>
                </li>
            '''

            session = create_db_session()
            restaurants = session.query(Restaurant).all()
            restaurants_html = "".join(
                restaurant_html.format(restaurant_name=restaurant.name, restaurant_id=restaurant.id) for restaurant in restaurants
            )
            self.wfile.write(page_html.format(restaurants=restaurants_html).encode())
            return

        # ********************* NEW RESTAURANT *********************
        if self.path.endswith('/restaurants/new'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            page_html = '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>Restaurants</title>
                        <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400" rel="stylesheet">
                    </head>
                    <body style="font-family: 'Open Sans', sans-serif; font-weight: 300; padding: 10px 20px;">
                        <h1>New Restaurant</h1>
                        <form style="margin-bottom: 10px;" method="POST" action="/restaurants/new">
                            <input
                                type="text" name="restaurant_name"
                                style="font-size: 16px;
                                    padding: 5px;
                                    border-radius: 3px;
                                    border: 1px solid lightgray;"
                            >
                            <button
                                type="submit"
                                style="font-size: 16px;
                                    margin: 10px;
                                    background-color: #0083a8;
                                    padding: 5px 10px;
                                    border: 0;
                                    border-radius: 3px;
                                    color: white;
                                    font-weight: 300;"
                            >Create</button>
                        </form>
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants">
                            Home
                        </a>
                    </body>
                </html>
            '''

            self.wfile.write(page_html.encode())
            return

        # ********************* EDIT RESTAURANT *********************
        if self.edit_url_regex.match(self.path): # /restaurants/:id/edit
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            form_html = '''
                <form style="margin-bottom: 10px;" method="POST" action="/restaurants/{id}/edit">
                    <input
                        type="text" name="restaurant_name"
                        placeholder="Enter new name"
                        value="{name}"
                        style="font-size: 16px;
                            padding: 5px;
                            border-radius: 3px;
                            border: 1px solid lightgray;"
                    >
                    <button
                        type="submit"
                        style="font-size: 16px;
                            margin: 10px;
                            background-color: #0083a8;
                            padding: 5px 10px;
                            border: 0;
                            border-radius: 3px;
                            color: white;
                            font-weight: 300;"
                    >Rename</button>
                </form>
            '''

            restaurant_not_found_html = '''
                <p>Sorry, that restaurant does not exist.</p>
            '''

            page_html = '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>Restaurants</title>
                        <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400" rel="stylesheet">
                    </head>
                    <body style="font-family: 'Open Sans', sans-serif; font-weight: 300; padding: 10px 20px;">
                        <h1>{name}</h1>
                        {content}
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants">
                            Home
                        </a>
                    </body>
                </html>
            '''

            id_search = re.search('\d+', self.path)
            id = id_search.group(0)

            session = create_db_session()
            restaurant = session.query(Restaurant).filter_by(id=id)

            if(restaurant.count() > 0):
                content = form_html.format(id=restaurant[0].id, name=restaurant[0].name)
                self.wfile.write(page_html.format(name=restaurant[0].name, content=content).encode())
            else:
                self.wfile.write(page_html.format(name='Not found', content=restaurant_not_found_html).encode())
            return

        # ********************* DELETE RESTAURANT *********************
        if self.delete_url_regex.match(self.path): # /restaurants/:id/delete
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            form_html = '''
                <form style="margin-bottom: 10px;" method="POST" action="/restaurants/{id}/delete">
                    <p>Are you sure you want to delete {name}?</p>
                    <button
                        type="submit"
                        style="font-size: 16px;
                            margin: 10px;
                            background-color: red;
                            padding: 5px 10px;
                            border: 0;
                            border-radius: 3px;
                            color: white;
                            font-weight: 300;"
                    >Delete</button>
                </form>
            '''

            restaurant_not_found_html = '''
                <p>Sorry, that restaurant does not exist.</p>
            '''

            page_html = '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>Restaurants</title>
                        <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400" rel="stylesheet">
                    </head>
                    <body style="font-family: 'Open Sans', sans-serif; font-weight: 300; padding: 10px 20px;">
                        <h1>{name}</h1>
                        {content}
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants">
                            Home
                        </a>
                    </body>
                </html>
            '''

            id_search = re.search('\d+', self.path)
            id = id_search.group(0)

            session = create_db_session()
            restaurant = session.query(Restaurant).filter_by(id=id)

            if(restaurant.count() > 0):
                content = form_html.format(id=restaurant[0].id, name=restaurant[0].name)
                self.wfile.write(page_html.format(name=restaurant[0].name, content=content).encode())
            else:
                self.wfile.write(page_html.format(name='Not found', content=restaurant_not_found_html).encode())
            return
        else:
            self.send_error(404, 'File not found: %s' % self.path)

    def do_POST(self):
        try:
            # ********************* NEW RESTAURANT *********************
            if(self.path.endswith('/restaurants/new')):

                length = int(self.headers.get('Content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)
                if ('restaurant_name' in params):
                    restaurant_name = params['restaurant_name'][0]
                    session = create_db_session()

                    new_restaurant = Restaurant(name = restaurant_name)
                    session.add(new_restaurant)
                    session.commit()

                    self.send_response(303)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                else:
                    self.send_response(303)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

            # ********************* EDIT RESTAURANT *********************
            if self.edit_url_regex.match(self.path):  # /restaurants/:id/edit
                length = int(self.headers.get('Content-length', 0))
                body = self.rfile.read(length).decode()
                params = parse_qs(body)

                if ('restaurant_name' in params):
                    restaurant_name = params['restaurant_name'][0]

                    session = create_db_session()
                    id_search = re.search('\d+', self.path)
                    id = id_search.group(0)
                    restaurant = session.query(Restaurant).filter_by(id=id)

                    if (restaurant.count() > 0):
                        updated_restaurant = restaurant.one()
                        updated_restaurant.name = restaurant_name
                        session.add(updated_restaurant)
                        session.commit()

                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            # ********************* DELETE RESTAURANT *********************
            if self.delete_url_regex.match(self.path):  # /restaurants/:id/delete
                id_search = re.search('\d+', self.path)
                id = id_search.group(0)

                session = create_db_session()
                restaurant = session.query(Restaurant).filter_by(id=id)

                if (restaurant.count() > 0):
                    session.delete(restaurant.one())
                    session.commit()

                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
        except:
            pass

def main():
    try:
        port = 8000
        server_address = ('', port)
        server = HTTPServer(server_address, WebServerHandler)
        print('Web server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C entered, stopping web server')
        server.socket.close()

if __name__ == '__main__':
    main()