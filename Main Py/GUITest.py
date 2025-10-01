from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Rotate
from kivy.core.audio import SoundLoader
import random



Window.size = (800, 600)
Window.resizable = False
Window.fullscreen = False



class ImageButton(ButtonBehavior, Image):
    pass


class ImageCheckbox(ButtonBehavior, Image):
    def __init__(self, active=False, on_state=None, **kwargs):
        super().__init__(**kwargs)
        self.active = active
        self.on_state = on_state
        self.update_image()
        self.bind(on_release=self.toggle)

    def toggle(self, *args):
        self.active = not self.active
        self.update_image()
        if self.on_state:
            self.on_state(self, self.active)

    def update_image(self):
        if self.active:
            self.source = "Assets/Botonotoniocheck.png"
        else:
            self.source = "Assets/Botonotoniovacio.png"


class BorderedBox(BoxLayout):
    def __init__(self, color=(0.8, 0.4, 0.0, 1), border_color=(0.2, 0.1, 0.0, 1), radius=15, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = color
        self.border_color = border_color
        self._radius = radius

        with self.canvas.before:
            Color(*self.border_color)
            self.border = RoundedRectangle(radius=[self._radius])
            Color(*self.bg_color)
            self.bg = RoundedRectangle(radius=[max(self._radius - 3, 0)])

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.border.pos = (self.x - 2, self.y - 2)
        self.border.size = (self.width + 4, self.height + 4)
        self.bg.pos = self.pos
        self.bg.size = self.size


class TodoItem(BoxLayout):
    def __init__(self, text, remove_callback, progress_callback=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=40, **kwargs)

        self.remove_callback = remove_callback
        self.progress_callback = progress_callback

      
        self.checkbox = ImageCheckbox(
            active=False,
            on_state=self.on_checkbox_active,
            size_hint=(None, None),
            size=(60, 40)  
        )
        self.add_widget(self.checkbox)

        
        self.label = Label(text=text, halign="left", valign="middle", color=(1, 1, 1, 1))
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

       
        btn_delete = Image(
            source="Assets/Botonotonio.png",
            size_hint=(None, None),
            size=(60, 40),
            allow_stretch=True
        )
        btn_delete.bind(on_touch_down=self.on_delete_touch)
        self.add_widget(btn_delete)

    def on_checkbox_active(self, instance, value):
        if self.progress_callback:
            self.progress_callback()

    def on_delete_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.remove_item(instance)

    def remove_item(self, instance):
        self.remove_callback(self)
        if self.progress_callback:
            self.progress_callback()


class CustomProgressBar(Widget):
    value = NumericProperty(0)
    max = NumericProperty(1)
    percent_text = StringProperty("0%")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(
            text=self.percent_text,
            font_size=18,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )
        self.add_widget(self.label)
        self.bind(pos=self.redraw, size=self.redraw, value=self.redraw, max=self.redraw)
        self.bind(percent_text=self.update_label)

    def redraw(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            Color(0, 0, 0, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
           
            Color(0.3, 0.12, 0.0, 1)
            RoundedRectangle(pos=(self.x + 3, self.y + 3), size=(self.width - 6, self.height - 6), radius=[20])
            
            percent = 0
            if self.max > 0:
                percent = float(self.value) / float(self.max)
            bar_width = (self.width - 12) * percent
            if percent > 0:
                Color(1.0, 0.6, 0.0, 1)
            else:
                Color(0.3, 0.12, 0.0, 1)
            RoundedRectangle(pos=(self.x + 6, self.y + 6), size=(bar_width, self.height - 12), radius=[20])

        self.percent_text = f"{int(percent * 100)}%"

    def update_label(self, *args):
        self.label.text = self.percent_text
        self.label.size = (self.width, self.height)
        self.label.pos = self.pos
        self.label.halign = "center"
        self.label.valign = "middle"
        self.label.text_size = (self.width, self.height)


class FallingLeaf(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "Assets/Hojaoto.png"
        self.size_hint = (None, None)
        self.size = (48, 48)
        self.x = random.randint(0, Window.width - self.width)
        self.y = Window.height
        self.angle = random.uniform(0, 360)
        self.angular_speed = random.uniform(-1, 1)
        self.speed_y = random.uniform(80, 180)
        self.pos = (self.x, self.y)
        self.bind(pos=self.update_canvas)

    def update(self, dt):
        self.y -= self.speed_y * dt
        self.angle += self.angular_speed
        self.pos = (self.x, self.y)
        if self.y < -self.height:
            if self.parent:
                self.parent.remove_widget(self)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=self.angle, origin=self.center)
        self.canvas.after.clear()
        with self.canvas.after:
            PopMatrix()


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.leaf_layer = FloatLayout(size_hint=(1, 1), pos=(0, 0))

        self.background = Image(
            source="Assets/fondo.png",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(self.background)
        self.add_widget(self.leaf_layer)


        self.todo_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.7, 0.7),
            pos_hint={"center_x": 0.5, "top": 0.95},
            spacing=10
        )


        self.header_box = BorderedBox(
            color=(0.8, 0.4, 0.0, 1),      
            border_color=(0.1, 0.05, 0.0, 1),  
            orientation="vertical",
            size_hint=(1, None),
            height=100,
            padding=10,
            spacing=5
        )


        title_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=2)
        title_row.add_widget(Image(
            source="Assets/Hojaoto.png",
            size_hint=(None, None),
            size=(44, 44),  
            allow_stretch=True,
            keep_ratio=True
        ))
        title_row.add_widget(Label(
            text="TO DO",
            font_size=28,
            size_hint=(1, None),
            height=40,
            bold=True,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        ))
        title_row.add_widget(Image(
            source="Assets/Hojaoto.png",
            size_hint=(None, None),
            size=(44, 44),  
            allow_stretch=True,
            keep_ratio=True
        ))
        self.header_box.add_widget(title_row)


        input_box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=5)
        self.task_input = TextInput(hint_text=" ", multiline=False)


        btn_add = ImageButton(
            source="Assets/Botonotoniosi.png",
            size_hint=(None, 1),
            width=40,
            allow_stretch=True
        )
        btn_add.bind(on_release=self.add_task)

        input_box.add_widget(self.task_input)
        input_box.add_widget(btn_add)
        self.header_box.add_widget(input_box)

        self.todo_box.add_widget(self.header_box)

        self.list_box = BorderedBox(
            color=(0.5, 0.2, 0.0, 0.8),      
            border_color=(0.1, 0.05, 0.0, 1),  
            orientation="vertical",
            size_hint=(1, 1),
            padding=10
        )


        self.scroll = ScrollView(size_hint=(1, 1))
        self.task_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter("height"))
        self.scroll.add_widget(self.task_list)

        self.list_box.add_widget(self.scroll)
        self.todo_box.add_widget(self.list_box)

        self.add_widget(self.todo_box)


        self.progress_box = BorderedBox(
            color=(0.8, 0.4, 0.0, 1),
            border_color=(0.1, 0.05, 0.0, 1),
            orientation="vertical",
            size_hint=(1, None),
            height=110,
            pos_hint={"x": 0, "y": 0},
            padding=10,
            spacing=5,
            radius=0
        )

        self.progress_box.clear_widgets()

        progress_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=48, spacing=2)
        progress_row.add_widget(Image(
            source="Assets/Hojaoto.png",
            size_hint=(None, None),
            size=(44, 44),  
            allow_stretch=True,
            keep_ratio=True
        ))
        progress_row.add_widget(Label(
            text="PROGRESS",
            font_size=24,
            size_hint=(1, None),
            height=48,
            bold=True,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        ))
        progress_row.add_widget(Image(
            source="Assets/Hojaoto.png",
            size_hint=(None, None),
            size=(44, 44), 
            allow_stretch=True,
            keep_ratio=True
        ))
        self.progress_box.add_widget(progress_row)
        self.progress_bar = CustomProgressBar(
            size_hint=(1, None),
            height=40
        )
        self.progress_box.add_widget(self.progress_bar)

        self.add_widget(self.progress_box)

        self.music = SoundLoader.load("Music/Music.mp3")
        self.music_playing = True
        if self.music:
            self.music.loop = True
            self.music.volume = 0.05  
            self.music.play()

        self.music_btn = ImageButton(
            source="Assets/Botonaudio.png",
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"right": 1, "top": 1}
        )
        self.music_btn.bind(on_release=self.toggle_music)
        self.add_widget(self.music_btn)

        Clock.schedule_interval(self.spawn_leaf, 0.7)
        Clock.schedule_interval(self.update_leaves, 1/60.)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        if task_text:
            item = TodoItem(task_text, remove_callback=self.remove_task, progress_callback=self.update_progress)
            self.task_list.add_widget(item)
            self.task_input.text = ""
            self.update_progress()

    def remove_task(self, item):
        self.task_list.remove_widget(item)
        self.update_progress()

    def update_progress(self):
        total = len(self.task_list.children)
        completed = sum(1 for item in self.task_list.children if hasattr(item, "checkbox") and item.checkbox.active)
        self.progress_bar.max = total if total > 0 else 1
        self.progress_bar.value = completed

    def spawn_leaf(self, dt):
        leaf = FallingLeaf()
        self.leaf_layer.add_widget(leaf)

    def update_leaves(self, dt):
        for leaf in list(self.leaf_layer.children):
            if isinstance(leaf, FallingLeaf):
                leaf.update(dt)

    def toggle_music(self, instance):
        if self.music:
            if self.music_playing:
                self.music.stop()
                self.music_btn.source = "Assets/Botonaudiono.png"
                self.music_playing = False
            else:
                self.music.play()
                self.music_btn.source = "Assets/Botonaudio.png"
                self.music_playing = True


class GUIApp(App):
    def build(self):
        self.title = "To Do App"
        return Root()


if __name__ == "__main__":
    GUIApp().run()
