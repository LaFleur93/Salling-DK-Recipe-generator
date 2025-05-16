from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from customtkinter import *
import tkintermapview
import math
import api_food_waste
import api_gpt
import requests
from urllib.request import urlopen
from io import BytesIO

class FoodWaste:
    def __init__(self, window):
        # Initializations and window dimensions
        self.wind = window
        self.wind_x = 300
        self.wind_y = 590
        self.wind.title('Salling Food Waste')
        self.wind.geometry(f'{self.wind_x}x{self.wind_y}')
        self.wind.resizable(False, False)

        self.border_color = "#558BB9"
        self.bg_color = "white"
        self.bg_color_2 = "#DDEEF8"
        self.font_color = "#022742"

        #-------------------------------------
        # Notifications
        #-------------------------------------
        frame_column_1 = LabelFrame(self.wind, borderwidth = '0', bg=self.bg_color_2)
        frame_column_1.place(x=0, y=0, width=self.wind_x)
        top = LabelFrame(frame_column_1, borderwidth = "0", height=5, bg=self.bg_color_2).pack(fill="x")

        frame_msg = LabelFrame(
            frame_column_1,
            text='  Notifications',
            font=('Segoe UI', 9, 'bold'),
            height=50,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bg=self.bg_color
        )
        frame_msg.pack(anchor="center", fill="x", padx=5, pady=1)

        self.message = Label(frame_msg, text = 'Please set your preferences', bg=self.bg_color)
        self.message.place(x=10, y=3)

        #-------------------------------------
        # User preferences
        #-------------------------------------
        
        self.preferences_status = False # False if no preferences were setted

        frame_preferences = LabelFrame(
            frame_column_1,
            text='  My preferences',
            font=('Segoe UI', 9, 'bold'),
            height=50,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bg=self.bg_color
        )
        frame_preferences.pack(anchor = "center", fill="x", padx=5, pady=1)

        Label(frame_preferences, text = "Enter your address:", bg=self.bg_color).pack(anchor="w", padx=5, pady=3)

        frame_street_box = LabelFrame(frame_preferences, borderwidth = "0", width=280, height=30, bg="white")
        frame_street_box.pack()

        self.address_entry = CTkEntry(frame_street_box, width=200, placeholder_text="E.g. Nørrebrogade 15")
        self.address_entry.place(x=5, y=0)
        self.address_entry.bind("<Return>", lambda event: self.geocode_address())
        CTkButton(frame_street_box, text='Search', text_color="white", width=70, font=('Segoe UI', 12, 'bold'), border_width=1, command=self.geocode_address).place(x=206)

        self.map_widget = tkintermapview.TkinterMapView(frame_preferences, width=270, height=200, corner_radius=10)
        self.map_widget.pack()

        self.coordinates = [55.676098, 12.568337] # Coordinates for Rådhuspladsen
        self.map_widget.set_position(self.coordinates[0], self.coordinates[1])
        self.map_widget.set_zoom(12)

        self.marker = self.map_widget.set_marker(20, 20, text="Your location")
        self.map_widget.add_left_click_map_command(self.left_click_event)
        self.circle = self.map_widget.set_polygon([(0,0)])

        #-------------------------------------
        # Travel distance
        #-------------------------------------

        Label(frame_preferences, text = "I'm willing to travel:", bg=self.bg_color).pack(anchor="w", padx=5, pady=5)

        frame_slider = LabelFrame(frame_preferences, borderwidth = "0", height=30, bg=self.bg_color)
        frame_slider.pack(fill="x")

        self.kilometers = 0.1
        self.slider = CTkSlider(frame_slider, from_=0.1, to=10, command=self.sliding)
        self.slider.pack()
        self.slider.set(self.kilometers)
        
        self.distance_entry = CTkEntry(frame_slider, fg_color="#D3D3D3", corner_radius=5, border_width=2, justify="center", width=50)
        self.distance_entry.insert(0, "0.10")
        self.distance_entry.pack(pady=3)
        self.distance_entry.bind("<Return>", lambda e: self.update_distance_from_entry())

        Label(frame_slider, text = "100m", bg=self.bg_color).place(x = 34, y = 18)
        Label(frame_slider, text = "10 km", bg=self.bg_color).place(x = 212, y = 18)

        set_preferences = CTkButton(frame_preferences, text = 'Set my location', font=('Segoe UI', 12,'bold'), border_width=1, text_color='white', command=self.set_location)
        set_preferences.pack(pady=5)

        #-------------------------------------
        # Import data from Salling
        #-------------------------------------

        frame_buttons = LabelFrame(
            frame_column_1,
            text = '    Help us reducing food waste!',
            font=('Segoe UI', 9, 'bold'),
            height=50,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bg=self.bg_color
        )
        frame_buttons.pack(anchor="center", fill="x", padx=5, pady=1)

        button_width, button_height = 270, 30
        
        # Button 1

        button_1 = CTkButton(frame_buttons, text = 'Browse Discounted Products Near Me', width = button_width, height=button_height,
            font=('Segoe UI', 13, 'bold'), text_color="white", border_width=1, command=self.browse_products)
        button_1.pack(pady=3)

        # Button 2

        button_2 = CTkButton(frame_buttons, text = 'Want Smarter Recipes? Scan Your Fridge', width = button_width, height=button_height,
            font=('Segoe UI', 13, 'bold'), text_color="white", border_width=1, command=self.smart_recipes)
        button_2.pack(pady=3)
        
        # Button 3

        button_3 = CTkButton(frame_buttons, text = 'Help Me Find Ingredients for My Dish', width = button_width, height=button_height,
            font=('Segoe UI', 13, 'bold'), text_color="white", border_width=1, command=self.find_ingredients)
        button_3.pack(pady=3)

        bottom = LabelFrame(frame_buttons, borderwidth = "0", height=5, bg="white").pack(fill="x")

    def browse_products(self):
        if self.preferences_status == True:

            get_data = api_food_waste.salling_api(self.coordinates, self.kilometers)

            if get_data[0] == []:
                self.message['text'] = f'Unable to find any story close by!'
                self.message['fg'] = 'red'
                self.message['font'] = ('Helvetica', 8, 'bold')
                return None

            self.products, self.df = get_data
            df_discount = self.df.sort_values(by="Discount (%)", ascending=False)
            df_discount = df_discount[0:10]
            
            self.wind_x_2 = self.wind_x
            self.wind_2 = Toplevel(self.wind)
            self.wind_2.title('Salling Food Waste')
            self.wind_2.geometry(f'{self.wind_x_2}x{self.wind_y}')
            self.wind_2.resizable(False, False)
            
            #-------------------------------------
            # Products with high discount
            #-------------------------------------

            frame_column_2 = LabelFrame(self.wind_2, borderwidth = '0', bg=self.bg_color_2)
            frame_column_2.place(x=0, y=0, width=300, relheight=1)

            Label(frame_column_2, text = f"We've found {len(self.products)} products!", font=('Segoe UI', 13, 'bold'), fg=self.font_color, bg=self.bg_color_2).pack(pady=5, anchor = "center")
            Label(frame_column_2, text = f"Scroll down these high-discount products:", font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack(pady=5, anchor = "center")

            scrollable_frame_discounts = CTkScrollableFrame(frame_column_2, width=270, height=495, fg_color='white')
            scrollable_frame_discounts._scrollbar.grid_remove()
            scrollable_frame_discounts.pack(anchor = "center")

            for i in range(0, 10):
                try:
                    image_url = df_discount.iloc[i]["Product Image"]    
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data)); img.thumbnail((220, 220), Image.LANCZOS)
                except: # In case the product has no image available
                    image_url = "https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg"    
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data)); img.thumbnail((130, 130), Image.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)

                label = Label(scrollable_frame_discounts, image=photo)
                label.image = photo
                label.pack(pady=3)

                Label(scrollable_frame_discounts, bg="white", text = f'{df_discount.iloc[i]["Product Description"]}', font=('Segoe UI', 10, 'bold')).pack(pady=(3, 0))
                Label(scrollable_frame_discounts, bg="white", text = f'Price: {df_discount.iloc[i]["New Price (DKK)"]} dkk (Original: {df_discount.iloc[i]["Original Price (DKK)"]} dkk)', font=('Calibri', 10, 'bold')).pack(pady=(0, 0))
                Label(scrollable_frame_discounts, bg="white", text = f'Where? {df_discount.iloc[i]["Store Name"]}', font=('Calibri', 10, 'bold')).pack(pady=(0, 3))

                line = Canvas(scrollable_frame_discounts, height=3, bg=self.border_color, highlightthickness=0)
                line.pack(fill='x', padx=5, pady=10) # Add a line between each product

        else:
            self.message['text'] = f'Please, set your location and preferences'
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')

    def find_ingredients(self):
        if self.preferences_status == True:
            get_data = api_food_waste.salling_api(self.coordinates, self.kilometers)

            if get_data[0] == []:
                self.message['text'] = f'Unable to find any story close by!'
                self.message['fg'] = 'red'
                self.message['font'] = ('Helvetica', 8, 'bold')
                return None

            self.products, self.df = get_data
            df_discount = self.df.sort_values(by="Discount (%)", ascending=False)

            self.wind_x_3 = self.wind_x
            self.wind_y_3 = 540
            self.wind_3 = Toplevel(self.wind)
            self.wind_3.title('Salling Food Waste')
            self.wind_3.geometry(f'{self.wind_x_3}x{self.wind_y_3}')
            self.wind_3.resizable(False, False)

            #-------------------------------------
            # Chatbot, recommendations and recipe
            #-------------------------------------

            self.frame_column_3 = LabelFrame(self.wind_3, borderwidth = '0', bg=self.bg_color_2)
            self.frame_column_3.place(x=0, y=0, width=300, relheight=1)

            Label(self.frame_column_3, text = f"Want something? We’ll guide you to what’s available — no waste.", wraplength=280, font=('Segoe UI', 13, 'bold'), fg=self.font_color, bg=self.bg_color_2).pack(pady=3)
            Label(self.frame_column_3, text = f"Type in what you’d like to eat. The more specific you are, the better we can help!", wraplength=300, font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack(pady=2)

            self.chat_textbox = CTkTextbox(self.frame_column_3, width=280, height=50, border_width=1)
            self.chat_textbox.pack(pady=3)

            button_width, button_height = 70, 25

            chat_button = CTkButton(self.frame_column_3, text = 'Tell us',  width = button_width, height=button_height,
                font=('Segoe UI', 13, 'bold'), text_color="white", border_width=1, command=self.feed_prompt)
            chat_button.pack(padx=10, pady=1, anchor="e")

            # Recommendations

            Label(self.frame_column_3, text = "Our recommendations:", font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack()
            
            self.scrollable_frame_recommendations = CTkScrollableFrame(self.frame_column_3, width=270, height=150, fg_color='white')
            self.scrollable_frame_recommendations._scrollbar.grid_remove()
            self.scrollable_frame_recommendations.pack(pady=3)

            Label(self.scrollable_frame_recommendations, text = "Tell us what you'd like to eat in the box above :)", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=60)

            Label(self.frame_column_3, text = "Combine those products: Try this recipe!", font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack()

            # Recipe

            self.scrollable_frame_recipe = CTkScrollableFrame(self.frame_column_3, width=260, height=90, fg_color='white')
            self.scrollable_frame_recipe._scrollbar.grid_remove()
            self.scrollable_frame_recipe.pack(pady=3)

            Label(self.scrollable_frame_recipe, text = "No recipe yet available!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=35)

            Label(self.frame_column_3, text = 'Not happy with what you see? Try clicking on "Tell us" again!', font=('Segoe UI', 7, 'bold'), fg=self.font_color, bg=self.bg_color_2).pack()
            
        else:
            self.message['text'] = f'Please, set your location and preferences'
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')

    def smart_recipes(self):
        if self.preferences_status == True:
            get_data = api_food_waste.salling_api(self.coordinates, self.kilometers)

            if get_data[0] == []:
                self.message['text'] = f'Unable to find any story close by!'
                self.message['fg'] = 'red'
                self.message['font'] = ('Helvetica', 8, 'bold')
                return None

            self.products, self.df = get_data
            df_discount = self.df.sort_values(by="Discount (%)", ascending=False)

            self.wind_x_4 = 700
            self.wind_y_4 = self.wind_y
            self.wind_4 = Toplevel(self.wind)
            self.wind_4.title('Salling Food Waste')
            self.wind_4.geometry(f'{self.wind_x_4}x{self.wind_y_4}')
            self.wind_4.resizable(False, False)

            #---------------------------------------------------
            # Upload file, check ingredients and suggest recipes
            #---------------------------------------------------

            self.frame_column_4 = LabelFrame(self.wind_4, borderwidth = '0', bg=self.bg_color_2)
            self.frame_column_4.place(x=0, y=0, width=self.wind_x_4, relheight=1)

            Label(self.frame_column_4, text = f"No more waste — let’s turn your fridge into real meals with nearby deals.", wraplength=690, font=('Segoe UI', 13, 'bold'), fg=self.font_color, bg=self.bg_color_2).pack(pady=3)
            Label(self.frame_column_4, text = f"Let's scan your fridge! We can tell you what you can cook with what’s inside + today’s local discounts", wraplength=690, font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack(pady=2)

            frame_image_and_items = LabelFrame(self.frame_column_4, borderwidth = '0', width=self.wind_x_4, height=300, bg=self.bg_color_2)
            frame_image_and_items.pack()

            image_url = "https://cdn-icons-png.flaticon.com/512/1092/1092216.png"
            u = urlopen(image_url)
            raw_data = u.read()
            u.close()
            img = Image.open(BytesIO(raw_data))
            img.thumbnail((150, 150), Image.LANCZOS)

            upload_default_photo = ImageTk.PhotoImage(img)

            self.upload_image_label = Label(frame_image_and_items, image=upload_default_photo, width=180, height=180, cursor="hand2")
            self.upload_image_label.image = upload_default_photo  # keep a reference
            self.upload_image_label.place(x=10, y=10)
            self.upload_image_label.bind("<Button-1>", lambda event: self.upload_fridge_image())

            button_width, button_height = 180, 25
            upload_image_button = CTkButton(frame_image_and_items, text = 'Upload fridge photo', width = button_width, height=button_height, font=('Segoe UI', 13, 'bold'), text_color="white", border_width=1, command=self.upload_fridge_image)
            upload_image_button.place(x=10, y=200)
            Label(frame_image_and_items, text = f"Accepted formats: .png, .jpg, .jpeg", font=('Segoe UI', 8, 'bold'), fg=self.font_color, bg=self.bg_color_2).place(x=10, y=225)


            Label(frame_image_and_items, text = f"🧊 These are the items we could detect in your fridge:", font=('Segoe UI', 11, 'bold'), fg=self.font_color, bg=self.bg_color_2).place(x=203, y=0)

            self.scrollable_frame_fridge_products = CTkScrollableFrame(frame_image_and_items, width=475, height=20, fg_color=self.bg_color_2, orientation="horizontal")
            self.scrollable_frame_fridge_products.place(x=203, y=22)
            #self.scrollable_frame_fridge_products._scrollbar.grid_remove()
            self.items_in_fridge = Label(self.scrollable_frame_fridge_products, text = "No items scanned! Please, upload a picture of your fridge :)", wraplength=2000, font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2)
            self.items_in_fridge.pack(anchor="w")

            Label(frame_image_and_items, text = f"💰 Discounted items that might be perfect to combine!", font=('Segoe UI', 11, 'bold'), fg=self.font_color, bg=self.bg_color_2).place(x=203, y=60)

            self.scrollable_frame_smart = CTkScrollableFrame(frame_image_and_items, width=475, height=183, fg_color='white', orientation="horizontal")
            self.scrollable_frame_smart.place(x=203, y=90)

            Label(self.scrollable_frame_smart, text = "No recommendations yet available. Please, scan your fridge!", wraplength=400, font=('Segoe UI', 9, 'normal'), bg="white").pack(anchor="center", padx=90, pady=80)            

            Label(self.frame_column_4, text = f"Not sure how to combine them? These recipes might inspire you!", font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack(anchor="w", padx=10)

            # Recipes

            self.scrollable_frame_smart_recipe = CTkScrollableFrame(self.frame_column_4, width=self.wind_x_4, height=200, fg_color='white')
            self.scrollable_frame_smart_recipe._scrollbar.grid_remove()
            self.scrollable_frame_smart_recipe.pack(padx=10, pady=3)

            Label(self.scrollable_frame_smart_recipe, text = "No recipes yet available. Please, scan your fridge!", wraplength=500, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=90)

        else:

            self.message['text'] = f'Please, set your location and preferences'
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')

    def feed_prompt(self):
        self.clear_scrollable_frame(self.scrollable_frame_recommendations)
        self.prompt = self.chat_textbox.get("0.0", "end")
        
        response = api_gpt.chat_with_gpt(self.prompt, self.products)

        if response not in ["[]", "Not related to food"]:
            self.clear_scrollable_frame(self.scrollable_frame_recommendations) # Clear the scrollbar frame
            self.clear_scrollable_frame(self.scrollable_frame_recipe)

            useful_products = list(map(int, response.strip("[]").split(",")))

            for i in useful_products:
                try:
                    image_url = self.df.iloc[i]["Product Image"]
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data))
                    img.thumbnail((120, 120), Image.LANCZOS)
                except:
                    image_url = "https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg"
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data))
                    img.thumbnail((100, 100), Image.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                product_card = CTkFrame(self.scrollable_frame_recommendations, fg_color='white')
                product_card.pack(padx=10, pady=5)

                Label(product_card, image=photo, bg='white').pack()
                product_card.image = photo  # Keep a reference

                Label(product_card, text=self.df.iloc[i]["Product Description"], bg='white', font=('Segoe UI', 10, 'bold')).pack(pady=(3, 0))
                Label(product_card, text=f'Price: {self.df.iloc[i]["New Price (DKK)"]} dkk', bg='white', font=('Calibri', 10)).pack(pady=(0, 0))
                Label(product_card, text=f'Where? {self.df.iloc[i]["Store Name"]}', bg='white', font=('Calibri', 10)).pack(pady=(0,3))

            selected_products = [self.df.iloc[i]["Product Description"] for i in useful_products]

            # Recipe prompt

            recipe_response = api_gpt.get_recipe(self.prompt, selected_products)

            response_textbox = CTkTextbox(self.scrollable_frame_recipe, width=270, fg_color="white")
            response_textbox.insert("0.0", recipe_response)
            response_textbox.pack()

            products_for_metrics = self.df.loc[useful_products]

            self.metrics(products_for_metrics)


        elif response == "[]":

            self.clear_scrollable_frame(self.scrollable_frame_recommendations)
            self.clear_scrollable_frame(self.scrollable_frame_recipe)
            Label(self.scrollable_frame_recommendations, text = "We are sorry :( No products were found. You can try with something else!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=60)
            Label(self.scrollable_frame_recipe, text = "No recipe yet available!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=35)            

        else:

            self.clear_scrollable_frame(self.scrollable_frame_recommendations)
            self.clear_scrollable_frame(self.scrollable_frame_recipe)
            Label(self.scrollable_frame_recommendations, text = "Are you sure that's edible?! Maybe you can try with something else!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=60)
            Label(self.scrollable_frame_recipe, text = "No recipe yet available!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=35)

    def upload_fridge_image(self):

        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filepath:
            self.fridge_image_path = filepath

            # Show preview
            img = Image.open(filepath)
            img.thumbnail((180, 180))
            photo = ImageTk.PhotoImage(img)

            self.upload_image_label.configure(image=photo, text="")
            self.upload_image_label.image = photo  # Keep reference

            # Detect items
            detected_items = self.detect_items_in_fridge(filepath)
 
            # Show helpful message
            self.message['text'] = "Fridge photo uploaded!"
            self.message['fg'] = 'green'
            self.message['font'] = ('Helvetica', 8, 'bold')

    def detect_items_in_fridge(self, image_path):
        model_url = "https://detect.roboflow.com/group_work-8xzxi/1"
        api_key = "Insert roboflow API key here"
    
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                f"{model_url}?api_key={api_key}",
                files={"file": image_file}
            )
    
        data = response.json()
    
        # Extract detected items
        items = set([pred["class"].capitalize() for pred in data.get("predictions", [])])
        self.textual_items = ', '.join(items)
        self.items_in_fridge["text"] = self.textual_items

        # Execute smart findings function right after uploading the fridge photo

        self.smart_items_and_recipes()

    def smart_items_and_recipes(self):
        
        get_data = api_food_waste.salling_api(self.coordinates, self.kilometers)

        self.products, self.df = get_data
        self.prompt = self.textual_items
        
        response = api_gpt.smart_scan_gpt(self.prompt, self.products)

        if response not in ["[]"]:
            self.clear_scrollable_frame(self.scrollable_frame_smart) # Clear the scrollbar frame
            self.clear_scrollable_frame(self.scrollable_frame_smart_recipe)

            useful_products = list(map(int, response.strip("[]").split(",")))

            for i in useful_products:
                try:
                    image_url = self.df.iloc[i]["Product Image"]
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data))
                    img.thumbnail((90, 90), Image.LANCZOS)
                except:
                    image_url = "https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg"
                    u = urlopen(image_url)
                    raw_data = u.read()
                    u.close()
                    img = Image.open(BytesIO(raw_data))
                    img.thumbnail((100, 100), Image.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                product_card = CTkFrame(self.scrollable_frame_smart, fg_color='white')
                product_card.pack(side='left', padx=10, pady=5)

                Label(product_card, image=photo, bg='white').pack()
                product_card.image = photo  # Keep a reference

                Label(product_card, text=self.df.iloc[i]["Product Description"], bg='white', font=('Segoe UI', 10, 'bold')).pack(pady=(3, 0))
                Label(product_card, text=f'Price: {self.df.iloc[i]["New Price (DKK)"]} dkk', bg='white', font=('Calibri', 10)).pack(pady=(0, 0))
                Label(product_card, text=f'Where? {self.df.iloc[i]["Store Name"]}', bg='white', font=('Calibri', 10)).pack(pady=(0,3))

            selected_products = [self.df.iloc[i]["Product Description"] for i in useful_products]

            # Recipe prompt

            recipe_response = api_gpt.get_smart_recipe(self.prompt, selected_products)

            response_textbox = CTkTextbox(self.scrollable_frame_smart_recipe, width=self.wind_x_4, fg_color="white")
            response_textbox.insert("0.0", recipe_response)
            response_textbox.pack()

            products_for_metrics = self.df.loc[useful_products]

            self.metrics(products_for_metrics)

        else:

            self.clear_scrollable_frame(self.scrollable_frame_smart)
            self.clear_scrollable_frame(self.scrollable_frame_smart_recipe)
            Label(self.scrollable_frame_smart, text = "We are sorry :( No products were found. You can try scanning something else!", wraplength=600, font=('Segoe UI', 9, 'normal'), bg="white").pack(padx=20, pady=80)
            Label(self.scrollable_frame_smart_recipe, text = "No recipe yet available!", wraplength=200, font=('Segoe UI', 9, 'normal'), bg="white").pack(pady=90)            

    def metrics(self, products):
        y = 20 * len(products)
        self.wind_x_5 = self.wind_x
        self.wind_y_5 = 90 + y + 110
        self.wind_5 = Toplevel(self.wind)
        self.wind_5.title('Salling Food Waste')
        self.wind_5.geometry(f'{self.wind_x_5}x{self.wind_y_5}')
        self.wind_5.resizable(False, False)

        self.frame_column_5 = LabelFrame(self.wind_5, borderwidth = '0', bg=self.bg_color_2)
        self.frame_column_5.place(x=0, y=0, width=self.wind_x_5, relheight=1)

        Label(self.frame_column_5, text = f"🌍 You're Saving More Than Money", wraplength=690, font=('Segoe UI', 13, 'bold'), fg=self.font_color, bg=self.bg_color_2).pack(pady=3)
        Label(self.frame_column_5, text = f"Your choices matter. Look how you can help reducing food waste:", wraplength=self.wind_x_5, font=('Segoe UI', 11, 'normal'), fg=self.font_color, bg=self.bg_color_2).pack(pady=2)

        metrics_table = Frame(self.frame_column_5, bg=self.bg_color_2)
        metrics_table.pack(padx=5, pady=2, fill="x")

        # Table header
        header_font = ('Segoe UI', 9, 'bold')
        Label(metrics_table, text="Product", font=header_font, bg=self.font_color, fg="white", width=22).grid(row=0, column=0, sticky="w")
        Label(metrics_table, text="Saved CO₂", font=header_font, bg=self.font_color, fg="white", width=8).grid(row=0, column=1)
        Label(metrics_table, text="Saved DKK", font=header_font, bg=self.font_color, fg="white", width=9).grid(row=0, column=2)

        # Table data
        total_carbon = 0
        total_discount = 0

        estimated_co2_by_category = {
            "Unknown": 0,
            "Dairy And Cold Storage": 1.5,
            "Meat Fish": 3.0,
            "Bread And Cakes": 0.5,
            "Personal Care": 0.8,
            "Frozen Products": 1.2,
            "Beverages": 0.7
        }

        for i in range(len(products)):
            name = products.iloc[i]["Product Description"]
            emission = api_food_waste.estimated_emissions(name)
            if emission == 0:
                category = products.iloc[i]["Category"]
                emission = estimated_co2_by_category[category]

            discount = float(products.iloc[i]["Discount (DKK)"])

            Label(metrics_table, text=name, bg=self.bg_color, font=('Segoe UI', 9), anchor="w", width=22).grid(row=i+1, column=0, sticky="w")
            Label(metrics_table, text=f"{emission:.2f} kg", fg="green", bg=self.bg_color, font=('Segoe UI', 9, 'bold'), width=8).grid(row=i+1, column=1)
            Label(metrics_table, text=f"{discount:.2f} kr.", fg="green", bg=self.bg_color, font=('Segoe UI', 9, 'bold'), width=9).grid(row=i+1, column=2)

            total_carbon += emission
            total_discount += float(discount)

        # Summary
        results = Label(
            self.frame_column_5,
            text=f"If you go with these products, you might help save {total_carbon:.2f}kg of CO₂ — and keep {total_discount:.2f} DKK in your pocket!",
            wraplength=self.wind_x_5,
            font=('Segoe UI', 11),
            fg=self.font_color,
            bg=self.bg_color_2
        )
        results.pack(pady=2)

    def sliding(self, value):
        self.kilometers = round(float(value), 2)
        self.distance_entry.delete(0, END)
        self.distance_entry.insert(0, f"{self.kilometers:.2f}")

    def update_distance_from_entry(self):
        try:
            km = float(self.distance_entry.get())
            if 0.1 <= km <= 10:
                self.kilometers = km
                self.slider.set(km)
            else:
                self.message['text'] = "Distance must be between 0.1 and 10 km"
                self.message['fg'] = 'red'
                self.message['font'] = ('Helvetica', 8, 'bold')
        except:
            self.message['text'] = "Invalid input. Use a number like 1.5"
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')

    def left_click_event(self, coordinates):
        self.marker.delete()
        self.marker = self.map_widget.set_marker(coordinates[0], coordinates[1], text="Your location")
        self.coordinates = coordinates

    def set_location(self):
        self.map_widget.set_position(self.coordinates[0], self.coordinates[1])
        self.draw_circle(self.coordinates[0], self.coordinates[1], self.kilometers, 36)

    def draw_circle(self, lat, lon, radius_km, num_points=36):
        circle_coordinates = []
        km_in_deg_lat = 110.574  # Approx km per degree latitude
        km_in_deg_lon = 111.320 * math.cos(math.radians(lat))  # Varies with latitude

        delta_lat = radius_km / km_in_deg_lat
        delta_lon = radius_km / km_in_deg_lon

        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            lat_offset = delta_lat * math.sin(angle)
            lon_offset = delta_lon * math.cos(angle)
            circle_coordinates.append((lat + lat_offset, lon + lon_offset))
        
        self.circle.delete()
        self.circle = self.map_widget.set_polygon(circle_coordinates, fill_color=None)

        lats, lons = zip(*circle_coordinates)
        top_left = (max(lats), min(lons))
        bottom_right = (min(lats), max(lons))
        self.map_widget.fit_bounding_box(top_left, bottom_right)

        self.message['text'] = f'Preferences updated!'
        self.message['fg'] = 'green'
        self.message['font'] = ('Helvetica', 8, 'bold')

        self.preferences_status = True

    def clear_scrollable_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def geocode_address(self):
        address = self.address_entry.get()
        if not address:
            self.message['text'] = "Please enter an address"
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')
            return

        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
        try:
            response = requests.get(url, headers={"User-Agent": "SmartGroceryAI/1.0"})
            data = response.json()
            if len(data) == 0:
                self.message['text'] = "Address not found. Try again."
                self.message['fg'] = 'red'
                self.message['font'] = ('Helvetica', 8, 'bold')
                return
        
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])

            # Update map and marker
            self.left_click_event((lat, lon))  # Set marker and coordinates
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_zoom(14)

            self.message['text'] = f"Location set!"
            self.message['fg'] = 'green'
            self.message['font'] = ('Helvetica', 8, 'bold')
            self.set_location()

        except Exception as e:
            self.message['text'] = "Error while searching location."
            self.message['fg'] = 'red'
            self.message['font'] = ('Helvetica', 8, 'bold')

if __name__ == '__main__':
    window = Tk()
    application = FoodWaste(window)
    window.mainloop()