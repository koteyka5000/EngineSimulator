from tkinter import *
from tkinter.messagebox import showerror
from pygame import mixer
from random import uniform

BG = 'gray60'

all_progress_bars = []
class ProgressBar:
    def __init__(self, window, bg:str, x:int, y:int, lenght:int, max_value:int) -> None:
        all_progress_bars.append(self)

        max_value += 7

        self.window = window
        self.marker_value = 0
        self.value = 0
        self.max_value = max_value
        self.canvas = None

        # 300x200+52+52
        self.canvas = Canvas(window, bg='white', highlightthickness=0)
        self.canvas.place(x=x, y=y, height=20, width=lenght)

        canvas = self.canvas

        canvas.create_rectangle(0, 0, lenght, 20,
                                              fill=bg,
                                              outline='lightgray',
                                              width=4)
        
        self.value_in_pixel = (lenght) / max_value

        self.marker = canvas.create_rectangle(4, 4, 16, 16, fill='purple', width=0)

    def _true_position(self, val):
        return int(self.value_in_pixel * val)
        return val
    
    def _go(self):
        if self._true_position(self.value) < self.marker_value:
            if self._true_position(self.value) < self.marker_value:
                self._move(-1)
                self.marker_value = self.canvas.coords(self.marker)[0]

        elif self._true_position(self.value) > self.marker_value:
            if self._true_position(self.value) > self.marker_value:
                self._move(1)
                self.marker_value = self.canvas.coords(self.marker)[0]
    
    def _move(self, x:int):
        self.canvas.move(self.marker, x, 0)
        self.window.update()
        # self.window.after(5)
    
    def set_value(self, value:int):
        if value > self.max_value - 7:
            self.value = self.max_value - 7
            return
        else:
            self.value = value
            self._go()

    def update_all(self):
        if self.value > self.max_value - 7:
            self.value = self.max_value - 7
            return
        else:
            for progress_bar in all_progress_bars:
                progress_bar._go()

    def reset(self):
        self.marker_value = 0
        self.set_value(0)
        self.canvas.coords(self.marker, 4, 4, 16, 16)

