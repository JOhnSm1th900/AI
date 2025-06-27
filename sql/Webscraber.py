from selenium import webdriver
from selenium.webdriver.common.by import By


def get_video_links(driver):
    thumbnails = driver.find_elements(By.ID, 'thumbnail')
    links = set(item.get_attribute('href')
                for item in thumbnails if item.get_attribute('href'))
    return list(links)


def get_video_titles(driver):
    videos = driver.find_elements(By.ID, 'video-title')
    return [item.text for item in videos]


def get_video_views(driver):
    views = driver.find_elements(
        By.CSS_SELECTOR, '#metadata-line > span:nth-child(3)')
    return [item.text for item in views]


def get_video_release_dates(driver):
    dates = driver.find_elements(
        By.CSS_SELECTOR, '#metadata-line > span:nth-child(4)')
    return [item.text for item in dates]


def get_youtube_channel_data():
    channel = input("Enter the channel username you are looking for: ")
    URL = f'https://www.youtube.com/@{channel}/videos'

    with webdriver.Chrome() as driver:
        driver.get(URL)

        try:
            driver.find_element(By.CSS_SELECTOR, '#primary')
        except:
            driver.close()
            print('\nThe page is not found, enter a valid channel.\n')
            return

        video_links = get_video_links(driver)
        video_titles = get_video_titles(driver)
        video_views = get_video_views(driver)
        video_release_dates = get_video_release_dates(driver)

        videos_data = [
            [video_titles[i], video_links[i], video_views[i], video_release_dates[i]]
            for i in range(len(video_links))
        ]

        for video in videos_data:
            print(video)


def main():
    to_continue = True
    while to_continue:
        get_youtube_channel_data()
        if input("Would you like to continue?\n").strip().upper() == 'NO':
            to_continue = False


if __name__ == "__main__":
    main()


