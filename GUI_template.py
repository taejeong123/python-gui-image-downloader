import sys, os, path, glob, time, requests

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
        if self.btnFlag:
            return

        self.btnFlag = True
        self.print_values()

        if self.txt_root.strip() == "":
            QMessageBox.warning(self, "Warning", "Empty Content!")
            self.btnFlag = False
            return
        keyword_list = self.read_txt_file(self.txt_root)

        driver = self.connect_driver()

        total_image_cnt = self.cnt_total.value()

        try:
            for x in range(len(keyword_list)):
                keyword = keyword_list[x]

                cnt = 0
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
                        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
                        time.sleep(1)

                    img_list = driver.find_elements_by_css_selector(self.img_selector.text())
                    for y in img_list:
                        print(y)
                        # src = y.get_attribute('src')
                        # img_data = requests.get(src).content
                        # img_save_path = os.path.join(save_root, str(cnt) + '.jpg')
                        # with open(img_save_path, 'wb') as handler:
                        #     handler.write(img_data)
                        # cnt += 1

                    print(cnt)
                    if cnt >= total_image_cnt:
                        break
        except Exception as e:
            print(e)
        finally:
            driver.quit()

        # self.site_url.text()
        # self.img_selector.text()
        # self.qs_keyword.text()
        # self.qs_page.text()
        # str(self.cnt_total.value())
        # str(self.check_scroll.isChecked())
        # str(self.check_decode.isChecked())
        # str(self.check_headless.isChecked())
        # str(self.check_gpu.isChecked())

    def connect_driver(self):
        try:
            options = webdriver.ChromeOptions()
            if self.check_headless.isChecked():
                options.add_argument('--headless')
            if self.check_gpu.isChecked():
                options.add_argument('--disable-gpu')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome('chromedriver1.exe', options=options)
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
        print('check_scroll:' + str(self.check_scroll.isChecked()))
        print('check_decode:' + str(self.check_decode.isChecked()))
        print('check_headless:' + str(self.check_headless.isChecked()))
        print('check_gpu:' + str(self.check_gpu.isChecked()))
        print('===============================================')
    
if __name__ == "__main__":
    app = QApplication(sys.argv)

    qss_file = open('dark.qss').read()
    app.setStyleSheet(qss_file)

    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

    # 대단해 태정쿤,,