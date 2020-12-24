import sys
from datetime import date, datetime

import kivy
import pandas as pd
from kivy.app import App
from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

import socket_client

# Config.set('graphics', 'resizable', False)
# Config.set('graphics', 'width', '500')
#kivy.config.Config.set('graphics','resizable', False)

#flag = 0
#admin_list_counter = 0
#SERVER_PORT = 1234         will be provided by socket_client.py
#SERVER_IP = '127.0.0.1'    will be provided by socket_client.py


def show_error(message):
    chat_app.infopage.update_info(message)
    chat_app.screen_manager.current = 'Info Page'
    Clock.schedule_once(sys.exit, 10)


class Custom(Switch):
    pass

Builder.load_string('''
<Custom>:
    values: ['ON', 'OFF']
    canvas:
        Color:
            rgb: 0, 0.6, 0.6, 1
        Rectangle:
            size: [sp(41.5), sp(20)]
            pos: [self.center_x - sp(41.5), self.center_y - sp(10)]
        Color:
            rgb: 0.4, 0.4, 0.4, 1
        Rectangle:
            size: [sp(41.5), sp(20)]
            pos: [self.center_x, self.center_y - sp(10)]
    Label:
        color: 0, 1, 0, 1
        text: '[b]{}[/b]'.format(root.values[0])
        markup: True
        bold: True
        font_size: 13
        pos: [root.center_x - sp(70), root.center_y - sp(50)]
    Label:
        color: 0, 0.75, 0.75, 1
        text: '[b]{}[/b]'.format(root.values[1])
        markup: True
        font_size: 13
        pos: [root.center_x - sp(30), root.center_y - sp(50)]
        ''')


class LoginPage(Image):
    def __init__(self, **kwargs):     #add **kwargs if not running
        super().__init__(**kwargs)

        self.source = 'guudu-6.jpg'
        self.allow_stretch = True
        self.keep_ratio = False
        self.color=[1,1,1,0.7]

        #will be used by Chat Page when getting username and role of logged in user
        #self.username_for_chatpage = None
        self.role_for_chatpage = None

        self.float_layout = FloatLayout(
            size=(Window.size[0],Window.size[1])
        )
        
        self.login_label = Label(
            text='[color=#ffffff]Chat Room[/color]',
            font_size=89,
            font_name='./IMPRISHA',
            pos=(5,190),
            markup=True
        )
        #print(Window.size[0], Window.size[1])
        self.username_input = TextInput(
            multiline=False,
            size_hint=(0.35,0.08),
            pos_hint={'x':0.330, 'y':0.6},
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.95),
            foreground_color=(1,1,1,1), #text color
            font_size='17sp',
            hint_text='Username',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13
        )

        self.password_input = TextInput(
            multiline=False,
            size_hint=(0.35,0.08),
            pos_hint={'x':0.330, 'y':0.45},
            password=True,
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.95),
            foreground_color=(1,1,1,1),
            font_size='17sp',
            hint_text='Password',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13
        )

        self.wrong_password_info = Label(
            text='',
            pos=(3,-50)
        )

        self.info_box = Label(
            text='If new user, then sign up',
            font_size=13,
            pos=(0,-165)
        )

        self.login_button = Button(
            text='Login',
            font_size=20,
            size_hint=(0.20,0.08),
            #pos_hint={'x':0.345, 'y':0.30}
            pos=(320,180),
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            background_normal=''
        )
        self.login_button.bind(on_press=self.login_button_function)

        self.signup_button = Button(
            text='Sign Up',
            size_hint=(0.20,0.08),
            font_size=20,
            #pos_hint={'x':0.345, 'y':0.30}
            pos=(320,70),
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            background_normal=''
        )
        self.signup_button.bind(on_press=self.signup_button_function)

        self.float_layout.add_widget(self.signup_button)
        self.float_layout.add_widget(self.login_button)
        self.float_layout.add_widget(self.wrong_password_info)
        self.float_layout.add_widget(self.info_box)
        self.float_layout.add_widget(self.username_input)
        self.float_layout.add_widget(self.password_input)
        self.float_layout.add_widget(self.login_label)
        self.add_widget(self.float_layout)

    def signup_button_function(self, instance):
        chat_app.screen_manager.transition.direction = 'right'
        chat_app.screen_manager.current = 'SignUp'


    def login_button_function(self, instance):
        # port = SERVER_PORT
        # ip = SERVER_IP
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        df = None 

        df = socket_client.get_df(show_error)
        #print(df)

        if df is None:
            return

        else:
            #check details and update label if necessary
            if username in df['Username'].unique():
                r = df.loc[df['Username'] == username]
                if (r.get('Password') == password).bool():
                    temp_role = df.loc[df['Username'] == username].get('Role').to_string()  #dunno why it has index num and 4 spaces
                    self.role_for_chatpage = temp_role[2:].strip()
                    #login
                    info = f'Joining {socket_client.ip1}:{socket_client.port} as {username}'
                    chat_app.infopage.update_info(info)

                    chat_app.screen_manager.current = 'Info Page'

                    Clock.schedule_once(self.connect, 1)
                else:
                    #update label
                    self.wrong_password_info.text = 'Wrong Password!'
                    self.password_input.text = ''
            else:
                #update label
                self.wrong_password_info.text = 'No such Username exists!'
                self.username_input.text = ''
                self.password_input.text = ''
        

    
    def connect(self, dt):
        # port = int(SERVER_PORT)
        # ip = SERVER_IP
        username = self.username_input.text
        
        #if socket_client.connect is not True, we will return 
        if not socket_client.connect(username, show_error):
            return

        #create a chat page and go to it
        chat_app.create_chat_page()
        chat_app.screen_manager.current = 'Chat Page'


