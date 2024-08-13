import customtkinter as ct
from webdriver import batch
import requests
from threading import Thread
import webbrowser
def open_url(url):
    webbrowser.open_new_tab(url)

ct.set_appearance_mode("dark") 
ct.set_default_color_theme("blue")

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        # window config
        self.geometry("933x700")
        self.title("Wp-auto")
        self.bind('<Return>', lambda e: self.confirm_if_focus_not_in_text())

        self.main_frame = ct.CTkFrame(master=self, fg_color='transparent')
        self.main_frame.grid(padx=2)
        
        self.secciones_frame = ct.CTkScrollableFrame(master=self.main_frame,height=10) 
        self.secciones_frame.grid(column=1, ipadx=242, ipady=237, pady=8)
        self.secciones_frame._parent_canvas.configure(yscrollincrement=3)

        self.side_frame = ct.CTkFrame(master=self.main_frame, height=10) 
        self.side_frame.grid(column=0, row=0, padx=8, sticky='ns', pady=8, ipady=0)
        self.side_frame_inner_container = ct.CTkFrame(master=self.side_frame, fg_color='transparent') 
        self.side_frame_inner_container.grid()
        self.gen_btn_inner = ct.CTkFrame(master=self.side_frame_inner_container, fg_color='transparent') 
        self.confirm_btn_inner = ct.CTkFrame(master=self.side_frame_inner_container, fg_color='transparent')
        self.middle_frame = ct.CTkFrame(master=self.side_frame_inner_container, fg_color='transparent') 
        self.settings_inner = ct.CTkFrame(master=self.middle_frame, fg_color='transparent')
        self.new_section_btn = ct.CTkButton(master=self.secciones_frame,
                                             text="New section",
                                             command=self.nueva_seccion,
                                             width=180,
                                             height=45)
        self.new_section_btn.grid(padx=250, pady=10)
        self.new_section_btn.grid_propagate(0)

        self.elementor_warning_lbl = ct.CTkLabel(master=self.gen_btn_inner, text="WP site and Elementor plugin \nmust be already installed \nand ready to use.")
        self.elementor_warning_lbl.grid(sticky='s', padx=5, pady=33)

        self.elementor_warning_lbl2 = ct.CTkLabel(master=self.gen_btn_inner, text="Reload in case a blocking \npopup doesn't close.")
        self.elementor_warning_lbl2.grid(sticky='s', padx=5, pady=32)

        self.lang_switch_lbl = ct.CTkLabel(master=self.settings_inner,text="Select Site Language")
        self.lang_switch_lbl.grid(sticky='w',padx=13)
        self.lang_switch = ct.CTkSegmentedButton(master=self.settings_inner)
        self.lang_switch.grid(sticky='w',padx=7)
        self.lang_switch.configure(values=['Español','English'])
        self.lang_switch.set("Español")

        self.host_lbl = ct.CTkLabel(master=self.settings_inner, text='Host')
        self.host_lbl.grid(sticky='w',padx=13)
        self.host_entry = ct.CTkEntry(master=self.settings_inner)
        self.host_entry.grid(sticky='w',padx=5, ipadx=20)
        self.user_lbl = ct.CTkLabel(master=self.settings_inner, text='User')
        self.user_lbl.grid(sticky='w',padx=13)
        self.user_entry = ct.CTkEntry(master=self.settings_inner)
        self.user_entry.grid(sticky='w',padx=5, ipadx=20)
        self.pass_lbl = ct.CTkLabel(master=self.settings_inner, text='Password')
        self.pass_lbl.grid(sticky='w',padx=13)
        self.pass_entry = ct.CTkEntry(master=self.settings_inner)
        self.pass_entry.grid(sticky='w',padx=5, ipadx=20)
        self.confirm_all_btn = ct.CTkButton(master=self.confirm_btn_inner,
                                            text="Confirm & Run",
                                            command=self.confirm_all,
                                            width=180,
                                            height=45)
        self.confirm_all_btn.grid(padx=3, pady=10)
        self.gen_btn_inner.grid()
        self.settings_inner.grid(sticky='we', pady=8, padx=3)
        self.middle_frame.grid(pady=0)
        self.confirm_btn_inner.grid()
        self.secciones = {}

    def confirm_if_focus_not_in_text(self):
        wid = str(self.focus_get())
        if not wid[-5:] == '!text':
            self.confirm_all()
        else:
            pass

    def eliminar_seccion_por_id(self, id):
        del self.secciones[id]

    seccion_id = 0
    def nueva_seccion(self):
        self.secciones[self.seccion_id] = Seccion(master=self.secciones_frame,
                               controller=self,
                               id=self.seccion_id)
        self.seccion_id += 1
        self.new_section_btn.grid(row=self.seccion_id) #siempre row+1 de Seccion

    def report(self):
        if len(self.secciones) == 0:
            print("Empty sections list")
        else:
            print(f'Number of sections: {len(self.secciones)}') 
        for seccion_id, s in self.secciones.items():
            print(f'Section id-{seccion_id}')
            print(f'Preset {s.preset}')
            if not any(s.containers.items()):
                print("vacio\n")
            else:
                for k,c in s.containers.items():
                    print(f'{repr(c)} {k}')
                    for _,w in c.widgets.items():
                        print(repr(w))
                        if repr(w) == 'HeaderWidget':
                            print(w.en.get())
                        if repr(w) == 'TextWidget':
                            print(w.txtbox.get("1.0",'end'))
            print('')
    
    def empty_fields_check(self,host_url, user, passw):
        if len(host_url) == 0 or len(user) == 0 or len(passw) == 0:
            return True
        else:
            return False
    
    def empty_sections_check(self):
        if len(self.secciones) == 0:
            return True
        else:
            return False
            
    def confirm_all(self, event=None):
        print('\n...System checks...System checks...') 
        print('...')

        # wiping popups
        if self.active_popup == True:
            self.popup.destroy_popup()

        # collecting settings
        host_url = self.host_entry.get()
        if not host_url.startswith("http"):
            host_url = "http://" + host_url
        if not host_url.endswith('/wp-admin') or not host_url.endswith('/wp-admin/'):
            host_url = host_url + '/wp-admin'
        user = self.user_entry.get()
        passw = self.pass_entry.get()
        lang = self.lang_switch.get()

        # checking for settings errors
        empty_settings_fields = self.empty_fields_check(host_url, user, passw)
        if empty_settings_fields == True:
            self.create_popup(type='error',text='Empty configuration fields')
            return print("...Cancelando...")
        #checking for sections errors
        empty_section_list = self.empty_sections_check()
        if empty_section_list == True:
            self.create_popup(type='error',text='No sections added')
            return print("...Cancelando...")
        else:
            print("Configs - OK\n")
        print(f"Revisando url - {host_url}")
        try:
            request = requests.get(host_url)
        except:
            print("URL not valid")
            try:
                print("Intentando con .com")
                host_url = host_url + ".com"
                request = requests.get(host_url)
            except:
                self.create_popup(type='error',text='URL not valid')
                return print("Cancelando")
        print(f"Url {host_url} - OK")

        print("...RUNNING...")
        batch_init = {
            'Host Url':host_url,
            'User': user,
            'Pass': passw,
            'Sections': self.secciones,
        } 
        wDriver_thread = Thread(target=batch,args=(batch_init,lang,self))
        wDriver_thread.start()
        #DEBUG
        # print(f'batch final: {batch_init}')
        # self.report()

    def failed(self):
        self.create_popup(type='error',text='Webdriver error.\nCheck settings and try again.')

    def success(self):
        host_url = self.host_entry.get()
        url = host_url + '/wp-admin/edit.php?post_type=page'
        self.create_popup(type='success',text=url)

    active_popup = False
    def create_popup(self,type, text):
        if type == 'error':
            if not self.active_popup:
                self.popup = ErrorPopUp(master=self.main_frame, controller=self, text=text)
                self.active_popup = not self.active_popup
        if type == 'success':
            if not self.active_popup:
                self.popup = SuccessPopUp(master=self.main_frame, controller=self, text=text)
                self.active_popup = not self.active_popup

