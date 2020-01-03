import os, sys
try:
    from colorama import Fore, Back, Style, init
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.wait import WebDriverWait as wdWait
    from selenium.webdriver.support.expected_conditions import url_contains
    init(autoreset=True)  # Start colorama filter
except ImportError:
    print('Installing requeriments: Selenium, Colorama')
    os.system('python -m pip install selenium colorama')
    input('Please restart the script...'); sys.exit(0)

Name = 'Rodrigo Silva'
Email = 'rodrigodogc2010@hotmail.com'
Taxonomy = '. . . . Viridiplantae (Green Plants)'
Database = 'SwissProt'

Peaklist_Path = 'C:/Users/Rodrigo-PCG/Desktop/Peaks'
Results_Path = 'C:/Users/Rodrigo-PCG/Desktop/teste'

Driver_path = './chromedriver.exe'
optiones = Options()
optiones.add_argument('headless')

Peptide_combinations = [['Da', '1.2'],
                        ['Da', '1.1']]
                        #['Da', '1.0'],
                        #['Da', '0.8'],
                        #['Da', '0.7'],
                        #['Da', '0.6'],
                        #['Da', '0.5'],
                        #['Da', '0.4'],
                        #['Da', '0.3'],
                        #['Da', '0.2'],
                        #['Da', '0.1'],
                        #['ppm', '200'],
                        #['ppm', '150'],
                        #['ppm', '100'],
                        #['ppm', '50']]

MsMs_combinations = ['0.6',
                     '0.4',
                     '0.2']

for _, _, Peaklists in os.walk(Peaklist_Path):
    print(Fore.MAGENTA + Style.BRIGHT + '%i Peaklists Loaded: %s ' % (len(Peaklists), str(Peaklists)))
driver = webdriver.Chrome(executable_path=Driver_path, options=optiones)

n_Signific_Results = 0 #Significative results counter.

for peaklist in Peaklists:
    for pepComb in Peptide_combinations:
        for combMsMs in MsMs_combinations:
            driver.get('http://www.matrixscience.com/cgi/search_form.pl?FORMVER=2&SEARCH=MIS')
            print(Fore.YELLOW + "Completing Search Fields...")
            print(Fore.GREEN + Style.BRIGHT + 'Search Parameters:\n'
                  + "................... Peaklist: " + str(peaklist) + '\n'
                  + "................... Taxonomy: " + Taxonomy.replace('.', '') + '\n'
                  + "................... Database: " + Database + '\n'
                  + "................... PepTol  : " + pepComb[1] + " " + pepComb[0] + '\n'
                  + "................... MsMsTol : " + combMsMs
                  )

            user = driver.find_element_by_name('USERNAME')
            user.send_keys(Keys.CONTROL + 'a')
            user.send_keys(Name)
            mail = driver.find_element_by_name('USEREMAIL')
            mail.send_keys(Keys.CONTROL + 'a')
            mail.send_keys(Email)

            data_Base_Select = Select(driver.find_element_by_name('DB'))
            data_Base_Select.select_by_visible_text('contaminants (AA)')
            driver.find_element_by_name("remove_DBs").click()

            taxonomy_DB_Select = Select(driver.find_element_by_name('MASTER_DB'))
            taxonomy_DB_Select.select_by_value(Database)
            driver.find_element_by_name('add_DBs').click()

            taxonomy_Select = Select(driver.find_element_by_name('TAXONOMY'))
            taxonomy_Select.select_by_value(Taxonomy)

            Mods_Select = Select(driver.find_element_by_name('MASTER_MODS'))
            Mods_Select.select_by_value('Carbamidomethyl (C)')
            driver.find_element_by_name('add_MODS').click()
            Mods_Select.select_by_value('Oxidation (M)');
            driver.find_element_by_name('add_IT_MODS').click()

            unity_Select = Select(driver.find_element_by_name('TOLU'))
            unity_Select.select_by_value(pepComb[0])

            driver.find_element_by_name('TOL').send_keys(Keys.CONTROL + 'a')
            driver.find_element_by_name('TOL').send_keys(pepComb[1])

            driver.find_element_by_name('ITOL').send_keys(Keys.CONTROL + 'a')
            driver.find_element_by_name('ITOL').send_keys(combMsMs)

            pepChargeSelect = Select(driver.find_element_by_name('CHARGE'))
            pepChargeSelect.select_by_visible_text('1+')

            driver.find_element_by_id('InputSource-DATAFILE').send_keys(Peaklist_Path + '/' + str(peaklist))

            data_Format_Select = Select(driver.find_element_by_name('FORMAT'))
            data_Format_Select.select_by_visible_text('Bruker (.XML)')

            instrument_Select = Select(driver.find_element_by_name('INSTRUMENT'))
            instrument_Select.select_by_visible_text('MALDI-TOF-TOF')

            precursor_Mass = str(peaklist).strip('.xml').split('msms')[1]
            driver.find_element_by_name('PRECURSOR').send_keys(precursor_Mass)

            driver.find_element_by_id('Start_Search_Button').submit()

            ###Scraping...

            try:
                waiter = wdWait(driver, 50).until(
                    url_contains('http://www.matrixscience.com/cgi/master_results.pl'))
                Result = driver.find_element_by_xpath('/html/body/font[1]/pre').text
            except:
                Result = 'Page not valid for this peaklist. Proceeding...'

            try:
                topScore = int(str(driver.find_element_by_xpath('/html/body/font[1]/pre/b[8]').text)[17:].split('for')[
                                   0].strip())  # Catch Search Score
                SignificScore = int(str(driver.execute_script('return document.querySelector(\"body > '
                                                              'br:nth-child(4)\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, '
                                                              'null).nextSibling.nodeValue')).split('than')[1].split('are')[0].strip())  # Catch Signific Scr

                if topScore > SignificScore:
                    Significance = '!_SIGNIFICANT_!'

                    n_Signific_Results += 1
                else:
                    Significance = 'Insignificant'
            except:
                topScore = str('Not significative')
                SignificScore = None
                Significance = 'Invalid'

            print('Top Score:', topScore, ' | ', 'Signific Score:', str(SignificScore), ' | ', 'Significance:', Fore.RED + Significance)
            try:
                Res_file = open(
                    file='%s/%s__%s__%s_%s__MsMsTol__%s_Da.txt' % (Results_Path, Significance, peaklist, str(pepComb[1]),
                                                                    str(pepComb[0]), combMsMs), mode='w', encoding='utf-8')
                Res_file.write('%s\n' % Result)
                Res_file.write('Minimun Significative Score is :%s\n'
                               '%s Result' % (SignificScore, Significance))
            except:
                print('Fail writing result file!')

print(Back.BLUE + Fore.LIGHTGREEN_EX + 'Search is done with %i signific scores founded.' %n_Signific_Results)

input()



