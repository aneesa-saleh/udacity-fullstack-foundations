from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

def create_db_session():
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    return DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
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
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="#">Edit</a>
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="#">Delete</a>
                    </span>
                </li>
            '''

            session = create_db_session()
            restaurants = session.query(Restaurant).all()
            restaurants_html = "".join(
                restaurant_html.format(restaurant_name=restaurant.name) for restaurant in restaurants
            )
            self.wfile.write(page_html.format(restaurants=restaurants_html).encode())
            return
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
                        <form method="POST" action="/restaurants/new/create">
                            <input type="text" name="restaurant_name">
                            <button type="submit">Create</button>
                        </form>
                        <a style="color: #0083a8; margin: 5px; font-weight: 400;" href="/restaurants">
                            Home
                        </a>
                    </body>
                </html>
            '''
            self.wfile.write(page_html.encode())
            return
        else:
            self.send_error(404, 'File not found: %s' % self.path)

    def do_POST(self):
        try:
            if(self.path.endswith('/restaurants/new/create')):

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