class PopUp(ct.CTkBaseClass):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.popup_frame = ct.CTkFrame(master=self.master, fg_color='gray40')
        self.popup_frame.place(relx=0.55, rely=0.55, anchor='s')
        self.popup_inner_frame = ct.CTkFrame(master=self.popup_frame, fg_color='gray40')
        self.popup_inner_frame.grid(padx=12, pady=12)
        self.main_lbl = ct.CTkLabel(self.popup_inner_frame)
        self.main_lbl.grid()
        self.separator = ct.CTkFrame(self.popup_inner_frame, width=20, height=3, fg_color="#4f4f4f")
        self.separator.grid(padx=5, pady=2, sticky="ew")
        self.desc_lbl = ct.CTkLabel(self.popup_inner_frame)
        self.desc_lbl.grid()
        self.close_popup_btn = ct.CTkButton(self.popup_inner_frame,text='[CLOSE]',
                                            command=self.destroy_popup,
                                            border_width=1,width=100)
        self.close_popup_btn.grid(pady=3)
        self.controller.bind('<Escape>',self.destroy_popup)
    
    def destroy_popup(self, event=None):
        self.controller.active_popup = not self.controller.active_popup
        self.popup_frame.destroy()

class SuccessPopUp(PopUp):
    def __init__(self, master, controller, text):
        super().__init__(master, controller)
        self.main_lbl.configure(text="New page created successfully.")
        self.desc_lbl.configure(text=f'Site pages: {text}')
        self.desc_lbl.configure(cursor='hand2')
        self.desc_lbl.bind('<Button-1>', lambda e:open_url(text))
        self.close_popup_btn.configure(fg_color='darkgreen',hover_color='green')