class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #just one column
        self.cols = 1
        self.message = Label(halign='center', valign='center', font_size=30)

        self.message.bind(width=self.update_text_width)
        #adding this widget to the layout
        self.add_widget(self.message)

    #Called with a message, to update message text in widget
    #see above in LoginPage
    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width*0.9, None)
    



class SignUpPage(Image):
    def __init__(self):     #add **kwargs if not running
        super().__init__()

        self.source = 'guudu-6.jpg'
        self.allow_stretch = True
        self.keep_ratio = False
        self.color=[1,1,1,0.7]

        self.signup_label = Label(
            text='[color=#ffffff]Sign-Up Page[/color]',
            font_size=89,
            font_name='./IMPRISHA',
            pos=(350,450),
            markup=True
        )

        self.username_input = TextInput(
            multiline=False,
            #size_hint=(0.35,0.08),
            #pos_hint={'x':0.5, 'y':1},
            size=(280,50),
            pos=(260,359),
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.95),
            foreground_color=(1,1,1,1), #text color
            font_size='17sp',
            hint_text='Username',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13
        )

        self.password_input = TextInput(
            multiline=False,
            size=(280,50),
            pos=(260,267),
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.95),
            foreground_color=(1,1,1,1), #text color
            font_size='17sp',
            hint_text='Password',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13,
            password=True
        )

        self.confirm_password_input = TextInput(
            multiline=False,
            size=(280,50),
            pos=(260,175),
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.95),
            foreground_color=(1,1,1,1), #text color
            font_size='17sp',
            hint_text='Confirm Password',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13,
            password=True
        )

        self.info_box_1 = Label(
            text='',
            font_size=16,
            pos=(350,20)
        )

        self.info_box_2 = Label(
            text='',
            font_size=16,
            pos=(350,-20)
        )

        self.signup_button = Button(
            text='Sign Up',
            #size_hint=(0.20,0.08),
            #pos_hint={'x':0.345, 'y':0.30}
            pos=(315,90),
            size=(160,48),
            font_size=20,
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            background_normal=''
        )
        self.signup_button.bind(on_press=self.signup_button_function)

        self.add_widget(self.signup_button)
        self.add_widget(self.info_box_2)
        self.add_widget(self.info_box_1)
        self.add_widget(self.confirm_password_input)
        self.add_widget(self.password_input)
        self.add_widget(self.username_input)
        self.add_widget(self.signup_label)


    def signup_button_function(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()

        if len(username) == 0:
            self.info_box_1.text = 'Username connot be empty!'
            return
        if len(username) > 20:
            self.info_box_1.text = 'Username must be less than 21 characters'
            self.username_input.text = ''
            return
        
        if len(password) < 9 or len(password) > 21:
            self.info_box_1.text = 'Password must be between 8 to 21 characters'
            self.password_input.text = ''
            return

        if confirm_password != password:
            self.info_box_2.text = 'Passwords do not match'
            self.confirm_password_input.text = ''
            return
        else:
            self.info_box_2.text = ''
   
        new_entry = [username, password, 'new', 'new', 'Non-Admin']
        df = None
        df = socket_client.get_df(show_error)

        if username in df['Username'].unique():
            self.info_box_2.text = 'This username already exists, choose a new one'
            self.username_input.text = ''
            return

        l = len(df)
        df.loc[l] = new_entry

        socket_client.send_df(df, show_error)

        self.username_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''

        chat_app.screen_manager.transition.direction = 'left'
        chat_app.screen_manager.current = 'Login'


class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #We need 2 widgets, a chat history label where msgs will update, and
        # an empty label below it, so that we can scroll down and see new messages
        #otherwise screen will always be at top and seeing new msgs will be difficult
        #so we make a grid layout and add these widgets in it, cuz scrollview doesnt allow more than 1 widget
        ####
        # Layout is going to have one collumn and and size_hint_y set to None,
        # so height wo't default to any size (we are going to set it on our own)
        self.layout = GridLayout(
            cols=1,
            size_hint_y=None
        )
        self.add_widget(self.layout)

        self.chat_history = Label(
            size_hint_y=None,
            markup=True
        )
        self.scroll_to_point = Label()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    # Method called externally to add new message to the chat history
    def update_chat_history(self, message):
        #1st add new line and the message itself
        self.chat_history.text += '\n' + message
        self.chat_history.font_size = '20sp'

        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at above)
        self.layout.height = self.chat_history.texture_size[1] + 15
        # Set chat history label to whatever height of chat history text is
        self.chat_history.height = self.chat_history.texture_size[1]
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.chat_history.text_size = (self.chat_history.width*0.98, None)

        # As we are updating above, text height, so also label and layout height are going to be bigger
        # than the area we have for this widget. ScrollView is going to add a scroll, but won't
        # scroll to the botton, nor is there a method that can do that.
        # That's why we want additional, empty widget below whole text - just to be able to scroll to it,
        # so scroll to the bottom of the layout
        #?????????????????
        #scroll_to is a method of ScrollView
        self.scroll_to(self.scroll_to_point)


