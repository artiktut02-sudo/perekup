from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
import random

Window.clearcolor = (0.1, 0.1, 0.12, 1)

# ---------- Данные ----------
PARTS = {
    "screen":  {"name": "Экран",     "price": 3000, "boost": 4000},
    "battery": {"name": "Батарея",   "price": 1500, "boost": 2500},
    "case":    {"name": "Корпус",    "price": 1000, "boost": 1800},
}

MODELS = ["iPhone 11", "Samsung S20", "Xiaomi Redmi", "Pixel 5", "OnePlus 8"]

class Phone:
    def __init__(self):
        self.model = random.choice(MODELS)
        self.base_price = random.randint(2000, 8000)   # цена на "Авито"
        self.broken = random.sample(list(PARTS.keys()), k=random.randint(1, 2))
        self.fixed = []
        self.asking_price = self.base_price  # текущая стоимость
        self.sold_for = 0

    def value(self):
        # базовая цена + стоимость починенных деталей
        v = self.base_price
        for p in self.fixed:
            v += PARTS[p]["boost"]
        return v

    def is_fixed(self):
        return set(self.broken) <= set(self.fixed)

    def broken_names(self):
        return ", ".join(PARTS[p]["name"] for p in self.broken)

# ---------- Главный интерфейс ----------
class Game(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=8, **kwargs)
        self.money = 20000
        self.inventory = []          # купленные телефоны
        self.market = [Phone() for _ in range(5)]

        # верхняя панель
        self.top = Label(text=f"💰 {self.money} ₽", size_hint=(1, 0.08),
                         font_size=20, bold=True)
        self.add_widget(self.top)

        # список объявлений
        self.market_box = GridLayout(cols=1, spacing=6, size_hint_y=None)
        self.market_box.bind(minimum_height=self.market_box.setter('height'))
        sv = ScrollView(size_hint=(1, 0.45))
        sv.add_widget(self.market_box)
        self.add_widget(sv)

        # инвентарь
        self.inv_label = Label(text="Твои телефоны:", size_hint=(1, 0.06),
                               font_size=16)
        self.add_widget(self.inv_label)
        self.inv_box = GridLayout(cols=1, spacing=6, size_hint_y=None)
        self.inv_box.bind(minimum_height=self.inv_box.setter('height'))
        sv2 = ScrollView(size_hint=(1, 0.35))
        sv2.add_widget(self.inv_box)
        self.add_widget(sv2)

        self.refresh()

    def refresh(self):
        self.top.text = f"💰 {self.money} ₽"

        # рынок
        self.market_box.clear_widgets()
        for i, p in enumerate(self.market):
            b = Button(text=f"{p.model}\nЦена: {p.asking_price} ₽\nПоломки: {p.broken_names()}",
                       size_hint_y=None, height=80)
            b.bind(on_press=lambda inst, idx=i: self.buy(idx))
            self.market_box.add_widget(b)

        # инвентарь
        self.inv_box.clear_widgets()
        for i, p in enumerate(self.inventory):
            status = "✅ Готов к продаже" if p.is_fixed() else f"🔧 Сломано: {', '.join(PARTS[x]['name'] for x in p.broken if x not in p.fixed)}"
            b = Button(text=f"{p.model}\nСтоимость: {p.value()} ₽\n{status}",
                       size_hint_y=None, height=80)
            b.bind(on_press=lambda inst, idx=i: self.open_phone(idx))
            self.inv_box.add_widget(b)

    # ---------- Действия ----------
    def buy(self, idx):
        p = self.market[idx]
        if self.money < p.asking_price:
            self.popup("Не хватает денег")
            return
        self.money -= p.asking_price
        self.inventory.append(p)
        self.market.pop(idx)
        self.market.append(Phone())   # новое объявление
        self.refresh()

    def open_phone(self, idx):
        p = self.inventory[idx]
        content = BoxLayout(orientation="vertical", spacing=6, padding=6)

        content.add_widget(Label(text=f"{p.model}\nТекущая стоимость: {p.value()} ₽",
                                 size_hint=(1, 0.2)))

        # «виртуальный стол»: кнопки установки деталей
        table = GridLayout(cols=3, spacing=4, size_hint=(1, 0.5))
        for key, info in PARTS.items():
            if key in p.fixed:
                table.add_widget(Label(text=f"{info['name']}\n✅ стоит"))
            else:
                b = Button(text=f"{info['name']}\n{info['price']} ₽")
                b.bind(on_press=lambda inst, k=key, ph=p, popup=None: self.install_part(ph, k, content))
                table.add_widget(b)
        content.add_widget(table)

        # продажа
        sell_btn = Button(text=f"Продать за {p.value()} ₽", size_hint=(1, 0.15))
        sell_btn.bind(on_press=lambda inst: self.sell(p, popup))
        content.add_widget(sell_btn)

        popup = Popup(title="Виртуальный стол ремонта", content=content,
                      size_hint=(0.9, 0.8))
        # сохраним ссылку для обновления
        self._current_popup = popup
        self._current_phone = p
        popup.open()

    def install_part(self, phone, part_key, content):
        info = PARTS[part_key]
        if self.money < info["price"]:
            self.popup("Не хватает денег на деталь")
            return
        self.money -= info["price"]
        phone.fixed.append(part_key)
        self.refresh()
        self._current_popup.dismiss()
        # переоткрываем стол, чтобы обновить вид
        idx = self.inventory.index(phone)
        self.open_phone(idx)

    def sell(self, phone, popup):
        if not phone.is_fixed():
            self.popup("Сначала почини все поломки!")
            return
        self.money += phone.value()
        phone.sold_for = phone.value()
        self.inventory.remove(phone)
        popup.dismiss()
        self.refresh()

    def popup(self, text):
        Popup(title="Инфо", content=Label(text=text),
              size_hint=(0.7, 0.3)).open()

class PhoneFlipper(App):
    def build(self):
        return Game()

if __name__ == "__main__":
    PhoneFlipper().run()