class ErrorPopUp(PopUp):
    def __init__(self, master, controller, text):
        super().__init__(master, controller)
        self.main_lbl.configure(text="Something went wrong")
        self.desc_lbl.configure(text=text)
        self.close_popup_btn.configure(fg_color='darkred',hover_color='red')

class Seccion(ct.CTkBaseClass):
    collapsed = False
    container_id = 0
    def __init__(self, master,controller,id):
        super().__init__(master)
        self.controller = controller
        self.id = id
        self.row = self.id
        self.containers = {}
        self.preset = 'c100' #default
        self.master_secciones_frame = ct.CTkFrame(master=self.master, fg_color='gray20', height=230)
        self.master_secciones_frame.grid(column=0,pady=5,ipadx=240,row=self.row)
        self.master_secciones_frame.grid_propagate(0)
        self.generar_presets()
        
    def generar_presets(self):
        self.outer_structure_presets_frame = ct.CTkFrame(master=self.master_secciones_frame, fg_color='transparent')
        self.outer_structure_presets_frame.grid(padx=110,pady=61)
        self.structure_presets_frame = ct.CTkFrame(master=self.outer_structure_presets_frame, fg_color='transparent') 
        self.structure_presets_frame.grid(padx=10,pady=10)

        self.btn = ct.CTkButton(master=self.structure_presets_frame,
                                text="Column direction",
                                command=lambda: self.final_structure("Column direction"))
        self.btn.grid(column=0,row=0,padx=3,pady=5)
        self.btn2 = ct.CTkButton(master=self.structure_presets_frame,
                                 text="Row direction",
                                 command=lambda: self.final_structure("Row direction"))
        self.btn2.grid(column=1,row=0,padx=3,pady=5)
        self.btn3 = ct.CTkButton(master=self.structure_presets_frame,
                                 text="2 Columns", #50-50
                                 command=lambda: self.final_structure("50-50"))
        self.btn3.grid(column=2,row=0,padx=3,pady=5)
        self.btn4 = ct.CTkButton(master=self.structure_presets_frame,
                                 text="4 Columns", #25-25-25-25
                                 command=lambda: self.final_structure("25-25-25-25"))
        self.btn4.grid(column=0,row=1,padx=3,pady=5)
        self.btn5 = ct.CTkButton(master=self.structure_presets_frame,
                                 text="2 Columns 2 Rows", #50-50-50-50
                                 command=lambda: self.final_structure("50-50-50-50"))
        self.btn5.grid(column=1,row=1,padx=3,pady=5)
        self.btn6 = ct.CTkButton(master=self.structure_presets_frame,
                                 text="3 Columns 2 Rows", #33-33-33-33-33-33
                                 command=lambda: self.final_structure("33-33-33-33-33-33"))
        self.btn6.grid(column=2,row=1,padx=3,pady=5)

    def final_structure(self,preset):
        #make frames
        self.inner_master = ct.CTkFrame(master=self.master_secciones_frame, fg_color='transparent', height=215) # toggle/del & 'section lbl' frm 
        self.inner_master.grid(padx=3,ipadx=0, pady=10)
        self.master_secciones_frame.grid_propagate(1) 
        self.master_secciones_frame.grid_configure(ipadx=0) 
        self.generar_top_menu() # toggle/del & 'section lbl'
        self.gen_frame = ct.CTkFrame(master=self.inner_master, fg_color='transparent') 
        self.gen_frame.grid()

        #make containers
        if preset == "Column direction":
            self.preset = "c100"
            self.containers[self.container_id] =  Container(master=self.gen_frame,
                                                            column=0,
                                                            row=0,
                                                            headerWd_width=400,
                                                            textWd_width=400,
                                                            addWd_padx=170)
            self.container_id +=1

        if preset == "Row direction":
            self.preset = "r100" 
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                           column=0,
                                                           row=0,
                                                            headerWd_width=400,
                                                            textWd_width=400,
                                                            addWd_padx=170)
            self.container_id +=1  

        if preset == "50-50":
            self.preset = preset
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=0,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=0,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1

        if preset == "25-25-25-25":
            self.preset = preset
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=0,
                                                headerWd_width=152,
                                                textWd_width=150,
                                                addWd_padx=30)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=0,
                                                headerWd_width=152,
                                                textWd_width=150,
                                                addWd_padx=30)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=2,
                                                row=0,
                                                headerWd_width=152,
                                                textWd_width=150,
                                                addWd_padx=30)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=3,
                                                row=0,
                                                headerWd_width=152,
                                                textWd_width=150,
                                                addWd_padx=30)
            self.container_id +=1

        if preset == "50-50-50-50":
            self.preset = preset
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=0,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=0,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=1,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=1,
                                                headerWd_width=300,
                                                textWd_width=300,
                                                addWd_padx=105)
            self.container_id +=1

        if preset == '33-33-33-33-33-33':
            self.preset = preset
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=0,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=0,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=2,
                                                row=0,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=0,
                                                row=1,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=1,
                                                row=1,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
            self.containers[self.container_id] = Container(master=self.gen_frame,
                                                column=2,
                                                row=1,
                                                headerWd_width=208,
                                                textWd_width=208,
                                                addWd_padx=57)
            self.container_id +=1
        self.outer_structure_presets_frame.destroy()

    def generar_top_menu(self):
        self.top_menu_frame = ct.CTkFrame(master=self.inner_master, fg_color='transparent')
        self.top_menu_frame.grid()
        self.toggle_btn = ct.CTkButton(master=self.top_menu_frame,
                                       text="-",
                                       width=30,
                                       height=25,
                                       command=self.toggle)
        self.toggle_btn.grid(row=0, sticky='w', padx=6)
        self.section_lbl = ct.CTkLabel(master=self.top_menu_frame,
                                       text=" ") # SEPARATOR
        self.section_lbl.grid(padx=315,row=0,sticky='n')
        self.del_btn = ct.CTkButton(master=self.top_menu_frame,
                                    text="X",
                                    width=30,
                                    height=25,
                                    command=self.eliminar,
                                    hover_color='darkred')
        self.del_btn.grid(column=1, row=0, sticky='e', padx=6)
  
    def eliminar(self):
        self.master_secciones_frame.destroy()
        self.controller.eliminar_seccion_por_id(self.id)
        self.destroy()
         
    def toggle(self):
        # desaparece
        if self.collapsed is not True:
            self.gen_frame.grid_forget()
            self.gen_frame.configure(height=0)
            self.toggle_btn.configure(text='+')
        # aparece
        if self.collapsed is True:
            self.gen_frame.grid(padx=5) 
            self.gen_frame.configure(height=10)
            self.toggle_btn.configure(text='-')
        self.collapsed = not self.collapsed