class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.background = Image(
                source='guddu-16.jpg',
                allow_stretch=True,
                keep_ratio=False,
                size=self.size,
                pos=self.pos,
                color=[1,1,1,0.6]
            )

        self.bind(pos=self.update_image,
            size=self.update_image)


        self.rows = 3
        self.cols = 1

        self.history = ScrollableLabel(
            height=Window.size[1]*0.8,
            size_hint_y=None    #SEE AGAIN
        )
        self.add_widget(self.history)

        self.history.update_chat_history('')

        self.username_text = Label(
            text=f'[color=#52ff57]{chat_app.loginpage.role_for_chatpage}[/color]',
            width=Window.size[0]*0.45,
            size_hint_x=None,
            markup=True,
            font_size=25,
            font_name='./MAGNETOB',
            bold=True
        )

        self.admin_list_button = Button(
            text='Admin List',
            width=Window.size[0]*0.35,
            size_hint_x=None,
            font_size=20,
            background_color=[0.01176470588,0.4,0.42745098039,0.89],
            background_normal=''
        )
        # self.admin_list_button.text = 'Admin List'
        # self.admin_list_button.width = Window.size[0]*0.4
        # self.size_hint_x = None
        # self.font_size = 20
        # self.back_color = (0.01176470588,0.20784313725,0.42745098039,0.89)
        self.admin_list_button.bind(on_press=self.goto_admin_list)

        self.exit_button = Button(
            text='Exit',
            font_size=20,
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            background_normal=''
        )
        self.exit_button.bind(on_press=self.exit_chatpage)

        above_bottom_line = GridLayout(cols=3)
        above_bottom_line.add_widget(self.username_text)
        above_bottom_line.add_widget(self.admin_list_button)
        above_bottom_line.add_widget(self.exit_button)
        self.add_widget(above_bottom_line)

        self.new_message = TextInput(
            width=Window.size[0]*0.8,
            size_hint_x=None,
            multiline=False,
            cursor_color=[0.27843137254,1,1,1],
            background_color=(0,0,0,0.8),
            foreground_color=(1,1,1,1), #text color
            font_size='17sp',
            hint_text='Type your message here',
            hint_text_color=[0.27843137254,1,1,0.5],
            padding_x=10,
            padding_y=13
        )

        self.send_button = Button(
            text='Send',
            font_size=20,
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            #background_normal=''
        )
        self.send_button.bind(on_press=self.send_message)


        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send_button)
        self.add_widget(bottom_line)


        # To be able to send message on Enter key, we want to listen to keypresses
        Window.bind(on_key_down=self.on_key_down)

        Clock.schedule_once(self.focus_text_input, 1)

        socket_client.start_listening(self.incoming_message, show_error)

    
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        #only take action when enter key is pressed
        if keycode == 40:
            self.send_message(None)


    def send_message(self, instance):
        message = self.new_message.text.strip('[')
        self.new_message.text = ''

        # If there is any message - add it to chat history and send to the server
        if message:
            # Our messages - use red color for the name (FOR NOW)
            self.history.update_chat_history(f'[color=#52ff63]{chat_app.loginpage.username_input.text}[/color] > {message}')
            socket_client.send(message)

            Clock.schedule_once(self.focus_text_input, 0.1)

        
    def focus_text_input(self, _):
        self.new_message.focus = True


    # Passed to sockets client, get's called on new message
    def incoming_message(self, username, message):
        self.history.update_chat_history(f'[color=#00ffff]{username} [/color]> {message}')


    def update_image(self, instance, value):
        self.background.pos = self.pos
        self.background.size = self.size

    def goto_admin_list(self, instance):

        if chat_app.loginpage.role_for_chatpage == 'Admin':
            #chat_app.create_admin_list()
            chat_app.screen_manager.current = 'Admin List'
        else:
            return

    def exit_chatpage(self, instance):
        
        today = date.today()
        now = datetime.now()

        last_seen_date = today.strftime("%d/%m/%Y")
        last_seen_time = now.strftime("%H:%M:%S")

        username = chat_app.loginpage.username_input.text

        df = socket_client.get_df(show_error)

        password = df.loc[df['Username'] == username].get('Password').to_string()
        password = password[2:].strip()
        #print(password)

        role = df.loc[df['Username'] == username].get('Role').to_string()
        role = role[2:].strip()

        changed_entry = [username, password, last_seen_date, last_seen_time, role]
        location = df[df['Username'] == username].index[0]
        df.loc[location] = changed_entry

        socket_client.send_df(df, show_error)

        # #date
        # chat_app.adminlist.admin_list.current_username.parent.children[3].text = last_seen_date
        # #time
        # chat_app.adminlist.admin_list.current_username.parent.children[2].text = last_seen_time

        chat_app.infopage.message.text = 'Exiting Application...'
        chat_app.screen_manager.current = 'Info Page'
        Clock.schedule_once(sys.exit, 1)


