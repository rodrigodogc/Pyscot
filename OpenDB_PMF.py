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

################################ SEARCH CONFIGURATION ##########################################
Name = 'Rodrigo Silva'
Email = 'rodrigodogc2010@hotmail.com'
Taxonomy = '. . . . Other Eukaryota'
Database = 'SwissProt'
Missed_cleavages = 1
Anottate_CSV_File = True #Criar ou não tabela de resultados
Console_mode = True      #Mostrar ou não o navegador trabalhando

Peaklist_Path = '/home/rodrigo/Documentos/Pyscot-ATT/peaklists'
Results_Path = '/home/rodrigo/Documentos/Pyscot-ATT/result'

Variable_xpath = '/html/body/font[1]/pre/b[8]' ### Em caso de erros alternar o último numero para [7] ou [8] ###

#Taxonomys
#. . . . Other Eukaryota
#. . . . . . Arabidopsis thaliana (thale cress)
#. . . . . . Oryza sativa (rice)
#. . . . . . Other green plants
#. . . . Viridiplantae (Green Plants)

Peptide_combinations = [['Da', '1.2'],
                        ['Da', '1.1'],
                        ['Da', '1.0'],
                        ['Da', '0.9'],
                        ['Da', '0.8'],
                        ['Da', '0.7'],
                        ['Da', '0.6'],
                        ['Da', '0.5'],
                        ['Da', '0.4'],
                        ['Da', '0.3'],
                        ['Da', '0.2'],
                        ['Da', '0.1'],
                        ['ppm', '200'],
                        ['ppm', '150'],
                        ['ppm', '100']]

##################################################################################################

Driver_path = './chromedriver'
optiones = Options()
if(Console_mode == True):
    optiones.add_argument('headless')

for _, _, Peaklists in os.walk(Peaklist_Path):
    print(Fore.MAGENTA + Style.BRIGHT + '%i Peaklists Loaded: %s ' % (len(Peaklists), str(Peaklists)))
driver = webdriver.Chrome(executable_path=Driver_path, options=optiones)

## Create CSV File
Taxonomy_clean = Taxonomy.replace('.', '').strip()
CSV_filename = '%s_%s_Infos.csv' %(Taxonomy_clean, Database)
if Anottate_CSV_File == True:
    print(Fore.RED + Style.BRIGHT +'Attention! Press [ENTER] will subscribe Table File, continue?')
    input()
    csv_file = open(CSV_filename, 'w')
    csv_file.write('Amostra;Taxonomia;Banco;PepTol;Mascot_ID_;Protein_Name;Score;Mass;pI;Uniprot_ID\n')
    csv_file.close()
