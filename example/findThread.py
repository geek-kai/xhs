import psutil
for proc in psutil.process_iter(['pid', 'name', 'num threads']):
    if 'python' in proc.info['name'].lower():
        print(f"Process ID: {proc.info['pid']}, Threads: {proc.info['num threads']}")