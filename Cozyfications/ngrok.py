from pyngrok import ngrok

def run_server():
    print("Starting ngrok server...")
    ngrok.connect(6001)
    tunnels = ngrok.get_tunnels()
    url = tunnels[1].public_url if tunnels[1].public_url.startswith("https://") else tunnels[0].public_url
    print(f"  Started ngrok server at '{url}'")
    return url

def close_server(url):
    ngrok.disconnect(url)