class Widget:
    """Elementor Widgets"""
    def __init__(self, master, controller, id,row):
        self.controller = controller
        self.id = id
        self.frm = ct.CTkFrame(master=master,fg_color='transparent')
        self.frm.grid(pady=3,row=row)
        self.lbl = ct.CTkLabel(master=self.frm)
        self.lbl.grid(sticky='w')
        self.del_btn = ct.CTkButton(master=self.frm,
                                    text='X',
                                    width=12,
                                    height=12,
                                    command=self.del_widget,
                                    hover_color='darkred')
        self.del_btn.grid(row=0, sticky='e')
    
    def del_widget(self):
        self.frm.destroy()
        self.controller.eliminar_widget_por_id(self.id)

class HeaderWidget(Widget):
    def __init__(self, master, controller, id,row,width): 
        super().__init__(master, controller, id,row)
        self.lbl.configure(text='Header')
        self.frm.grid(padx=4) 
        self.en = ct.CTkEntry(master=self.frm, height=30,width=width) 
        self.en.grid(sticky='we') 
    
    def __str__(self):
        return "HeaderWidget"
    
    def __repr__(self):
        return "HeaderWidget"

class TextWidget(Widget):
    def __init__(self, master, controller, id, row, width):
        super().__init__(master, controller,id, row)
        self.lbl.configure(text='Text')
        self.frm.grid(padx=4) 
        self.txtbox = ct.CTkTextbox(master=self.frm, height=100,width=width)
        self.txtbox.grid(sticky='we') 

    def __str__(self):
        return "TextWidget"
    
    def __repr__(self):
        return "TextWidget"

