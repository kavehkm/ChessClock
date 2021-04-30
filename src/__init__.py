# standard
import tkinter as tk
from threading import Thread, Event
# internal
from src import settings as st


class Clock(Thread):
    """Chess Clock Model"""
    TIMEOUT = 1

    def __init__(self):
        super().__init__(name=self.__class__.__name__, daemon=True)
        self._func = None
        self._args = None
        self._kwargs = None
        self._begin = Event()
        self._end = Event()
        # start Clock Thread
        self.start()

    def connect(self, func, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def begin(self):
        self._end.clear()
        self._begin.set()

    def end(self):
        self._begin.clear()
        self._end.set()

    def run(self):
        while self._begin.wait():
            while not self._end.wait(timeout=self.TIMEOUT):
                if self._func is not None:
                    self._func(*self._args, **self._kwargs)


class Player(object):
    """Chess Player Model"""
    def __init__(self, name, time):
        self.name = name
        self._time = time
        self._remain = time

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time
        self._remain = time

    @property
    def remain(self):
        return self._remain

    def dec(self, val=1):
        r = self._remain - val
        if r >= 0:
            self._remain = r

    def inc(self, val):
        self._remain += val

    def reset(self):
        self._remain = self._time


class Controller(object):
    """Players Controller"""
    WHITE = 1
    BLACK = -1
    # default turn with white player
    DEFAULT_TURN = WHITE

    def __init__(self, app):
        # attach ui
        self._app = app
        # set clock
        self._clock = Clock()
        self._clock.connect(self._tik)
        # create players
        self._players = {
            self.WHITE: Player(**st.get('white')),
            self.BLACK: Player(**st.get('black'))
        }
        # set turn to default
        self._turn = self.DEFAULT_TURN

    def _update_app_clocks(self):
        self._app.set_clocks(*self.players_remain())

    def _change_turn(self):
        self._turn *= -1

    def _tik(self):
        self._players[self._turn].dec()
        self._update_app_clocks()

    def players_remain(self):
        return (
            self._players[self.WHITE].remain,
            self._players[self.BLACK].remain
        )

    def game_is_on(self):
        return all(self.players_remain())

    def move(self):
        self._clock.end()
        if self.game_is_on():
            self._change_turn()
            self._clock.begin()

    def reset(self):
        self._clock.end()
        for player in self._players.values():
            player.reset()
        self._turn = self.DEFAULT_TURN
        self._update_app_clocks()

    def pause(self):
        pass

    def resume(self):
        pass


class App(tk.Tk):
    """Chess Clock App"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller = Controller(self)
        self._bootstrap()

    def _bootstrap(self):
        self._create_ui()
        self._binds()
        self._initialize()

    def _create_ui(self):
        self.title('Chess Clock')
        self.resizable(0, 0)
        self.rowconfigure(0, minsize=300)
        self.rowconfigure(1, minsize=100)
        self.columnconfigure([0, 1], minsize=400)
        # create clocks
        clock_font = ('Helvetica', 72, 'bold')
        self.white_clock = tk.Label(master=self, bg='white', fg='black', font=clock_font)
        self.white_clock.grid(column=0, row=0, sticky=tk.NSEW)
        self.black_clock = tk.Label(master=self, bg='black', fg='white', font=clock_font)
        self.black_clock.grid(column=1, row=0, sticky=tk.NSEW)
        # create names
        name_font = ('Helvetica', 28, 'bold')
        self.white_name = tk.Label(master=self, bg='white', fg='black', font=name_font)
        self.white_name.grid(column=0, row=1, sticky=tk.NSEW)
        self.black_name = tk.Label(master=self, bg='black', fg='white', font=name_font)
        self.black_name.grid(column=1, row=1, sticky=tk.NSEW)

    def _binds(self):
        self.bind('<Key>', self.warkey)

    def _initialize(self):
        white = st.get('white')
        black = st.get('black')
        self.set_clocks(white['time'], black['time'])
        self.set_names(white['name'], black['name'])

    @staticmethod
    def clock_format(t):
        mins, secs = divmod(t, 60)
        return '{:02d}:{:02d}'.format(mins, secs)

    def set_clocks(self, white_time, black_time):
        self.white_clock['text'] = self.clock_format(white_time)
        self.black_clock['text'] = self.clock_format(black_time)

    def set_names(self, white_name, black_name):
        self.white_name['text'] = white_name
        self.black_name['text'] = black_name

    def warkey(self, event):
        if event.char == ' ':
            self._controller.move()
        elif event.char == 'r':
            self._controller.reset()
