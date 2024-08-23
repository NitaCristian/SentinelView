import subprocess

if __name__ == "__main__":
    scripts = ['api/app.py', 'desktop_app/main.py', 'web_app/app.py']
    processes = []

    for script in scripts:
        process = subprocess.Popen(["python", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(process)

    for process in processes:
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(f"{process.args[1]} completed successfully.")
            print(stdout.decode())
        else:
            print(f"Error running {process.args[1]}.")
            print(stderr.decode())
