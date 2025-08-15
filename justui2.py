import gint
import time
from collections import namedtuple

C_LIGHT = 0xD69A
C_DARK = 0xAD55

# --- Constants from the C implementation ---
J_ALIGN_LEFT = 0
J_ALIGN_CENTER = 1
J_ALIGN_RIGHT = 2
J_ALIGN_TOP = 0
J_ALIGN_MIDDLE = 1
J_ALIGN_BOTTOM = 2
J_BORDER_NONE = 0
J_BORDER_SOLID = 1

# --- Helper Functions and Classes ---

class Font:
    def __init__(self, width, height, line_spacing=2):
        self.char_width = width
        self.line_height = height
        self.line_distance = height + line_spacing

DEFAULT_FONT = Font(8, 12)
VisibleRect = namedtuple('VisibleRect', ['x1', 'y1', 'x2', 'y2'])

class JEvent:
    def __init__(self, type, source=None, **kwargs):
        self.type = type
        self.source = source
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return f"JEvent({attrs})"

# Event Types
JWIDGET_KEY = 0x1000
JWIDGET_FOCUS_CHANGED = 0x1001
JBUTTON_CLICKED = 0x1002
JINPUT_VALIDATED = 0x1003

class JWidget:
    def __init__(self, parent=None):
        self._parent = None
        self._children = []
        self.x, self.y, self.w, self.h = 0, 0, 0, 0
        self.min_w, self.min_h = 0, 0
        self.max_w, self.max_h = 32767, 32767
        self._layout = None
        self.stretch_x, self.stretch_y = 0, 0
        self.visible = True
        self._clipped = False
        self._margins = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._borders = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._padding = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        self._border_color = gint.C_NONE
        self._background_color = gint.C_NONE
        self._dirty, self._update = True, True
        self.focusable = False
        self.is_focused = False
        if parent:
            self.set_parent(parent)

    def set_parent(self, parent):
        if self._parent:
            self._parent.remove_child(self)
        self._parent = parent
        if self._parent:
            self._parent.add_child(self)

    def add_child(self, child):
        if child not in self._children:
            self._children.append(child)
            child._parent = self
            self.mark_dirty()

    def remove_child(self, child):
        if child in self._children:
            self._children.remove(child)
            child._parent = None
            self.mark_dirty()

    def mark_dirty(self):
        self._dirty = True
        if self._parent:
            self._parent.mark_dirty()

    def mark_for_update(self):
        self._update = True
        if self._parent:
            self._parent.mark_for_update()

    def needs_update(self):
        if self._update: return True
        return any(c.visible and c.needs_update() for c in self._children)

    def set_layout(self, layout):
        self._layout = layout
        self.mark_dirty()

    def set_fixed_size(self, w, h):
        self.min_w, self.max_w = w, w
        self.min_h, self.max_h = h, h
        self.mark_dirty()

    def set_padding(self, top, right, bottom, left):
        self._padding = {'top': top, 'right': right, 'bottom': bottom, 'left': left}
        self.mark_dirty()

    def set_border(self, width, color):
        self._borders = {'top': width, 'right': width, 'bottom': width, 'left': width}
        self._border_color = color
        self.mark_dirty()

    def set_background(self, color):
        self._background_color = color
        self.mark_for_update()

    @property
    def content_width(self):
        return self.w - (self._margins['left'] + self._borders['left'] + self._padding['left'] +
                         self._padding['right'] + self._borders['right'] + self._margins['right'])

    @property
    def content_height(self):
        return self.h - (self._margins['top'] + self._borders['top'] + self._padding['top'] +
                         self._padding['bottom'] + self._borders['bottom'] + self._margins['bottom'])

    def _get_full_box_size(self):
        width = (self._margins['left'] + self._borders['left'] + self._padding['left'] +
                 self._padding['right'] + self._borders['right'] + self._margins['right'])
        height = (self._margins['top'] + self._borders['top'] + self._padding['top'] +
                  self._padding['bottom'] + self._borders['bottom'] + self._margins['bottom'])
        return width, height

    def _csize(self):
        max_x, max_y = 0, 0
        for child in self._children:
            if child.visible:
                child._csize()
                max_x = max(max_x, child.x + child.w)
                max_y = max(max_y, child.y + child.h)
        self.w, self.h = max_x, max_y

    def _layout_phase1(self):
        for child in self._children:
            if child.visible:
                child._layout_phase1()
        if self._layout:
            self._layout.csize(self)
        else:
            self._csize()
        geom_w, geom_h = self._get_full_box_size()
        self.w += geom_w
        self.h += geom_h

    def _layout_phase2(self, w, h):
        self.w = max(self.min_w, min(w, self.max_w))
        self.h = max(self.min_h, min(h, self.max_h))
        if self._layout:
            self._layout.apply(self)
        for child in self._children:
            if child.visible:
                child._layout_phase2(child.w, child.h)
        self._dirty = False

    def _render_own_geometry(self, x, y):
        if self._background_color != gint.C_NONE:
            bg_x = x + self._margins['left'] + self._borders['left']
            bg_y = y + self._margins['top'] + self._borders['top']
            bg_w = self.w - (self._margins['left'] + self._margins['right'] + self._borders['left'] + self._borders['right'])
            bg_h = self.h - (self._margins['top'] + self._margins['bottom'] + self._borders['top'] + self._borders['bottom'])
            gint.drect(bg_x, bg_y, bg_x + bg_w - 1, bg_y + bg_h - 1, self._background_color)
        if self._border_color != gint.C_NONE:
            b_x = x + self._margins['left']
            b_y = y + self._margins['top']
            b_w = self.w - (self._margins['left'] + self._margins['right'])
            b_h = self.h - (self._margins['top'] + self._margins['bottom'])
            gint.drect_border(b_x, b_y, b_x + b_w - 1, b_y + b_h - 1, gint.C_NONE, self._borders['top'], self._border_color)

    def _render(self, x, y, visible_rect):
        if not self.visible: return
        self._render_own_geometry(x, y)
        content_x = x + self._margins['left'] + self._borders['left'] + self._padding['left']
        content_y = y + self._margins['top'] + self._borders['top'] + self._padding['top']
        self._render_content(content_x, content_y, visible_rect)
        for child in self._children:
            child._render(content_x + child.x, content_y + child.y, visible_rect)
        self._update = False

    def _render_content(self, x, y, visible_rect): pass
    def _event(self, event): return False
    def handle_event(self, event):
        if self._event(event): return True
        if self._parent: return self._parent.handle_event(event)
        return False
    def on_focus_change(self, is_focused):
        self.is_focused = is_focused
        self.mark_for_update()

