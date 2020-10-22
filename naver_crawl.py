import sys, time, requests, os, path, glob, base64
from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import TimeoutException
from tqdm import trange
from PIL import Image

if __name__ == "__main__":
    keyword = sys.argv[1]
    save_root = r'C:\Users\Alchera\Desktop\crawl_img\20201012_glasses_crawl\naver\\' + keyword
    img_max = 100

    # 안경: 4,320,097
    # 선글라스: 4,823,249

    try:
        # 한페이지에 80개
        driver = webdriver.Chrome('chromedriver.exe')
        
        cnt = 0
        for x in trange(img_max):
            # if x <= 1543:
            #     cnt = 127161
            #     continue
            
            try:
                # https://search.shopping.naver.com/search/all?&query=안경pagingIndex=1&pagingSize=80&viewType=thumb
                url = r'http://browse.auction.co.kr/search?keyword=' + keyword + r'&p=' + str(x + 1)
                driver.get(url)
                time.sleep(.5)
            except:
                continue

            driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
            time.sleep(1)

            img_list = driver.find_elements_by_css_selector('#__next div div div div div div div ul li div a img')
            for y in img_list:
                src = y.get_attribute('src')
                img_data = requests.get(src).content
                img_save_path = os.path.join(save_root, str(cnt) + '.jpg')
                with open(img_save_path, 'wb') as handler:
                    handler.write(img_data)
                cnt += 1

    except Exception as e:
        print(e)
    finally:
        driver.quit()