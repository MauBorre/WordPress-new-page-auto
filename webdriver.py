from playwright.sync_api import sync_playwright
#https://playwright.dev/python/docs/input
#https://playwright.dev/python/docs/locators
#tested wp version: 6.5.3

# translation matching by index
lang_es = ['Encabezado',
           'Escribe tu título',
           'Editor de texto',
           'HTML',
           'Publicar']

lang_en = ['Heading',
           'Enter your title',
           'Text Editor',
           'Text',
           'Publish']

def make_lang(lang):
    lang_map = dict.fromkeys(['elem-headerWidget-name',
                          'elem-headerWidget-placeholder',
                          'elem-textWidget-name',
                          'elem-inner-widget-btn-text',
                          'elem-publish-btn-text'])
    i = 0
    if lang == "Español":
        for key,_ in lang_map.items():
            lang_map[key] = lang_es[i]
            i+=1
    if lang == "English":
        for key,_ in lang_map.items():
            lang_map[key] = lang_en[i]
            i+=1
    return lang_map

def make_widget(c, page, lang_texts, timeout): # timeout 500 needed for first pass (avoids popup)
    for _,w in c.widgets.items():
        if repr(w) == 'HeaderWidget':
            # add new Header 
            page.get_by_role("button", name=lang_texts['elem-headerWidget-name']).click() 
            # place header text content in new Header
            page.get_by_placeholder(lang_texts['elem-headerWidget-placeholder']).fill(w.en.get())
            # go to elementor-widgets menu
            page.locator("id=elementor-panel-header-add-button").click()
        if repr(w) == 'TextWidget':
            # add new Text 
            page.get_by_role("button", name=lang_texts['elem-textWidget-name']).click()
            # place content text in new Text
            page.get_by_role("button", name=lang_texts['elem-inner-widget-btn-text'],exact=True).click()
            page.wait_for_timeout(timeout)
            page.get_by_role("textbox").fill(w.txtbox.get("1.0",'end'))
            page.keyboard.press("Insert") # necessary textbox confirm
            # go to elementor-widgets menu
            page.locator("id=elementor-panel-header-add-button").click()

def make_section(page, pink_container_count, s, lang_texts):
    iframe = page.frame_locator("id=elementor-preview-iframe")
    add_new_container_btn = iframe.get_by_title("Add New Container")
    add_new_container_btn.click()
    flexbox_btn = iframe.get_by_text("Flexbox")
    flexbox_btn.click()
    six_grid_option = iframe.locator(f'div[data-preset="{s.preset}"]')
    six_grid_option.click()
    if pink_container_count == 0:
        pink_container = iframe.locator(f".elementor-section-wrap > div:nth-child({pink_container_count+1})").first
        pink_container.click(position={'x':0,'y':0})
        for i,c in s.containers.items():
            gray_container = pink_container.locator(f".e-con-inner > div:nth-child({i+3})").first
            gray_container.hover()
            gray_container.click(position={'x':0,'y':0})
            # go to elementor-widgets menu
            page.locator("id=elementor-panel-header-add-button").click()
            make_widget(c,page,lang_texts,500)
    elif pink_container_count > 0:
        pink_container = iframe.locator(f".elementor-section-wrap > div:nth-child({pink_container_count+1})")
        pink_container.click(position={'x':0,'y':0})
        for i,c in s.containers.items():
            gray_container = pink_container.locator(f".e-con-inner > div:nth-child({i+3})")
            gray_container.hover()
            gray_container.click(position={'x':0,'y':0})
            # go to elementor-widgets menu
            page.locator("id=elementor-panel-header-add-button").click()
            make_widget(c,page,lang_texts,0)

def batch(batch_init,lang,controller):
        #check/pick language
        lang_texts = make_lang(lang)

        #start playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(batch_init['Host Url']+'/wp-admin')

                """User login"""
                # buscar entry login | # poner texto user
                page.locator("id=user_login").fill(batch_init['User'])
                # buscar entry password | # poner texto password
                page.locator("id=user_pass").fill(batch_init['Pass'])
                # buscar boton 'LOGIN' | # presionar boton 'LOGIN'
                page.locator("id=wp-submit").click()
                ###end user login###

                """Site settings"""
                # pagina nueva-pagina
                page.goto(batch_init['Host Url']+"/wp-admin/post-new.php?post_type=page")
                page.wait_for_timeout(2000)
                page.keyboard.press("Escape") #dismiss popup
                page.keyboard.press("Escape") #dismiss popup
                # seleccionar editar con elementor
                page.locator("id=elementor-switch-mode-button").click()
                page.wait_for_timeout(2000)
                page.keyboard.press("Escape") #dismiss popup
                page.reload(timeout=0) #dismiss popup
                page.keyboard.press('F5',delay=500) #dismiss popup
                page.keyboard.press('Control+R',delay=500) #dismiss popup

                #close navigator
                page.locator("id=elementor-navigator__close").click()
                pink_container_count = 0

                """Batch start"""
                for _,s in batch_init['Sections'].items(): 
                    make_section(page, pink_container_count, s, lang_texts)
                    # exit current 'section space'
                    page.locator("id=elementor-preview").click(position={"x":20,"y":20})
                    pink_container_count += 1
                ### end batch ###

                #save page
                page.get_by_role("button", name=lang_texts['elem-publish-btn-text']).click()
                page.wait_for_timeout(2500)
                browser.close()
                controller.success()
            except:
                controller.failed()

if __name__ == '__main__':
     ...