class JScene(JWidget):
    def __init__(self):
        super().__init__()
        self.w, self.h = gint.DWIDTH, gint.DHEIGHT
        self._running = False
        self._focused_widget = self

    def set_focus(self, widget):
        if self._focused_widget == widget: return
        if self._focused_widget:
            self._focused_widget.on_focus_change(False)
        self._focused_widget = widget
        if self._focused_widget:
            self._focused_widget.on_focus_change(True)

    def layout(self):
        if not self._dirty: return
        self._layout_phase1()
        self._layout_phase2(self.w, self.h)

    def render(self):
        visible_rect = VisibleRect(0, 0, gint.DWIDTH, gint.DHEIGHT)
        self._render(0, 0, visible_rect)
        gint.dupdate()

    def run(self):
        self._running = True
        while self._running:
            if self._dirty:
                self.layout()
                self.mark_for_update()
            if self.needs_update():
                self.render()
            ev = gint.pollevent()
            if ev.type != gint.KEYEV_NONE:
                if ev.type == gint.KEYEV_DOWN and ev.key == gint.KEY_MENU:
                    self.stop()
                    continue
                if self._focused_widget:
                    event = JEvent(JWIDGET_KEY, source=self._focused_widget, key_event=ev)
                    self._focused_widget.handle_event(event)
            time.sleep_ms(10)

    def stop(self): self._running = False

class BaseBoxLayout:
    def __init__(self, spacing=0): self.spacing = spacing
    def _get_focusable_children(self, widget):
        return [c for c in widget._children if c.visible and c.focusable]
    def _navigate_focus(self, widget, current_focus, direction):
        focusable = self._get_focusable_children(widget)
        if not focusable: return False
        try:
            idx = focusable.index(current_focus)
            new_idx = idx + direction
            if 0 <= new_idx < len(focusable):
                scene = widget
                while not isinstance(scene, JScene): scene = scene._parent
                scene.set_focus(focusable[new_idx])
                return True
        except ValueError:
            scene = widget
            while not isinstance(scene, JScene): scene = scene._parent
            scene.set_focus(focusable[0])
            return True
        return False