def centerwindow(win):
    """
    💀💀💀💀💀💀💀💀💀💀💀 чт
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

root = Tk()
root.geometry('400x110')
root.title('Симулятор двигателя?')
root['bg'] = BG
root.resizable(False, False)
centerwindow(root)

modes = 'davlenie', 'burn'
mode = 'davlenie'
last_key = None
started = False
running = True 
distance = 0
help_actiavted = False

davlenie_blocked = False
burn_reduce_lock = False

mixer.init()

def playsound(sound):
    if sound == 'stop':
        mixer.music.fadeout(10000)
        print('ss')
        return
    print(13123)
    mixer.music.load(f"{sound}.mp3")
    mixer.music.play(loops=0, fade_ms=200)
 

def increase_davlenie():
    if not davlenie_blocked:
        davlenie = davlenie_progress.value
        davlenie_progress.set_value(davlenie + 2)

def increase_burn():
    if davlenie_progress.value <= 2:
        return
    
    if burn_progress.max_value-7 <= burn_progress.value:
        return
    burn = burn_progress.value
    burn_progress.set_value(burn + 1)
    davlenie_progress.value -= 2

def increase_speed():
    burn = burn_progress.value
    if burn > 2:
        speed = speed_progress.value
        if speed_progress.max_value <= speed:
            return
        speed_progress.value += 1
        burn_progress.value -= 2

def reduce_speed():
    speed = speed_progress.value
    if speed <= 0:
        lose('Машина заглохла')
        return
    speed_progress.set_value(speed-1)

def lose(reason):
    global running, started, last_key, distance
    playsound('death')
    running = False
    showerror('Ты проиграл ахахахахаха', f'Причина: {reason}\nДистанция: {distance} амогусов')
    speed_progress.reset()
    burn_progress.reset()
    davlenie_progress.reset()
    last_key = None
    started = False
    distance = 0
    root.bind(f'<Shift-KeyRelease>', switch_mode)

    davlenie_progress.update_all()
    playsound('stop')
    running = True


def probability(percent):
    return uniform(0, 1) < percent/100
    

def pressed(e=None):
    global last_key

    # if e.keycode == ... #TODO

    if help_actiavted:
        help1_lbl.destroy()

    if e.char == last_key:
        return
    
    last_key = e.char

    if mode == 'davlenie':
        increase_davlenie()
    elif mode == 'burn':
        increase_burn()

def safe_sleep(ms):
    for i in range(ms // ticks_delay):
        run()

def switch_mode(e=None):
    global mode
    root.unbind(f'<Shift-KeyRelease>')
    if mode == 'davlenie':
        mode = 'changing'
        davlenie_lbl.configure(fg=BG)
        burn_lbl.configure(fg='red')
        safe_sleep(1000)
        mode = 'burn'
        burn_lbl.configure(fg='white')
        root.bind(f'<Shift-KeyRelease>', switch_mode)
        
    else:
        mode = 'changing'
        davlenie_lbl.configure(fg='red')
        burn_lbl.configure(fg=BG)
        safe_sleep(1000)
        mode = 'davlenie'
        davlenie_lbl.configure(fg='white')
        root.bind(f'<Shift-KeyRelease>', switch_mode)
    
def every_n_tick(n):
    return ticks % n == 0

def every_n_sec(seconds):
    return ticks % (seconds*1000 / ticks_delay) == 0

def logic():
    global started, distance
    speed = speed_progress.value
    davlenie = davlenie_progress.value
    burn = burn_progress.value

    if speed > 2:
        started = True
    
    if every_n_tick(30):
        increase_speed()

    if every_n_tick(60):
        if started:
            reduce_speed()
    
    if every_n_tick(300):
        distance += 0.1 * speed

        distance *= 10
        distance = int(distance)
        distance /= 10
        if distance >0:
            distance_lbl.configure(font='Arial 15')
            distance_lbl.configure(text=distance)

    if every_n_sec(1):
        if probability(5) or (speed > 10 and probability(12)):
            global davlenie_blocked
            if davlenie_blocked:
                return
            davlenie_progress.set_value(2)
            davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='red')
            davlenie_blocked = True
            for i in range(8):
                safe_sleep(250)
                davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='purple')
                safe_sleep(250)
                davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='red')
            davlenie_blocked = False
            davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='purple')
    
    if every_n_sec(1):
        if probability(5) or (speed > 15 and probability(12)):
            global burn_reduce_lock
            if burn_reduce_lock:
                return
            
            burn_reduce_lock = True
            burn = burn_progress.value
            if burn_progress.value <= 10:
                burn_progress.set_value(0)
            else:
                burn_progress.set_value(burn-10)

            burn_progress.canvas.itemconfig(burn_progress.marker, fill='red')
            for i in range(2):
                safe_sleep(250)
                burn_progress.canvas.itemconfig(burn_progress.marker, fill='purple')
                safe_sleep(250)
                burn_progress.canvas.itemconfig(burn_progress.marker, fill='red')
            burn_progress.canvas.itemconfig(burn_progress.marker, fill='purple')
            burn_reduce_lock = False



    if ticks == 700 and last_key is None:
        global help_actiavted, help1_lbl
        help_actiavted = True
        help1_lbl = Label(text="Управление осуществляется кнопками\nz, x, c, Shift на клавиатуре. Если ничего\nне происходит, переключи раскладку.\nНачни играть чтобы убрать это сообщение", justify='left', font='Arial 15', bg=BG)
        help1_lbl.place(x=1, y=5)

    
            
        

davlenie_lbl = Label(text='<', font='Arial 18', bg=BG, fg='white')
davlenie_lbl.place(x=330, y=38)

burn_lbl = Label(text='<', font='Arial 18', bg=BG, fg=BG)
burn_lbl.place(x=330, y=70)

Label(text="Скорость", font=10, bg=BG).place(x=0, y=7)
Label(text="Давление", font=10, bg=BG).place(x=0, y=40)
Label(text="Сгорание", font=10, bg=BG).place(x=0, y=73)

distance_lbl = Label(text='Расстояние', bg=BG, font="Arial 8")
distance_lbl.place(x=330, y=7)


root.bind(f'<KeyRelease-z>', pressed)
root.bind(f'<KeyRelease-x>', pressed)
root.bind(f'<KeyRelease-c>', pressed)
root.bind(f'<Shift-KeyRelease>', switch_mode)

root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

speed_progress = ProgressBar(root, BG, 80, 10, 250, 30)
davlenie_progress = ProgressBar(root, BG, 80, 43, 250, 100)
burn_progress = ProgressBar(root, BG, 80, 75, 250, 100)

ticks = 0
ticks_delay = 10
def run():
    global ticks
    davlenie_progress.update_all()
    logic()
    root.update()
    root.after(ticks_delay)
    ticks += 1

try:
    while root.winfo_exists():
        if running:
            run()
except Exception as e:
    print(e)