# Copyright (c) 2026 Emberfall. All Rights Reserved.

from bld_modules import WindowModule


window_100x30x260: WindowModule = WindowModule(width=1.0, height=2.6, depth=0.3, opening_width=0.6)
window_200x30x260: WindowModule = WindowModule(width=2.0, height=2.6, depth=0.3)
window_400x30x260: WindowModule = WindowModule(width=4.0, height=2.6, depth=0.3, opening_width=2.0)

assert window_100x30x260.name == "window_100x30x260"
assert window_200x30x260.name == "window_200x30x260"
assert window_400x30x260.name == "window_400x30x260"