class VBoxLayout(BaseBoxLayout):
    def csize(self, widget):
        total_h, max_w = 0, 0
        visible_children = [c for c in widget._children if c.visible]
        if visible_children:
            total_h = (len(visible_children) - 1) * self.spacing
            for child in visible_children:
                max_w = max(max_w, child.w)
                total_h += child.h
        widget.w, widget.h = max_w, total_h
    def apply(self, widget):
        y_pos, content_w = 0, widget.content_width
        for child in widget._children:
            if not child.visible: continue
            child.x = (content_w - child.w) // 2
            child.y = y_pos
            y_pos += child.h + self.spacing
    def handle_event(self, widget, event):
        if event.type == JWIDGET_KEY:
            key = event.key_event.key
            if event.key_event.type in (gint.KEYEV_DOWN, gint.KEYEV_HOLD):
                if key == gint.KEY_UP:
                    return self._navigate_focus(widget, event.source, -1)
                if key == gint.KEY_DOWN:
                    return self._navigate_focus(widget, event.source, 1)
        return False

class HBoxLayout(BaseBoxLayout):
    def csize(self, widget):
        total_w, max_h = 0, 0
        visible_children = [c for c in widget._children if c.visible]
        if visible_children:
            total_w = (len(visible_children) - 1) * self.spacing
            for child in visible_children:
                total_w += child.w
                max_h = max(max_h, child.h)
        widget.w, widget.h = total_w, max_h
    def apply(self, widget):
        x_pos, content_h = 0, widget.content_height
        for child in widget._children:
            if not child.visible: continue
            child.x = x_pos
            child.y = (content_h - child.h) // 2
            x_pos += child.w + self.spacing
    def handle_event(self, widget, event):
        if event.type == JWIDGET_KEY:
            key = event.key_event.key
            if event.key_event.type in (gint.KEYEV_DOWN, gint.KEYEV_HOLD):
                if key == gint.KEY_LEFT:
                    return self._navigate_focus(widget, event.source, -1)
                if key == gint.KEY_RIGHT:
                    return self._navigate_focus(widget, event.source, 1)
        return False

# Add layout event handling to JWidget
JWidget.handle_event = lambda self, event: self._event(event) or (self._layout and self._layout.handle_event(self, event)) or (self._parent and self._parent.handle_event(event))

class JLabel(JWidget):
    def __init__(self, text="", parent=None, font=DEFAULT_FONT):
        super().__init__(parent)
        self.text = text
        self.font = font
        self.color = gint.C_BLACK
        self._lines = []
    def _csize(self):
        self._lines = self._wrap_text(self.text, self.w or gint.DWIDTH)
        if not self._lines: self.w, self.h = 0, 0; return
        max_line_width = max(len(line) * self.font.char_width for line in self._lines)
        self.w, self.h = max_line_width, len(self._lines) * self.font.line_height
    def _wrap_text(self, text, max_width):
        lines = []
        max_width = max(max_width, self.font.char_width)
        for paragraph in text.split('\n'):
            words, current_line = paragraph.split(' '), ""
            for word in words:
                word_width = len(word) * self.font.char_width
                if word_width > max_width:
                    if current_line: lines.append(current_line); current_line = ""
                    temp_word = ""
                    for char in word:
                        if (len(temp_word) + 1) * self.font.char_width > max_width:
                            lines.append(temp_word); temp_word = char
                        else: temp_word += char
                    current_line = temp_word
                else:
                    separator = ' ' if current_line else ''
                    if (len(current_line) + len(separator) + len(word)) * self.font.char_width > max_width:
                        lines.append(current_line); current_line = word
                    else: current_line += separator + word
            lines.append(current_line)
        return lines
    def _render_content(self, x, y, visible_rect):
        self._lines = self._wrap_text(self.text, self.content_width)
        line_y = y
        for line in self._lines:
            if line_y + self.font.line_height > visible_rect.y1 and line_y < visible_rect.y2:
                gint.dtext(x, line_y, self.color, line)
            line_y += self.font.line_height

class JButton(JLabel):
    def __init__(self, text="", on_click=None, parent=None):
        super().__init__(text, parent)
        self.on_click = on_click
        self.focusable = True
        self.set_padding(2, 5, 2, 5)
        self.set_border(1, gint.C_BLACK)
    def _render_content(self, x, y, visible_rect):
        fg, bg = (gint.C_BLACK, gint.C_WHITE)
        if self.is_focused:
            fg, bg = gint.C_WHITE, gint.C_BLACK
        gint.drect(x, y, x + self.content_width -1, y + self.content_height -1, bg)
        text_x = x + (self.content_width - len(self.text) * self.font.char_width) // 2
        text_y = y + (self.content_height - self.font.line_height) // 2
        gint.dtext(text_x, text_y, fg, self.text)
    def _event(self, event):
        if event.type == JWIDGET_KEY and self.is_focused:
            if event.key_event.type == gint.KEYEV_DOWN and event.key_event.key == gint.KEY_EXE:
                if self.on_click:
                    self.on_click(self)
                # Propagate a generic click event
                if self._parent: self._parent.handle_event(JEvent(JBUTTON_CLICKED, source=self))
                return True
        return False

