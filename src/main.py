import time, threading
import inventory, arena, utility, settings, work, expedition, player, quest

from selenium import webdriver
from seleniumrequests import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup

"""
Main
"""
def plan_manager():
    """
    Defines the plan to play the game
    """
    print("I'm the plan manager!")

    arenaManager      = arena.ArenaManager(driver, secureHash)
    playerManager     = player.PlayerManager(driver, secureHash)
    inventoryManager  = inventory.InventoryManager(driver, secureHash)
    questManager      = quest.QuestManager(driver, secureHash)
    workManager       = work.WorkManager(driver, secureHash)
    expeditionManager = expedition.ExpeditionManager(driver, secureHash)

    # questsProcess = multiprocessing.Process(target = questManager.loop_quests, args = (False,)) # skip_timed_quests = False
    questsProcess = threading.Thread(target = questManager.loop_quests, args = (False,)) # skip_timed_quests = False
    questsProcess.daemon = True # This process should die along with the main one
    questsProcess.start()

    while True:
        print("********** Starting new cycle **********")

        ### Manage HP
        hp_percent = playerManager.get_hp_percentage()
        print(f"I have {hp_percent}% HP left")
        if hp_percent <= 50:
            print("I'm weak, i should eat something")
            if not inventoryManager.eat_food():
                print("Couldn't eat, getting some food")
                inventoryManager.collect_food()
                print("Trying to eat again")
                inventoryManager.eat_food()

        ### Spend action points
        arenaManager.go_arena_provinciarum(max_fight_level = 47)
        arenaManager.go_circus_provinciarum(max_fight_level = 47)

        expeditionManager.go_expedition(location = 0, stage = 3)
        expeditionManager.go_dungeon_cave_temple(difficulty = 'Normal', skip_boss = True)

        ### Go to work
        time_working = 3 * 60 # workManager.go_work()
        if time_working != -1:
            print(f"Sleeping for {time_working} seconds...")
            time.sleep(time_working)
            print("Finished working!")

with Firefox() as driver:
    settings.login_data['index_url'] = f"https://s{settings.login_data['server_number']}-{settings.login_data['server_country']}.gladiatus.gameforge.com/game/index.php"
    settings.login_data['ajax_url'] = f"https://s{settings.login_data['server_number']}-{settings.login_data['server_country']}.gladiatus.gameforge.com/game/ajax.php"

    print("Logging in into Gladiatus")
    """
    # Block image loading on Firefox
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    driver = Firefox(firefox_profile=firefox_profile)
    """

    driver.get(settings.login_data['login_url'])
    driver.find_element_by_id("loginRegisterTabs").find_element_by_css_selector('ul:nth-child(1)').find_element_by_css_selector('li:nth-child(1)').click()
    driver.find_element_by_xpath('//input[@name="email"]').send_keys(settings.login_data['user_email'])
    driver.find_element_by_xpath('//input[@name="password"]').send_keys(settings.login_data['user_password'])
    driver.find_element_by_xpath('//button[@type="submit"]').click()

    play_button = WebDriverWait(driver, 15).until(lambda x: x.find_element_by_xpath('//span[@class="serverDetails"]'))
    play_button.click()
    driver.switch_to.window(driver.window_handles[1])

    time.sleep(12) # TODO: fix into an elegant solution, gotta wait for 'secureHash' in JS to be defined
    secureHash = utility.get_hash(driver.page_source)

    print(f"Logged in, our secure hash is {secureHash}")
    plan_manager()