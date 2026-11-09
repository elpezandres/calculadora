"""COSTIFY - Calculadora de costos y presupuestos para Windows y Android."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle

BG = (0.953, 0.965, 0.984, 1)
PANEL = (1, 1, 1, 1)
NAVY = (0.09, 0.14, 0.23, 1)
BLUE = (0.22, 0.47, 0.91, 1)
BLUE_DARK = (0.15, 0.35, 0.72, 1)
TEXT = (0.09, 0.14, 0.23, 1)
MUTED = (0.40, 0.46, 0.54, 1)
GREEN = (0.08, 0.55, 0.39, 1)
RED = (0.82, 0.20, 0.20, 1)


def money(value):
    value = Decimal(str(value)).quantize(Decimal('1'))
    return '$' + f'{int(value):,}'.replace(',', '.')


def parse_number(value, label, allow_zero=True):
    raw = str(value).strip().replace('$', '').replace(' ', '')
    # Formato colombiano: 3.000.000; también acepta decimales con coma.
    if '.' in raw and ',' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif raw.count('.') > 1:
        raw = raw.replace('.', '')
    elif ',' in raw:
        raw = raw.replace(',', '.')
    if not raw:
        raise ValueError(f'Ingresa el dato: {label}.')
    try:
        number = Decimal(raw)
    except InvalidOperation:
        raise ValueError(f'El valor de «{label}» no es válido.')
    if not number.is_finite():
        raise ValueError(f'El valor de «{label}» no es válido.')
    if number < 0 or (not allow_zero and number == 0):
        condition = 'mayor que cero' if not allow_zero else 'igual o mayor que cero'
        raise ValueError(f'«{label}» debe ser {condition}.')
    return number


class RoundedPanel(BoxLayout):
    def __init__(self, color=PANEL, radius=12, **kwargs):
        super().__init__(**kwargs)
        self._panel_color = color
        self._radius = radius
        with self.canvas.before:
            self._color_instruction = Color(*color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class CostifyApp(App):
    title = 'COSTIFY | Calculadora de costos'

    def build(self):
        Window.clearcolor = BG
        self.manager = ScreenManager()
        self.show_home()
        return self.manager

    def label(self, text, size=14, color=TEXT, bold=False, height=None, align='left'):
        return Label(text=text, font_size=sp(size), color=color, bold=bold,
                     size_hint_y=None, height=dp(height or max(30, size * 2.1)),
                     halign=align, valign='middle', text_size=(None, None))

    def button(self, text, callback, primary=True, height=46):
        b = Button(text=text, size_hint_y=None, height=dp(height),
                   background_normal='', background_down='',
                   background_color=BLUE if primary else (0.90, 0.93, 0.97, 1),
                   color=(1, 1, 1, 1) if primary else BLUE_DARK,
                   bold=True, font_size=sp(14))
        b.bind(on_release=lambda *_: callback())
        return b

    def field(self, parent, label, default=''):
        parent.add_widget(self.label(label, 12, MUTED, True, 25))
        inp = TextInput(text=default, multiline=False, size_hint_y=None, height=dp(46),
                        font_size=sp(16), padding=(dp(12), dp(12)),
                        background_normal='', background_active='',
                        background_color=(0.95, 0.97, 0.99, 1), foreground_color=TEXT,
                        cursor_color=BLUE)
        parent.add_widget(inp)
        parent.add_widget(self.label('', 5, MUTED, height=8))
        return inp

    def result_panel(self, parent, title):
        panel = RoundedPanel(orientation='vertical', size_hint_y=None, height=dp(112),
                             padding=dp(14), spacing=dp(4), color=(0.92, 0.96, 1, 1))
        panel.add_widget(self.label(title.upper(), 10, BLUE_DARK, True, 22))
        value = self.label('—', 23, TEXT, True, 38)
        detail = self.label('', 11, MUTED, False, 44)
        detail.bind(texture_size=lambda w, s: setattr(w, 'height', max(dp(35), s[1])))
        panel.add_widget(value)
        panel.add_widget(detail)
        parent.add_widget(panel)
        return value, detail

    def base_screen(self, title):
        screen = Screen(name=title)
        root = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
        with root.canvas.before:
            Color(*BG)
            root.bg_rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        root.bind(pos=lambda w, p: setattr(w.bg_rect, 'pos', p),
                  size=lambda w, s: setattr(w.bg_rect, 'size', s))
        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        if title != 'Inicio':
            header.add_widget(self.button('‹ Inicio', self.show_home, False, 42))
        header.add_widget(self.label('COSTIFY', 18, NAVY, True, 42))
        root.add_widget(header)
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=(0, dp(4), 0, dp(18)))
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content)
        root.add_widget(scroll)
        nav = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(5))
        for name, short in [('Costo total','Costo'), ('Margen de contribución','Margen'), ('Utilidad','Utilidad'), ('Punto de equilibrio','Equilibrio'), ('Presupuesto','Presup.')]:
            nav.add_widget(self.button(short, lambda n=name: self.show_module(n), False, 48))
        root.add_widget(nav)
        screen.add_widget(root)
        self.manager.add_widget(screen)
        return content

    def show_home(self):
        if 'Inicio' in self.manager.screen_names:
            self.manager.remove_widget(self.manager.get_screen('Inicio'))
        content = self.base_screen('Inicio')
        content.add_widget(self.label('Bienvenido a COSTIFY', 22, TEXT, True, 42))
        intro = self.label('Calcula costos, analiza la rentabilidad y prepara presupuestos desde tu computador o celular.', 13, MUTED, False, 58)
        intro.text_size = (Window.width - dp(48), None)
        content.add_widget(intro)
        modules = [
            ('01  Costo total', 'Costos fijos + costos variables', 'Costo total'),
            ('02  Margen de contribución', 'Margen total y porcentual', 'Margen de contribución'),
            ('03  Utilidad', 'Utilidad antes y después de impuestos', 'Utilidad'),
            ('04  Punto de equilibrio', 'Unidades, pesos y margen de seguridad', 'Punto de equilibrio'),
            ('05  Presupuesto', 'Unidades necesarias para la utilidad objetivo', 'Presupuesto'),
        ]
        for heading, desc, module in modules:
            card = RoundedPanel(orientation='vertical', size_hint_y=None, height=dp(105), padding=dp(13), spacing=dp(4))
            card.add_widget(self.label(heading, 15, TEXT, True, 28))
            card.add_widget(self.label(desc, 11, MUTED, False, 25))
            card.add_widget(self.button('Abrir módulo  →', lambda m=module: self.show_module(m), False, 36))
            content.add_widget(card)
        self.manager.current = 'Inicio'

    def show_module(self, module):
        if module in self.manager.screen_names:
            self.manager.remove_widget(self.manager.get_screen(module))
        content = self.base_screen(module)
        builders = {
            'Costo total': self.module_cost,
            'Margen de contribución': self.module_margin,
            'Utilidad': self.module_profit,
            'Punto de equilibrio': self.module_break_even,
            'Presupuesto': self.module_budget,
        }
        content.add_widget(self.label(module, 21, TEXT, True, 42))
        builders[module](content)
        self.manager.current = module

    def form_card(self, content, title, description):
        content.add_widget(self.label(title, 16, TEXT, True, 30))
        desc = self.label(description, 11, MUTED, False, 48)
        desc.text_size = (Window.width - dp(50), None)
        content.add_widget(desc)
        card = RoundedPanel(orientation='vertical', size_hint_y=None, height=None,
                            padding=dp(14), spacing=dp(7))
        card.bind(minimum_height=card.setter('height'))
        content.add_widget(card)
        return card

    def calculate_button(self, card, text, callback):
        card.add_widget(self.button(text, callback, True, 48))

    def error(self, exc):
        self.show_result_dialog('Revisa los datos', str(exc))

    def show_result_dialog(self, title, message):
        from kivy.uix.popup import Popup
        body = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))
        lbl = Label(text=message, color=TEXT, font_size=sp(14), halign='left', valign='middle')
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', (s[0], None)))
        body.add_widget(lbl)
        body.add_widget(self.button('Aceptar', lambda: popup.dismiss(), True))
        popup = Popup(title=title, content=body, size_hint=(0.88, None), height=dp(230))
        popup.open()

    def module_cost(self, content):
        card = self.form_card(content, 'Costo total', 'CT = CF + (CVu × Q). Suma los costos fijos y los costos variables de todas las unidades.')
        cf = self.field(card, 'Costos fijos (CF) - COP', '3000000')
        cvu = self.field(card, 'Costo variable unitario (CVu) - COP', '20000')
        q = self.field(card, 'Cantidad de unidades (Q)', '200')
        value, detail = self.result_panel(card, 'Costo total (CT)')
        def calc():
            try:
                fixed = parse_number(cf.text, 'Costos fijos'); variable = parse_number(cvu.text, 'Costo variable unitario'); qty = parse_number(q.text, 'Cantidad de unidades')
                variable_total = variable * qty; total = fixed + variable_total
                value.text = money(total); detail.text = f'Costo variable total: {money(variable_total)}\nCostos fijos: {money(fixed)}'
            except ValueError as e: self.error(e)
        self.calculate_button(card, 'Calcular costo total', calc)

    def module_margin(self, content):
        card = self.form_card(content, 'Margen de contribución', 'MCT = Ventas totales − Costos variables totales. MC% = (MCT ÷ Ventas) × 100.')
        pv = self.field(card, 'Precio de venta unitario (PVu) - COP', '50000'); cvu = self.field(card, 'Costo variable unitario (CVu) - COP', '20000'); q = self.field(card, 'Unidades vendidas (Q)', '200')
        value, detail = self.result_panel(card, 'Margen de contribución total (MCT)')
        def calc():
            try:
                price = parse_number(pv.text, 'Precio de venta unitario', False); variable = parse_number(cvu.text, 'Costo variable unitario'); qty = parse_number(q.text, 'Unidades vendidas')
                if price <= variable: raise ValueError('El precio de venta debe ser mayor que el costo variable unitario.')
                sales = price * qty; variable_total = variable * qty; mct = sales - variable_total
                value.text = money(mct); value.color = GREEN
                detail.text = f'Ventas totales: {money(sales)}\nCostos variables: {money(variable_total)}\nMCu: {money(price-variable)}  |  MC%: {(mct/sales*100 if sales else Decimal(0)):.2f}%'
            except ValueError as e: self.error(e)
        self.calculate_button(card, 'Calcular margen de contribución', calc)

    def module_profit(self, content):
        card = self.form_card(content, 'Utilidad y utilidad neta', 'Utilidad = Margen de contribución total − Costos fijos. Utilidad neta = Utilidad − Impuestos.')
        pv = self.field(card, 'Precio de venta unitario (PVu) - COP', '50000'); q = self.field(card, 'Unidades vendidas (Q)', '200'); cvu = self.field(card, 'Costo variable unitario (CVu) - COP', '20000'); cf = self.field(card, 'Costos fijos (CF) - COP', '3000000'); tax = self.field(card, 'Impuestos (COP)', '0')
        value, detail = self.result_panel(card, 'Utilidad neta')
        def calc():
            try:
                price = parse_number(pv.text, 'Precio de venta unitario', False); qty = parse_number(q.text, 'Unidades vendidas'); variable = parse_number(cvu.text, 'Costo variable unitario'); fixed = parse_number(cf.text, 'Costos fijos'); taxes = parse_number(tax.text, 'Impuestos')
                if price <= variable: raise ValueError('El precio de venta debe ser mayor que el costo variable unitario.')
                sales = price*qty; variable_total=variable*qty; profit=sales-variable_total-fixed; net=profit-taxes
                value.text=money(net); value.color=GREEN if net >= 0 else RED
                detail.text=f'Ventas: {money(sales)}\nCostos variables: {money(variable_total)}\nUtilidad antes de impuestos: {money(profit)}\nImpuestos: {money(taxes)}'
            except ValueError as e: self.error(e)
        self.calculate_button(card, 'Calcular utilidad', calc)

    def module_break_even(self, content):
        card = self.form_card(content, 'Punto de equilibrio y margen de seguridad', 'PE unidades = CF ÷ MCu. PE pesos = CF ÷ MC% (MC% en decimal).')
        cf=self.field(card,'Costos fijos (CF) - COP','3000000'); pv=self.field(card,'Precio de venta unitario (PVu) - COP','50000'); cvu=self.field(card,'Costo variable unitario (CVu) - COP','20000'); actual=self.field(card,'Ventas reales en unidades (opcional)','200')
        uv, ud = self.result_panel(card, 'Punto de equilibrio en unidades'); pvout, pd = self.result_panel(card, 'Punto de equilibrio en pesos'); sv, sd = self.result_panel(card, 'Margen de seguridad')
        def calc():
            try:
                fixed=parse_number(cf.text,'Costos fijos'); price=parse_number(pv.text,'Precio de venta unitario',False); variable=parse_number(cvu.text,'Costo variable unitario')
                if price<=variable: raise ValueError('El precio de venta debe ser mayor que el costo variable unitario.')
                mcu=price-variable; ratio=mcu/price; exact=fixed/mcu; units=exact.to_integral_value(rounding=ROUND_CEILING); sales=fixed/ratio
                uv.text=f'{units:,.0f} unidades'; ud.text=f'Resultado exacto: {exact:,.2f}. Se redondea hacia arriba.'; pvout.text=money(sales); pd.text=f'Margen de contribución porcentual: {ratio*100:.2f}%'
                if actual.text.strip():
                    qty=parse_number(actual.text,'Ventas reales en unidades'); safe_units=qty-exact; safe_sales=qty*price-sales; pct=(safe_sales/(qty*price)*100) if qty else Decimal(0)
                    sv.text=f'{safe_units:,.2f} unidades'; sv.color=GREEN if safe_units>=0 else RED; sd.text=f'Margen de seguridad en pesos: {money(safe_sales)}\nMargen de seguridad porcentual: {pct:.2f}%'
                else: sv.text='—'; sd.text='Ingresa las ventas reales para calcular el margen de seguridad.'
            except ValueError as e: self.error(e)
        self.calculate_button(card,'Calcular punto de equilibrio',calc)

    def module_budget(self, content):
        card=self.form_card(content,'Presupuesto de ventas según utilidad objetivo','Q = (Costos fijos + Utilidad objetivo) ÷ MCu. Calcula cuántas unidades se deben vender para alcanzar la utilidad deseada.')
        period=self.field(card,'Periodo del presupuesto','Mensual'); cf=self.field(card,'Costos fijos (CF) - COP','3000000'); pv=self.field(card,'Precio de venta unitario (PVu) - COP','50000'); cvu=self.field(card,'Costo variable unitario (CVu) - COP','20000'); target=self.field(card,'Utilidad objetivo (COP)','3000000'); tax=self.field(card,'Impuestos estimados (COP)','0')
        value,detail=self.result_panel(card,'Unidades necesarias en el presupuesto')
        def calc():
            try:
                label=period.text.strip() or 'No especificado'; fixed=parse_number(cf.text,'Costos fijos'); price=parse_number(pv.text,'Precio de venta unitario',False); variable=parse_number(cvu.text,'Costo variable unitario'); goal=parse_number(target.text,'Utilidad objetivo'); taxes=parse_number(tax.text,'Impuestos estimados')
                if price<=variable: raise ValueError('El precio de venta debe ser mayor que el costo variable unitario.')
                mcu=price-variable; exact=(fixed+goal)/mcu; units=exact.to_integral_value(rounding=ROUND_CEILING); sales=units*price; variable_total=units*variable; total=fixed+variable_total; profit=sales-total; net=profit-taxes
                value.text=f'{units:,.0f} unidades'; value.color=GREEN
                detail.text=f'Periodo: {label}\nUnidades exactas: {exact:,.2f}\nPresupuesto de ventas: {money(sales)}\nCostos variables: {money(variable_total)}\nCosto total: {money(total)}\nUtilidad antes de impuestos: {money(profit)}\nUtilidad neta estimada: {money(net)}'
            except ValueError as e: self.error(e)
        self.calculate_button(card,'Calcular presupuesto',calc)


if __name__ == '__main__':
    CostifyApp().run()
