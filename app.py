import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EXECUTABLE_PATH = 'E://Training//rust//snoflake_connector_rs//connector//target//debug//connector.exe'


@app.route('/run-executable', methods=['POST'])
def run_executable():
    if not os.path.exists(EXECUTABLE_PATH):
        return jsonify({'error': f'Executable not found at {EXECUTABLE_PATH}'}),
    # Get the data from the frontend request
    data = request.get_json()
    usrername = data.get('username')
    password = data.get('password')
    arg = data.get('arg')
    output = ""
    error = ""

    # if arg not in ['create', 'query']:
    #     return jsonify({'error': 'Invalid argument selected. Must be "create" or "query".'}), 400

    # Initialize command based on the argument
    command = [EXECUTABLE_PATH, usrername, password, arg]

    try:
        # Start the executable with the command-line argument
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Now based on the argument, get the required additional input
        if arg == 'create':
            create_query = data.get('createQuery')
            insert_query = data.get('insertQuery')
            if not create_query or not insert_query:
                return jsonify({'error': 'Both Create and Insert queries are required.'}), 400
            user_input_data = f"{create_query}\n{insert_query}\n"
        elif arg == 'query':
            query = data.get('query')
            if not query:
                return jsonify({'error': 'Query input is required.'}), 400
            user_input_data = f"{query}\n"

        # Pass the user input (queries) to the executable
        stdout, stderr = process.communicate(input=user_input_data.encode())

        # Check the process output or error
        if process.returncode == 0:
            output = stdout.decode('utf-8')
        else:
            error = stderr.decode('utf-8')

    except Exception as e:
        error = str(e)

    # Return the output or error
    if output:
        return jsonify({'output': output})
    else:
        return jsonify({'error': error}), 500

if __name__ == '__main__':
    app.run(debug=True)