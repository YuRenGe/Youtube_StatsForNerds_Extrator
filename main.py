import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver import ActionChains


# find stats for nerd and open it, this part is using sharat910/selenium-youtube work
def enable_stats():
    movie_player = driver.find_element_by_id('movie_player')
    hover = ActionChains(driver).move_to_element(movie_player)
    hover.perform()
    ActionChains(driver).context_click(movie_player).perform()
    options = driver.find_elements_by_class_name('ytp-menuitem')
    for option in options:
        option_child = option.find_element_by_class_name('ytp-menuitem-label')
        if option_child.text == 'Stats for nerds' or option_child.text == '详细统计信息':
            option_child.click()
            print("Enabled stats for Nerds plugin.")
            return True
    return False


# using regex to extract stats information from stats text
def data_collection(_df, _context, _video_time):
    video_id = re.search(r"^Video ID / (.*) /", _context).group(1)
    viewport = re.search(r"Viewport / Frames (.*) /", _context).group(1)
    current_res = re.search(r"Current / Optimal Res (.*) / (.*)", _context).group(1)
    optimal_res = re.search(r"Current / Optimal Res (.*) / (.*)", _context).group(2)
    connection_speed = re.search(r"Connection Speed (.*) ", _context).group(1)
    buffer_health = re.search(r"Buffer Health (.*) ", _context).group(1)
    date = re.search(r"Date (.*) GMT", _context).group(1)
    data_list = [video_id, viewport, current_res, optimal_res, connection_speed, buffer_health, date, _video_time]
    return data_list


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=EYKHNk_4Iic'
    driver = webdriver.Chrome('./third-part/chromedriver.exe')
    driver.get(url)
    time.sleep(3)
    driver.find_element_by_css_selector('.ytp-large-play-button.ytp-button').click()
    time.sleep(3)
    movie_player = driver.find_element_by_id('movie_player')
    # open stats for nerd plugin
    ret = enable_stats()
    if not ret:
        print("Qurey Stats for Nerds Failed, Close Programme.")
        driver.close()
    # statistics info collections
    total_collection_time = 2000
    time_interval = 2
    print("Creating data frame.\r\n")
    df = pd.DataFrame(
        columns=["video id", "viewport", "current res", "optimal res", "connection speed", "buffer health", "date_time", "video_time"])
    print("Start collecting data.\r\n")
    video_time = 0
    for i in range(0, total_collection_time, time_interval):
        print("Current Process:", i / total_collection_time)
        video_time += time_interval
        stats_infos = driver.find_element_by_css_selector('div.html5-video-info-panel-content.ytp-sfn-content')
        context = stats_infos.text
        data_list = data_collection(df, context, video_time)
        df.loc[len(df)] = data_list
        print(df.values)
        time.sleep(2)
    print("Data collection is complete.\r\n")
    df.to_csv("./datasets/youtubedata.csv")