## END
for peaklist in Peaklists:
    for pepComb in Peptide_combinations:
        driver.get('http://www.matrixscience.com/cgi/search_form.pl?FORMVER=2&SEARCH=PMF')
        print(Fore.YELLOW + "Completing Search Fields...")
        print(Fore.GREEN + Style.BRIGHT + 'Search Parameters:\n'
              + "................... Peaklist: " + str(peaklist) + '\n'
              + "................... Taxonomy: " + Taxonomy_clean  + '\n'
              + "................... Database: " + Database + '\n'
              + "................... PepTol  : " + pepComb[1] + " " + pepComb[0] + '\n'
              )

        data_Base_Select = Select(driver.find_element_by_name('DB'))

        user = driver.find_element_by_name('USERNAME')
        user.send_keys(Keys.CONTROL + 'a')
        user.send_keys(Name)
        mail = driver.find_element_by_name('USEREMAIL')
        mail.send_keys(Keys.CONTROL + 'a')
        mail.send_keys(Email)

        data_Base_Select.select_by_value(Database)
        data_Base_Select.deselect_by_value('contaminants')

        taxonomy_Select = Select(driver.find_element_by_name('TAXONOMY'))
        taxonomy_Select.select_by_value(Taxonomy)

        miss_Cleavages = Select(driver.find_element_by_name('PFA'))
        miss_Cleavages.select_by_value(str(Missed_cleavages))

        Mods_Select = Select(driver.find_element_by_name('MASTER_MODS'))
        Mods_Select.select_by_value('Carbamidomethyl (C)')
        driver.find_element_by_name('add_MODS').click()
        Mods_Select.select_by_value('Oxidation (M)')
        driver.find_element_by_name('add_IT_MODS').click()

        unity_Select = Select(driver.find_element_by_name('TOLU'))
        unity_Select.select_by_value(pepComb[0])

        driver.find_element_by_name('TOL').send_keys(Keys.CONTROL + 'a')
        driver.find_element_by_name('TOL').send_keys(pepComb[1])

        driver.find_element_by_id('InputSource-DATAFILE').send_keys(Peaklist_Path + '/' + str(peaklist))

        driver.find_element_by_id('Start_Search_Button').submit()
        print(Fore.CYAN + Style.DIM + 'Searching...')
        try:
            waiter = wdWait(driver, 320).until(
                url_contains('http://www.matrixscience.com/cgi/master_results.pl'))
            Result = driver.find_element_by_xpath('/html/body/font[1]/pre').text
            Protein_name = str(driver.find_element_by_xpath(Variable_xpath).text)[36:].split('OS=')[0].strip(',').strip()
            Mascot_ID = str(driver.find_element_by_xpath(Variable_xpath).text)[17:].split('for')[1].split(',')[0].strip()

        except:
            Result = 'Page not valid for this peaklist. Proceeding...'

        try:
            topScore = int(str(driver.find_element_by_xpath(Variable_xpath).text)[17:].split('for')[
                               0].strip())  # Catch Search Score
            SignificScore = int(str(driver.execute_script('return document.querySelector(\"body > br:nth-child(4)\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).nextSibling.nodeValue')).split('than')[1].split('are')[0].strip())  # Catch Signific Scr
            if topScore > SignificScore:
                Significance = 'SIGNIFICANT!'
                SignificancePrinter = Fore.GREEN + Style.BRIGHT + 'SIGNIFICANT!' #Bug fix :b

                driver.get(driver.find_element_by_xpath('/html/body/form[2]/table[1]/tbody/tr[1]/td[2]/tt/a').get_attribute("href"))
                Detail_mass = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr[4]/td').text ###
                Detail_pI = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr[5]/td').text ###

                driver.get('https://www.uniprot.org/uniprot/%s' %Mascot_ID)
                Uniprot_ID = str(driver.current_url).split('org/uniprot/')[1]

                ### CSV Writting
                if Anottate_CSV_File == True:
                    file = open(file=CSV_filename, mode='r')
                    content = file.readlines()
                    content.append('"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s"\n' % (
	                str(peaklist), Taxonomy_clean, Database, pepComb[1] + " " + pepComb[0], Mascot_ID, Protein_name, topScore,
	                Detail_mass, Detail_pI, Uniprot_ID))
                    file = open(file=CSV_filename, mode='w')
                    file.writelines(content)
                    file.close()
            else:
                Significance = 'Insignificant'
                SignificancePrinter = Fore.RED + Style.BRIGHT + 'Insignificant'
                Detail_mass = 'NonSignif'
                Detail_pI   = 'NonSignif'
                Uniprot_ID  = 'NonSignif'
        except:
                topScore = 'Not significative'
                SignificScore = None
                Significance = 'Invalid'
                SignificancePrinter = Fore.YELLOW + Style.BRIGHT + 'Invalid'
                Detail_mass = 'NonSignif'
                Detail_pI   = 'NonSignif'
                Uniprot_ID  = 'NonSignif'

        print('Top Score:', topScore, ' | ', 'Signific Score:', SignificScore, ' | ', 'Significance:', SignificancePrinter)

        try:
            Res_file = open(
                file='%s/%s__%s__%s_%s__PMF.txt' % (Results_Path, Significance, peaklist.replace('.xml', ''), str(pepComb[1]),
                                                                str(pepComb[0])), mode='w', encoding='utf-8')
            Res_file.write('%s\n' % Result)
            Res_file.write('Protein name    : %s\n' % Protein_name)
            Res_file.write('Isotopic mass   : %s\n' % Detail_mass)
            Res_file.write('Calculated pI   : %s\n' % Detail_pI)
            Res_file.write('Minimun Significative Score is :%s\n'
                           '%s Result' % (SignificScore, Significance))
        except:
            print('Fail writing result file!')

print(Back.BLUE + Fore.LIGHTGREEN_EX + 'All searchs done.')
input()

