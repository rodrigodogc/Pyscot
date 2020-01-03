import os
from colorama import Fore, Back, Style, init

init(autoreset=True) #Start colorama filter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait as wdWait
from selenium.webdriver.support.expected_conditions import url_contains
	
from PrintResult import printTxtResultMsMs

Taxonomy = 'All entries'
Database = 'Opuntia_ficus_indica'
Peaklist_Path = 'C:\\Users\\Rodrigo\\Desktop\\PeaklistsMara2019'

Driver_path = '.\\chromedriver.exe'
optiones = Options()
optiones.add_argument('headless')

Peptide_combinations = [['Da','1.2'],
                        ['Da','1.0'],
                        ['Da','0.8'],
                        ['Da','0.6'],
                        ['Da','0.4'],
                        ['Da','0.2'],
                        ['ppm','200'],
                        ['ppm','100']]

MsMs_combinations    = ['0.6',
                        '0.4',
                        '0.2']

for _, _, Peaklists in os.walk(Peaklist_Path):
    print(Fore.MAGENTA + Style.BRIGHT + '%i Peaklists Loaded: %s ' %(len(Peaklists),str(Peaklists)))
driver = webdriver.Chrome(executable_path=Driver_path, options=optiones)

nSignificResults = 0

for peaklist in Peaklists:
    for pepComb in Peptide_combinations:
        for combMsMs in MsMs_combinations:
            driver.get('https://proteomicsresource.washington.edu/mascot/cgi/search_form.pl?FORMVER=2&SEARCH=MIS')
            try:
                if driver.find_element_by_xpath('//*[@id="plainContent"]/table/tbody/tr/td/h2').is_displayed():
                    print('Logging in DB')
                    driver.find_element_by_id('username').send_keys('terciliojr')
                    driver.find_element_by_name('password').send_keys('tercilio2018')
                    driver.find_element_by_name('submit').submit()
            except:
                print(Fore.GREEN + 'Already authenticated.')
            print("Completing Search Fields...")
            print(Fore.GREEN + Style.BRIGHT +'Search Parameters:\n'
                  + "................... Peaklist: " + str(peaklist) + '\n'
                  + "................... Taxonomy: " + Taxonomy.replace('.', '') + '\n'
                  + "................... Database: " + Database + '\n'
                  + "................... PepTol  : " + pepComb[1] + " " + pepComb[0] + '\n'
                  + "................... MsMsTol : " + combMsMs
                  )


            data_Base_Select = Select(driver.find_element_by_name('DB'))
            data_Base_Select.select_by_visible_text('Gossypium_hirsutum (AA)')
            driver.find_element_by_name("remove_DBs").click()

            taxonomy_DB_Select = Select(driver.find_element_by_name('MASTER_DB'))
            taxonomy_DB_Select.select_by_value(Database)
            driver.find_element_by_name('add_DBs').click()

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

            driver.find_element_by_id('InputSource-DATAFILE').send_keys(Peaklist_Path + '\\' + str(peaklist))

            data_Format_Select = Select(driver.find_element_by_name('FORMAT'))
            data_Format_Select.select_by_visible_text('Bruker (.XML)')

            instrument_Select = Select(driver.find_element_by_name('INSTRUMENT'))
            instrument_Select.select_by_visible_text('MALDI-TOF-TOF')

            precursor_Mass = str(peaklist).strip('.xml').split('msms')[1]
            driver.find_element_by_name('PRECURSOR').send_keys(precursor_Mass)

            driver.find_element_by_xpath('//*[@id=\"plainContent\"]/form/table/tbody/tr[18]/td[2]/b/input').submit()


            try:
                waiter = wdWait(driver, 5).until(url_contains('https://proteomicsresource.washington.edu/mascot/cgi/master_results.pl'))
                Result = driver.find_element_by_xpath('/html/body/font[1]/pre').text
            except:
                Result = 'Page not valid for this peaklist. Proceeding...'

            try:
                topScore = int(str(driver.find_element_by_xpath('/html/body/font[1]/pre/b[7]').text)[17:].split('for')[0].strip()) #Catch Search Score
                SignificScore = int(str(driver.execute_script('return document.querySelector(\"body > '
                                                          'br:nth-child(4)\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, '
                                                          'null).nextSibling.nodeValue')).split('than')[1].split('are')[0].strip()) #Catch Signific Scr
                if topScore > SignificScore:
                    Significance = '!_SIGNIFICANT_!'
                    nSignificResults += 1
                else:
                    Significance = 'Insignificant'
            except:
                topScore = str('Not significative')
                SignificScore = None
                Significance = 'Invalid'

            printTxtResultMsMs(peaklist, pepComb, combMsMs, Significance, SignificScore, Result)
            print('Top Score:', topScore, ' | ', 'Signific Score:', SignificScore, ' | ', 'Significance:', Fore.RED + Significance)
			
print(Back.RED + Fore.LIGHTGREEN_EX + Style.DIM + 'Search is done with %i signific scores founded.' %nSignificResults)
input()
#driver.close()


