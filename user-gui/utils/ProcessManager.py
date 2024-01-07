import subprocess
import threading

class ProcessManager:
    """
    Class that manages the process invocation.

    It controls that no process is invoked twice.
    """

    def __init__(self):
        self.processesRunning = []
        self.threads = []

    def runCommand(
        self,
        cmdName: str,
        cmd: list,
        cmdArgs: dict={},
    ):
        """
        Runs the given cmd in a subprocess.Popen, and then calls the function
        onExit when the subprocess completes.
        cmdName is a string that is the name of the command being run.
        cmd is a list of strings that is the command to run and its arguments.
        cmdArgs is a dict of keyword args to be passed to Popen.
        """
        if cmdName in self.processesRunning:
            return

        def runInThread(cmd, cmdArgs):
            proc = subprocess.Popen(cmd, **cmdArgs)
            proc.wait()
            self.processesRunning.remove(cmdName)
            return
        
        self.processesRunning.append(cmdName)
        thread = threading.Thread(target=runInThread, args=(cmd, cmdArgs))
        thread.start()

        self.joinFinishedThreads()
        self.threads.append(thread)

    def areThreadsAlive(self):
        return len(self.threads) > 0
    
    def joinFinishedThreads(self):
        for thread in self.threads[::]:
            if not thread.is_alive():
                thread.join()
                self.threads.remove(thread)