class JFrame(JWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_x, self._scroll_y = 0, 0
        self._clipped = True
        self.set_border(1, gint.C_BLACK)
    def _render(self, x, y, parent_visible_rect):
        if not self.visible: return
        self._render_own_geometry(x, y)
        if not self._children: return
        child = self._children[0]
        content_x = x + self._margins['left'] + self._borders['left'] + self._padding['left']
        content_y = y + self._margins['top'] + self._borders['top'] + self._padding['top']
        content_w, content_h = self.content_width, self.content_height
        frame_visible_rect = VisibleRect(max(content_x, parent_visible_rect.x1), max(content_y, parent_visible_rect.y1),
                                         min(content_x + content_w, parent_visible_rect.x2), min(content_y + content_h, parent_visible_rect.y2))
        child._render(content_x - self._scroll_x, content_y - self._scroll_y, frame_visible_rect)
        self._render_scrollbars(content_x, content_y, content_w, content_h, child)
        self._update = False
    def _render_scrollbars(self, x, y, w, h, child):
        sw = 4
        if child.h > h:
            sh = max(10, h * h // child.h)
            sy = y + (self._scroll_y * (h - sh) // (child.h - h))
            sx = x + w - sw
            gint.drect(sx, y, sx + sw - 1, y + h - 1, C_LIGHT)
            gint.drect(sx, sy, sx + sw - 1, sy + sh - 1, C_DARK)
    def _event(self, event):
        if event.type != JWIDGET_KEY: return False
        ev = event.key_event
        if ev.type in (gint.KEYEV_DOWN, gint.KEYEV_HOLD):
            if ev.key == gint.KEY_UP:
                self._scroll_y = max(0, self._scroll_y - 10)
                self.mark_for_update(); return True
            if ev.key == gint.KEY_DOWN:
                if self._children:
                    max_scroll = max(0, self._children[0].h - self.content_height)
                    self._scroll_y = min(max_scroll, self._scroll_y + 10)
                    self.mark_for_update(); return True
        return False

def keymap_translate(key, shift, alpha):
    key_map = {
        gint.KEY_7: '7', gint.KEY_8: '8', gint.KEY_9: '9',
        gint.KEY_4: '4', gint.KEY_5: '5', gint.KEY_6: '6',
        gint.KEY_1: '1', gint.KEY_2: '2', gint.KEY_3: '3',
        gint.KEY_0: '0', gint.KEY_DOT: '.', gint.KEY_ADD: '+', gint.KEY_SUB: '-',
        gint.KEY_MUL: '*', gint.KEY_DIV: '/', gint.KEY_LEFTP: '(', gint.KEY_RIGHTP: ')',
        gint.KEY_COMMA: ',', gint.KEY_NEG: '-', gint.KEY_EXP: 'E',
    }
    alpha_map = {
        gint.KEY_XOT: 'X', gint.KEY_LOG: 'Y', gint.KEY_LN: 'Z', gint.KEY_SIN: '[', gint.KEY_COS: ']', gint.KEY_TAN: '{',
        gint.KEY_FRAC: '}', gint.KEY_FD: '"', gint.KEY_LEFTP: 'A', gint.KEY_RIGHTP: 'B', gint.KEY_COMMA: 'C', gint.KEY_ARROW: 'D',
        gint.KEY_7: 'E', gint.KEY_8: 'F', gint.KEY_9: 'G',
        gint.KEY_4: 'H', gint.KEY_5: 'I', gint.KEY_6: 'J',
        gint.KEY_1: 'K', gint.KEY_2: 'L', gint.KEY_3: 'M',
        gint.KEY_0: 'N', gint.KEY_DOT: 'O', gint.KEY_EXP: 'P', gint.KEY_NEG: 'Q',
    }
    if alpha:
        char = alpha_map.get(key, '')
        if not shift: return char.lower()
        return char
    if shift:
        return {gint.KEY_0: ' ', gint.KEY_DOT: ':', gint.KEY_ADD: ';', gint.KEY_SUB: '!'}.get(key, '')
    return key_map.get(key, '')

class JInput(JWidget):
    def __init__(self, text="", parent=None, font=DEFAULT_FONT):
        super().__init__(parent)
        self.text = text
        self.font = font
        self.color = gint.C_BLACK
        self.cursor_pos = len(text)
        self.scroll_offset = 0
        self.focusable = True
        self.set_padding(2, 4, 2, 4)
        self.set_border(1, gint.C_BLACK)
    def _csize(self):
        self.w = 120  # Default width
        self.h = self.font.line_height
    def _render_content(self, x, y, visible_rect):
        if self.is_focused:
            gint.drect(x, y, x + self.content_width - 1, y + self.content_height - 1, gint.C_WHITE)
            gint.drect_border(x-1, y-1, x + self.content_width, y + self.content_height, gint.C_NONE, 1, gint.C_BLACK)
        
        # Adjust scroll offset to keep cursor in view
        cursor_x_pos = self.cursor_pos * self.font.char_width
        if cursor_x_pos < self.scroll_offset:
            self.scroll_offset = cursor_x_pos
        if cursor_x_pos > self.scroll_offset + self.content_width - self.font.char_width:
            self.scroll_offset = cursor_x_pos - self.content_width + self.font.char_width
        
        # Draw visible portion of text
        start_char = self.scroll_offset // self.font.char_width
        num_chars = self.content_width // self.font.char_width + 1
        visible_text = self.text[start_char : start_char + num_chars]
        gint.dtext(x, y, self.color, visible_text)
        
        # Draw cursor
        if self.is_focused:
            cursor_draw_x = x + cursor_x_pos - self.scroll_offset
            gint.dvline(cursor_draw_x, self.color)
    def _event(self, event):
        if not (self.is_focused and event.type == JWIDGET_KEY): return False
        ev = event.key_event
        if ev.type != gint.KEYEV_DOWN: return False
        
        key, shift, alpha = ev.key, ev.shift, ev.alpha
        
        if key == gint.KEY_LEFT: self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == gint.KEY_RIGHT: self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
        elif key == gint.KEY_DEL:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key == gint.KEY_EXE:
            if self._parent: self._parent.handle_event(JEvent(JINPUT_VALIDATED, source=self))
        else:
            char = keymap_translate(key, shift, alpha)
            if char:
                self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                self.cursor_pos += 1
        self.mark_for_update()
        return True

class JTextField(JFrame):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.label = JLabel(text, parent=self)
        # self.label.set_stretch(1, 0)
        self.focusable = True # The frame itself can be focused to scroll
    @property
    def text(self): return self.label.text
    @text.setter
    def text(self, value):
        self.label.text = value
        self.label.mark_dirty()
        self.mark_for_update()
    def on_focus_change(self, is_focused):
        super().on_focus_change(is_focused)
        if is_focused:
            self.set_border(1, C_DARK)
        else:
            self.set_border(1, gint.C_BLACK)

# --- Example Usage ---

def main():
    scene = JScene()
    scene.set_background(C_LIGHT)
    
    # Main container using a vertical layout
    main_container = JWidget(parent=scene)
    main_container.set_layout(VBoxLayout(spacing=5))
    main_container.set_padding(5, 5, 5, 5)

    def on_my_button_click(button):
        button.text = "Clicked!"
        button.mark_dirty()

    # Horizontal box for buttons
    button_box = JWidget(parent=main_container)
    button_box.set_layout(HBoxLayout(spacing=10))
    
    button1 = JButton("Button 1", on_click=on_my_button_click, parent=button_box)
    button2 = JButton("Button 2", on_click=on_my_button_click, parent=button_box)
    
    # Input field
    input_field = JInput("Edit me", parent=main_container)

    # Multi-line text field
    long_text = ("This is a JTextField. It combines a JFrame and a JLabel to create a scrollable, "
                 "word-wrapping text area. You can focus it with the navigation keys and then "
                 "word-wrapping text area. You can focus it with the navigation keys and then "
                 "word-wrapping text area. You can focus it with the navigation keys and then "
                 "word-wrapping text area. You can focus it with the navigation keys and then "
                 "word-wrapping text area. You can focus it with the navigation keys and then "
                 "scroll using UP and DOWN.")
    text_field = JTextField(long_text, parent=main_container)
    text_field.set_fixed_size(380, 80)

    # Set initial focus
    scene.set_focus(text_field)
    
    scene.run()

    gint.dclear(gint.C_WHITE)
    gint.dtext(10, 10, gint.C_BLACK, "Application finished.")
    gint.dupdate()
    time.sleep_ms(1000)

if __name__ == "__main__":
    main()