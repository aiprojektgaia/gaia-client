from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from typing import Callable


class TimerManager(QObject):
    progress_message_signal = pyqtSignal(dict, name="ProgressMessageSignal")
    timer_started_signal = pyqtSignal(int, name="TimerStartedSignal")
    timer_stopped_signal = pyqtSignal(int, name="TimerStoppedSignal")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timers = {}
        # Status requests run in a nested event loop, during which the timer
        # can fire again. Never start a second poll while one is in flight.
        self._in_flight = set()

    def start_timer(self, project_id: int, callback: Callable, duration: int = 5000):
        print(f"Starting timer for project {project_id}")

        if project_id in self.timers:
            print(f"Timer for project {project_id} already exists")
            return

        self.timers[project_id] = QTimer()
        self.timers[project_id].timeout.connect(
            lambda: self.handle_timer_callback(project_id, callback)
        )
        self.timers[project_id].start(duration)
        self.timer_started_signal.emit(project_id)

    def handle_timer_callback(self, project_id: int, callback: Callable):
        if project_id in self._in_flight:
            print(f"Previous status poll for project {project_id} still running - skipping")
            return
        print(f"Handling timer callback for project {project_id}")
        self._in_flight.add(project_id)
        try:
            response = callback()
        except Exception as e:
            print(f"Error in timer callback for project {project_id}: {e}")
            response = None
        finally:
            self._in_flight.discard(project_id)

        if response is not None:
            self.progress_message_signal.emit(response)
        else:
            self.stop_timer(project_id)

    def stop_timer(self, project_id: int):
        print(f"Stopping timer for project {project_id}")
        if project_id not in self.timers:
            print(
                f"Timer for project {project_id} does not exist (something is wrong?)"
            )
            return

        self.timers[project_id].stop()
        self.timers[project_id].deleteLater()
        del self.timers[project_id]

        self.timer_stopped_signal.emit(project_id)

    def clean_up(self):
        keys = [k for k, v in self.timers.items()]
        for key in keys:
            self.stop_timer(key)
