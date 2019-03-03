import http.server
import webbrowser

def start_server(port):
    # Open website in default browser
    print("Hosting in default webbrowser on: "+"http://localhost:"+str(port))
    webbrowser.open("http://localhost:"+str(port))

    # Open HTTP-server
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    print("Starting http server")
    httpd.serve_forever()


if __name__ == "__main__":
    start_server(8000)