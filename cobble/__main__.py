from logging import basicConfig, INFO, Formatter
from time import gmtime
from tkinter import Tk

from .__init__ import Wrapper

# Logging config
basicConfig(
    level=INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="[%Y-%m-%dT%H:%M:%SZ]"
)
Formatter.converter = gmtime

window = Tk()
# Make the window expand to fit displayed content
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

wrapper = Wrapper(window)
wrapper.render().grid(sticky="nswe")
window.mainloop()