class ScrollableWindow(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #main layout which wll contain other grids (cus ScrollView accepts only 1 child)
        self.layout = GridLayout(
            cols=1,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)

        #used for updating last seen details when exit button is pressed in admin list
        #self.current_user_grid = None
        self.current_username = chat_app.loginpage.username_input.text

        self.df = None
        self.df = socket_client.get_df(show_error)
        #print(self.df)
        for i in range(len(self.df)):
            grid = GridLayout(
                cols=5,
                rows=1,
                size_hint_y=None
            )

            # if self.current_username == self.df.iloc[i]['Username']:
            #     print("YES")
            #     self.current_user_grid = grid

            username_label = Label(
                size_hint_y=None,
                markup=True,
                text=self.df.iloc[i]['Username']
            )
            date_label = Label(
                size_hint_y=None,
                markup=True,
                text=self.df.iloc[i]['Last Seen Date']
            )
            time_label = Label(
                size_hint_y=None,
                markup=True,
                text=self.df.iloc[i]['Last Seen Time']
            )
            role_label = Label(
                size_hint_y=None,
                markup=True,
                text=self.df.iloc[i]['Role']
            )

            if self.df.iloc[i]['Role'] == 'Admin':
                role_bool = True
                #switch_disabled = True
            else:
                role_bool = False
                #switch_disabled = False

            upgrade_switch = Custom(
                active=role_bool,
            )
            #upgrade_switch.canvas.add(Color(1.,0,0))
            upgrade_switch.bind(active=self.switch_action)

            grid.add_widget(username_label)
            grid.add_widget(date_label)
            grid.add_widget(time_label)
            grid.add_widget(role_label)
            grid.add_widget(upgrade_switch)
            self.layout.add_widget(grid)

        
        self.scroll_to_point = Label()
        self.layout.add_widget(self.scroll_to_point)

        #??
        # self.scroll_to(self.scroll_to_point)


    def switch_action(self, instance, value):
        #print('the switch', instance, 'is', value)
        if value == False and instance.parent.children[1].text == 'Admin':
            instance.active = True
            return
        #making another function cus if switch is active when we click it (above if condition)
        #then instance.active is made True, means its same as switch click
        #and again switch_action() will be called as its binded to switch
        #then the code in switch_action_continued() will execute (if switch_action_continued() wasnt made and code written here only)
        #we dont want that ofc, after executing if stmt it should return and not be called again
        ###? still problems, removed changes, if later some prblm occurs then just deactivate switch
        self.switch_action_continued(instance, value)
        

    def switch_action_continued(self, instance, value):
        username = str(instance.parent.children[4].text).strip()
        date = str(instance.parent.children[3].text).strip()
        time = str(instance.parent.children[2].text).strip()
        role = 'Admin'  #instance.parent.children[1].text
        password = self.df.loc[self.df['Username'] == username].get('Password').to_string()  #dunno why index num and 4 spaces coming
        password = password[2:].strip()
        #print(password)

        #print(self.df)
        changed_entry = [username, password, date, time, role]
        location = self.df[self.df['Username'] == username].index[0]

        self.df.loc[location] = changed_entry
        #print(self.df)

        instance.parent.children[1].text = role

        socket_client.send_df(self.df, show_error)


    def called_by_adminlist(self):
        self.scroll_to(self.scroll_to_point)


class AdminList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.background = Image(
                source='guddu-7.jpg',
                allow_stretch=True,
                keep_ratio=False,
                size=self.size,
                pos=self.pos
            )
        self.bind(pos=self.update_image,
        size=self.update_image)

        self.cols = 1
        self.rows = 3

        self.top_line = GridLayout(
            cols=5,
            rows=1,
            height=0.1*Window.size[1],
            size_hint_y=None
        )

        self.username_label = Label(
            size_hint_y=None,
            markup=True,
            text='Username',
            font_size=21,
            font_name='./ROCCB___'
            #valign='top'
        )
        self.date_label = Label(
            size_hint_y=None,
            markup=True,
            text='Last Seen Date',
            font_size=21,
            font_name='./ROCCB___'
        )
        self.time_label = Label(
            size_hint_y=None,
            markup=True,
            text='Last Seen Time',
            font_size=21,
            font_name='./ROCCB___'
        )
        self.role_label = Label(
            size_hint_y=None,
            markup=True,
            text='Role',
            font_size=21,
            font_name='./ROCCB___'
        )
        self.upgrade_label = Label(
            size_hint_y=None,
            markup=True,
            text='Upgrade',
            font_size=21,
            font_name='./ROCCB___'
        )

        self.top_line.add_widget(self.username_label)
        self.top_line.add_widget(self.date_label)
        self.top_line.add_widget(self.time_label)
        self.top_line.add_widget(self.role_label)
        self.top_line.add_widget(self.upgrade_label)
        self.add_widget(self.top_line)

        self.admin_list = ScrollableWindow(
            # height=0.8*Window.size[1],
            # size_hint_y=None
        )
        self.admin_list.called_by_adminlist()
        
        self.add_widget(self.admin_list)

        self.bottom_line = GridLayout(
            cols=3,
            rows=1,
            height=0.1*Window.size[1],
            size_hint_y=None
        )

        self.bottom_line.add_widget(Label(width=0.4*Window.size[0], size_hint_x=None))
        
        self.exit_button = Button(
            text='Back',
            font_size=20,
            width=0.2*Window.size[0],
            size_hint_x=None,
            background_color=[0.01176470588,0.20784313725,0.42745098039,0.89],
            background_normal=''
        )
        self.exit_button.bind(on_press=self.update_details_and_exit)

        self.bottom_line.add_widget(self.exit_button)
        self.bottom_line.add_widget(Label(width=0.4*Window.size[0], size_hint_x=None))
        self.add_widget(self.bottom_line)


    def update_details_and_exit(self, instance):
        # #date
        # today = date.today()
        # self.admin_list.current_user_grid.children[3] = today.strftime("%d/%m/%Y")
        # #time
        # now = datetime.now()
        # self.admin_list.current_user_grid.children[2] = now.strftime("%H:%M:%S")
        # today = date.today()
        # now = datetime.now()

        # last_seen_date = today.strftime("%d/%m/%Y")
        # last_seen_time = now.strftime("%H:%M:%S")
        # username = self.admin_list.current_username

        # password = self.admin_list.df.loc[self.admin_list.df['Username'] == username].get('Password').to_string()
        # password = password[2:].strip()

        # role = self.admin_list.df.loc[self.admin_list.df['Username'] == username].get('Role').to_string()
        # role = role[2:].strip()

        # changed_entry = [username, password, last_seen_date, last_seen_time, role]
        # location = self.admin_list.df[self.admin_list.df['Username'] == username].index[0]
        # self.admin_list.df.loc[location] = changed_entry

        # socket_client.send_df(self.admin_list.df, show_error)

        chat_app.screen_manager.transition.direction = 'right'
        chat_app.screen_manager.current = 'Chat Page'
        # chat_app.infopage.message.text = 'Exiting Application...'
        # chat_app.screen_manager.current = 'Info Page'
        # Clock.schedule_once(sys.exit, 1)

    def update_image(self, instance, value):
        self.background.pos = self.pos
        self.background.size = self.size



class TestApp(App):
    def build(self):
        #Window.borderless = True
        #Window.set_icon(path)
        #Window.set_system_cursor('ibeam')
        #Window.set_title('Chat Room')
        Config.resizable = 0    #not working
    

        self.screen_manager = ScreenManager()

        self.loginpage = LoginPage()
        screen = Screen(name='Login')
        screen.add_widget(self.loginpage)
        self.screen_manager.add_widget(screen)

        self.infopage = InfoPage()
        screen = Screen(name='Info Page')
        screen.add_widget(self.infopage)
        self.screen_manager.add_widget(screen)

        self.signuppage = SignUpPage()
        screen = Screen(name='SignUp')
        screen.add_widget(self.signuppage)
        self.screen_manager.add_widget(screen)

        # self.chatpage = ChatPage()
        # screen = Screen(name='Chat Page')
        # screen.add_widget(self.chatpage)
        # self.screen_manager.add_widget(screen)

        #self.screen_manager.current = 'Chat Page'

        #if it runs slow then only make another function which makes admin list inside chat page when pressed a button
        #and then handle for multiple screens warning in kivy
        self.adminlist = AdminList()
        screen = Screen(name='Admin List')
        screen.add_widget(self.adminlist)
        self.screen_manager.add_widget(screen)
        #self.screen_manager.transition = RiseInTransition()
        #admin_list_counter += 1
        #self.screen_manager.current = 'Admin List'
        
        #chat_app.screen_manager.current = 'Admin List'
        return self.screen_manager


    def create_chat_page(self):
        self.chatpage = ChatPage()
        screen = Screen(name='Chat Page')
        screen.add_widget(self.chatpage)
        self.screen_manager.add_widget(screen)



if __name__ == '__main__':
    chat_app = TestApp()
    chat_app.run()
