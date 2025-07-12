from flask import Flask, render_template
import subprocess
import threading
import os

app = Flask(__name__)

# Define your commands with descriptive names
COMMANDS = {
    'Reload Page': 'python press_ctrl_r.py',
    'Page Down': 'python press_pgdn.py',
}

# Global variable to track auto-shift status
auto_shift_active = False
auto_shift_process = None

def run_command(command):
    """Execute a shell command in a separate thread"""
    def target():
        subprocess.run(command, shell=True)
    thread = threading.Thread(target=target)
    thread.start()

@app.route('/')
def dashboard():
    """Render the main dashboard page"""
    return render_template('admin-dashboard.html', commands=COMMANDS.keys(), auto_shift_active=auto_shift_active)

@app.route('/run/<command_name>')
def execute_command(command_name):
    """Endpoint to execute commands"""
    global auto_shift_active, auto_shift_process
    
    if command_name in COMMANDS:
        cmd = COMMANDS[command_name]
        run_command(cmd)
        return f'Executed: {command_name}', 200
    
    return 'Command not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8502, debug=True)
