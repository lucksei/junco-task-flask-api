from flask import Flask, request, jsonify
# from flask_cors import CORS

app = Flask(__name__)

# not safe, move this to env variable in production
# tareita:firulais
API_KEY = "dGFyZWl0YTpmaXJ1bGFpcw=="


@app.route("/ping", methods=["GET"])
def helloWorld():
    # chequeo de autorizacion
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"basic {API_KEY}":
        return jsonify({"message": "Unauthorized"}), 401

    # devolver ping
    return jsonify({
        'ping': 'pong',
    })


@app.route("/run_code", methods=["POST"])
def runCode():
    # chequeo de autorizacion
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"basic {API_KEY}":
        return jsonify({"message": "Unauthorized"}), 401

    # ejecutar codigo python
    try:
        import subprocess
        import re

        result = {}

        python_code = request.data.decode("utf-8")

        # sanitize code, careful, just testing, not production ready
        allowed_functions = ["print", "len", "range"]

        # Remove the imports and froms alltogheter (experimental)
        python_code = re.sub(r'^\s*import\s+', '',
                             python_code, flags=re.MULTILINE)
        python_code = re.sub(r'^\s*from\s+\w+\s+import',
                             '', python_code, flags=re.MULTILINE)

        # Check for disallowed functions and replace them
        for disallowed_function in set(re.findall(r'\b\w+\s*\(', python_code)):
            if disallowed_function.strip('()') not in allowed_functions:
                python_code = python_code.replace(disallowed_function, '')

        # find instances of /install
        for line in python_code.split("\n"):
            if re.match(r'^/install.*', line):
                subprocess.call(
                    ["pip3", "install", "torch"])
                result["torch"] = "installed"
                subprocess.call(
                    ["pip3", "install", "transformers"])
                result["transformers"] = "installed"

        # find instances of /load
        for line in python_code.split("\n"):
            if re.match(r'^/load.*', line):
                result["imports"] = True

        python_code = re.sub(r'^/load.*', 'from transformers import pipeline, Conversation',
                             python_code, flags=re.MULTILINE)

        # find instances of /chat
        new_lines = []
        for line in python_code.split("\n"):
            if re.match(r'^/chat.*', line):
                userInput = re.sub(r'^/chat\s+', '',
                                   line, flags=re.MULTILINE)
                new_lines.append(
                    f"print(pipeline('conversational', model='facebook/blenderbot_small-90M')(Conversation('{userInput}')).generated_responses[-1])")
            else:
                new_lines.append(line)
        python_code = "\n".join(new_lines)

        # python_code = re.sub(r'^/chat.*', 'print(pipeline("conversational", model="facebook/blenderbot_small-90M")(Conversation("Whats your favorite color")).generated_responses[-1])',
        #                      python_code, flags=re.MULTILINE)

        # find instances of "/" and remove them
        python_code = re.sub(r'^/.*', '',
                             python_code, flags=re.MULTILINE)

        # create file
        with open("temp.py", "w") as f:
            f.write(python_code)

        # Execute the code and capture the output
        result["output"] = subprocess.check_output(
            ["python3", "temp.py"], stderr=subprocess.STDOUT, text=True)

        # delete file
        subprocess.call(["rm", "temp.py"])

        # return value as text
        return jsonify(result)
    except subprocess.CalledProcessError as e:
        # If the command fails, e.output will contain stderr
        result["output"] = e.output
        return jsonify(result)
    except Exception as e:
        # If something else fails, e will contain the problem
        result["output"] = e.output
        return jsonify(result)


if __name__ == "__main__":
    app.run()
