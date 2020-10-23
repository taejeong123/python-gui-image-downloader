import sys
import os
import path
import glob
import time
import requests
import base64

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import uic

from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import TimeoutException

ui_file = uic.loadUiType("ui_design.ui")[0]

class WindowClass(QMainWindow, ui_file):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Image Downloader')

        self.txt_root = ''
        self.save_dest = ''
        self.btnFlag = False
        self.img_cnt = 0

        self.btn_browse_1.clicked.connect(self.get_txt_file)
        self.btn_browse_2.clicked.connect(self.get_save_folder)
        self.btn_start.clicked.connect(self.StartCrawling)

    def get_txt_file(self):
        filename = QFileDialog.getOpenFileName(self, "Select File")[0]
        self.txt_root = filename
        self.txt_file.setText(filename)

    def get_save_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.save_dest = foldername
        self.save_folder.setText(foldername)
        
    def StartCrawling(self):
        if self.btnFlag: return

        self.btnFlag = True
        self.print_values()

        if self.txt_root.strip() == "":
            QMessageBox.warning(self, "Warning", "Empty Content!")
            self.btnFlag = False
            return

        keyword_list = self.read_txt_file(self.txt_root)
        driver = self.connect_driver()

        try:
            for x in range(len(keyword_list)):
                keyword = keyword_list[x]

                cnt = 0
                self.img_cnt = 0
                while True:
                    cnt += 1

                    # TODO: url-ex) http://browse.auction.co.kr/search
                    # TODO: tag-ex) #section--inner_content_body_container div div div div div a img
                    # TODO: query-string-ex) keyword, p
                    url = self.site_url.text() + '?' + self.qs_keyword.text() + '=' + keyword + '&' + self.qs_page.text() + '=' + str(cnt)
                    try:
                        driver.get(url)
                        time.sleep(.5)
                    except:
                        continue

                    if self.check_scroll.isChecked():
                        self.scroll(driver)

                    img_list = driver.find_elements_by_css_selector(self.img_selector.text())
                    for y in img_list:
                        self.img_cnt += 1

                        src = y.get_attribute('src')

                        if 'smiledelivery.png' in src: continue

                        save_dir = os.path.join(self.save_dest, keyword)
                        os.makedirs(save_dir, exist_ok=True)
                        save_file_name = os.path.join(save_dir, str(self.img_cnt) + '.jpg')

                        if 'data:image/' in src:
                            if self.check_decode.isChecked():
                                self.download_base64(src, save_file_name)
                            else:
                                continue
                        
                        self.download_image(src, save_file_name)

                    if self.img_cnt >= self.cnt_total.value(): break
        except Exception as e:
            print(e)
        finally:
            driver.quit()

    # def set_progress(self):
    #     my_dialog = QDialog(self)
    #     # self.progress = QProgressBar(self)
    #     # self.progress.setGeometry(0, 0, 300, 25)
    #     # self.progress.setMaximum(100)
    #     my_dialog.exec_()
    #     current_img_percent = self.img_cnt / self.cnt_total.value() * 100
    #     self.progressBar.setValue(current_img_percent)

    def download_base64(self, src, save_file_name):
        base64_image_data = src.split(',')[1]
        base64_image_data = base64_image_data + '=' * (4 - len(base64_image_data) % 4)
        with open(save_file_name, 'wb') as f:
            f.write(base64.b64decode(base64_image_data))

    def download_image(self, src, save_file_name):
        img_data = requests.get(src).content
        with open(save_file_name, 'wb') as handler:
            handler.write(img_data)

    def scroll(self, driver):
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        time.sleep(1)

    def connect_driver(self):
        try:
            options = webdriver.ChromeOptions()
            if self.check_headless.isChecked():
                options.add_argument('--headless')
            if self.check_gpu.isChecked():
                options.add_argument('--disable-gpu')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome('chromedriver.exe', options=options)
        except:
            print('[ERROR]: Chromedriver Error')
            quit()
        return driver

    def read_txt_file(self, txt_root):
        f = open(txt_root, mode='rt', encoding='utf-8-sig')
        lines = f.readlines()
        result_list = []
        for line in lines:
            result_list.append(line.replace('\n', '').strip())
        f.close()
        return result_list

    def print_values(self):
        print('================ Start_Crawling ================')
        print('txt_root: ' + self.txt_root)
        print('save_folder: ' + self.save_dest)
        print('crawling_url: ' + self.site_url.text())
        print('image_selector: ' + self.img_selector.text())
        print('qs_keyword: ' + self.qs_keyword.text())
        print('qs_page: ' + self.qs_page.text())
        print('cnt_total: ' + str(self.cnt_total.value()))
        print('check_scroll: ' + str(self.check_scroll.isChecked()))
        print('check_decode: ' + str(self.check_decode.isChecked()))
        print('check_headless: ' + str(self.check_headless.isChecked()))
        print('check_gpu: ' + str(self.check_gpu.isChecked()))
        print('===============================================')
    
if __name__ == "__main__":
    app = QApplication(sys.argv)

    qss_file = open('dark.qss').read()
    app.setStyleSheet(qss_file)

    myWindow = WindowClass()
    myWindow.show()
    app.exec_()