class WidgetSelection:
    def __init__(self, master, controller, id, row):
        self.row = row
        self.id=id
        self.master=master
        self.controller=controller
        self.frm = ct.CTkFrame(master=self.master, fg_color='transparent')
        self.frm.grid(row=self.row,pady=3,padx=3)
        #entry option
        self.header_widget_btn = ct.CTkButton(master=self.frm,
                                              text="Encabezado",
                                              command=self.generar_encabezado,
                                              width=30)
        self.header_widget_btn.grid(padx=2,pady=10,
                                    column=0,row=self.row)
        #text option
        self.text_widget_btn = ct.CTkButton(master=self.frm,
                                            text="Texto",
                                            command=self.generar_texto,
                                            width=20)                             
        self.text_widget_btn.grid(padx=2,pady=10,
                                  column=1,row=self.row)
        self.row +=1
    
    def generar_encabezado(self):
        self.controller.generar_encabezado(self.row,)
        self.frm.destroy()
        self.controller.destroy_widget_selection_por_id(self.id)
    
    def generar_texto(self):
        self.controller.generar_texto(self.row)
        self.frm.destroy()
        self.controller.destroy_widget_selection_por_id(self.id)

class Container:
    wdgt_id = 0
    def __init__(self, master, column, row, headerWd_width, textWd_width, addWd_padx):
        self.widgets = {}
        self.master = master
        self.row_helper = 0
        self.headerWd_width = headerWd_width
        self.textWd_width = textWd_width
        self.frm = ct.CTkFrame(master=self.master,fg_color='gray40') 
        self.frm.grid(padx=3,pady=5, column=column,row=row)

        # default content
        self.widgets[self.wdgt_id] = HeaderWidget(master=self.frm,controller=self,
                                                  id=self.wdgt_id,row=self.row_helper,
                                                  width=self.headerWd_width) 
        self.wdgt_id += 1
        self.row_helper +=1
        self.widgets[self.wdgt_id] = TextWidget(master=self.frm,controller=self,
                                                id=self.wdgt_id,row=self.row_helper,
                                                width=self.textWd_width)
        self.wdgt_id += 1
        self.row_helper +=1
        # end default content

        self.add_widget_btn = ct.CTkButton(master=self.frm,text='Add widget',
                                        width=100,height=30,
                                        command=self.make_widget_selection)
        self.add_widget_btn.grid(pady=10,padx=addWd_padx,row=self.row_helper)
        self.row_helper+=1

    widget_selections = {}
    widget_selections_id = 0
    def make_widget_selection(self,):
        self.widget_selections[self.widget_selections_id] = WidgetSelection(master=self.frm,row=self.row_helper,
                                                                            controller=self,id=self.widget_selections_id)
        self.widget_selections_id+=1
        self.row_helper += 1
        #move add_widget_btn
        self.add_widget_btn.grid(row=self.row_helper)
        self.row_helper+=1
    
    def destroy_widget_selection_por_id(self, id):
        del self.widget_selections[id]

    ################# WIDGETS #################
    def generar_encabezado(self,exact_row):
        self.widgets[self.wdgt_id] = HeaderWidget(master=self.frm,controller=self,
                                                  id=self.wdgt_id,row=exact_row,
                                                  width=self.headerWd_width) 
        self.wdgt_id += 1
        self.add_widget_btn.grid(row=self.row_helper)
    
    def generar_texto(self,exact_row):
        self.widgets[self.wdgt_id] = TextWidget(master=self.frm,controller=self,
                                                id=self.wdgt_id,row=exact_row,
                                                width=self.textWd_width)
        self.wdgt_id += 1
        self.add_widget_btn.grid(row=self.row_helper)

    def eliminar_widget_por_id(self, id):
        del self.widgets[id]
    
    def __repr__(self):
        return "Container"

if __name__ == '__main__':
    app = App()
    app.mainloop()
