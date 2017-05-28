#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import tkinter as tk
import urllib.request
from bs4 import BeautifulSoup


class PizzaFilter(object):
    def __init__(self):
        with urllib.request.urlopen('https://pizzaforte.hu/pizzak.php') as response:
           html = response.read().decode()
        soup = BeautifulSoup(html, 'html.parser')

        self.data = {}
        self.load_pizza('classic', soup, self.data)
        self.load_pizza('italy', soup, self.data)
        self.query = {
            'type': 'italy',
            'toppings': []
        }
        self.output = None

    def get_toppings(self):
        return self.data['toppings']

    def set_clear(self, clear):
        self.clear = clear

    def set_output(self, output):
        self.clear()
        self.output = output
        self.render()

    def render(self):
        pizza_type = self.query['type']
        toppings = self.query['toppings']
        result = self.filter_pizzas(self.data, pizza_type, toppings)
        if len(toppings) == 0:
            output = 'Szamodra barmelyik pizza megfelel!\n'
            output += '\n'.join(['  '+t['name'] for t in result])
        else:
            perfect = [t for t in result if len(toppings) == t['fitness']]
            partial = [t for t in result if len(toppings) > t['fitness']]
            if len(perfect) > 0:
                output = 'Szamodra megfelelo pizzak:\n'
                output += '\n'.join(['  '+t['name'] for t in perfect])
                output += '\n\n'
            else:
                output = ''
            output += 'Reszlegesen megfelelo pizzak:\n'
            output += '\n'.join(['  '+t['name'].ljust(20, ' ')+'     hianyzik: '+', '.join([m for m in t['missing']]) for t in partial])

        self.clear()
        self.output(output)

    def update_pizza_type_query(self, pizza_type):
        self.query['type'] = pizza_type
        self.render()

    def update_toppings_query(self, topping, state):
        if state:
            self.query['toppings'].append(topping)
        else:
            self.query['toppings'].remove(topping)
        self.render()

    def load_pizza(self, pizza_class, soup, data):
        data[pizza_class] = {}
        temp_toppings = set()
        for pizza in soup.findAll('td', {'class': pizza_class+'_pizza'}):
            name = re.search('>([^<]+)<', str(pizza.h3)).group(1).strip()
            content = str(pizza.p).replace('\n', '')
            toppings = re.search('<p>\s*\(?\s*([^<\(\)]+)[^<]*<', content).group(1)
            toppings = [topping.strip() for topping in toppings.split(',')]
            data[pizza_class][name] = toppings
            temp_toppings.update(toppings)
        if 'toppings' not in data:
            data['toppings'] = temp_toppings
        else:
            data['toppings'].update(temp_toppings)
            data['toppings'] = [t for t in sorted(list(data['toppings'])) if not re.search('\d', t)]

    def filter_pizzas(self, data, pizza_type, toppings):
        result = []
        for candidate_name in data[pizza_type]:
            candidate = data[pizza_type][candidate_name]
            fitness = 0
            missing = []
            for t in toppings:
                if t in candidate:
                    fitness += 1
                else:
                    missing.append(t)
            result.append({
                'name': candidate_name,
                'fitness': fitness,
                'missing': missing
            })
        result = sorted(result, key=lambda p:p['name'])
        return sorted(result, key=lambda p:p['fitness'], reverse=True)



class PizzaTypeSelector(tk.Frame):
    def __init__(self, parent, pizza_type_protocol):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.italy = tk.Button(self, text='ITALY', height=2, command=lambda b='italy':self.toggle_callback(b))
        self.classic = tk.Button(self, text='CLASSIC', height=2, command=lambda b='classic':self.toggle_callback(b))
        self.italy.grid(row=0, column=0, sticky='we')
        self.classic.grid(row=0, column=1, sticky='we')
        self.italy.config(bg='green', activebackground='green4')
        self.pizza_type_protocol = pizza_type_protocol

    def toggle_callback(self, pizza_type):
        if pizza_type == 'classic':
            self.classic.config(bg='green', activebackground='green4')
            self.italy.config(bg='gray22', activebackground='#434343')
        elif pizza_type == 'italy':
            self.italy.config(bg='green', activebackground='green4')
            self.classic.config(bg='gray22', activebackground='#434343')
        self.pizza_type_protocol(pizza_type)


class ToggleButton(tk.Button):
    def __init__(self, parent, text, protocol, state=False):
        tk.Button.__init__(self, parent, text=text, command=self.callback, bg='gray22')
        self.topping = text
        self.state = state
        self.update_color()
        self.protocol = protocol

    def update_color(self):
        if self.state:
            self.config(bg='green', activebackground='green4')
        else:
            self.config(bg='gray22', activebackground='#434343')

    def callback(self):
        self.state = not self.state
        self.protocol(self.topping, self.state)
        self.update_color()


class ToppingsSelector(tk.Frame):
    def __init__(self, parent, toppings, toppings_protocol, columns=4):
        tk.Frame.__init__(self, parent)
        counter = 0
        for topping in toppings:
            b = ToggleButton(self, topping, toppings_protocol)
            b.grid(column=int(counter/columns), row=counter%columns, sticky='we')
            counter += 1


def main():
    pizza_filter = PizzaFilter()
    root = tk.Tk()
    root.wm_title('Pizza Forte pizza valaszto alkalmazas')
    PizzaTypeSelector(root, pizza_filter.update_pizza_type_query).pack(fill='x')
    ToppingsSelector(root, pizza_filter.get_toppings(), pizza_filter.update_toppings_query, columns=10).pack(fill='x')
    text = tk.Text(root)
    text.pack(fill='x')
    text.insert(0.0, 'imreeeee')
    pizza_filter.set_clear(lambda: text.delete(0.0, tk.END))
    pizza_filter.set_output(lambda t:text.insert(0.0, t))
    root.mainloop()

if __name__ == '__main__':
    main()

