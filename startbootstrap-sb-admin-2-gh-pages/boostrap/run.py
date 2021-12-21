from  __init__ import create_app, socketio
if __name__ == "__main__":
    socketio.run(create_app(), debug=True)                           