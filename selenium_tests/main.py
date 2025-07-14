from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
Proof of concept that selenium can perform user tests on
wordlistTool.v8_2_7.html (and other versions with same html layout);
It can change tabs and enter data and read the feedback
"""

def main():
    driver = webdriver.Chrome()
    driver.get(
        # "file:///Users/paulwakelin/coding/javascript/geptChecker/wordlistTool.v8_2_7.html"
        "file:///Users/paulwakelin/coding/python/selenium_tests/wordlistTool.v8_2_7.html"
    )
    title = driver.title
    print(f"title: {title}")

    driver.implicitly_wait(100)

    text_box = driver.find_element(by=By.ID, value="t1_term_i")
    # submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

    text_box.send_keys("bear")
    # results = driver.find_element(by=By.ID, value="t1_results_text")
    results_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='t1_results_text']/table"))
    )
    text = results_table.text
    print(f"msg: {text}")

    result_count = driver.find_elements(By.XPATH, "//*[@id='t1_results_text']/table/tbody/tr")
    print(f"Number of results returned = {len(result_count) - 1}")

    driver.find_element(by=By.XPATH, value="//*[@for='t1_match_x']").click()
    result_count = driver.find_elements(By.XPATH, "//*[@id='t1_results_text']/table/tbody/tr")
    print(f"Number of results returned = {len(result_count) - 1}")

    print("Change to Text Tab...")
    tab_2 = driver.find_element(by=By.ID, value="t1_tab_tag")
    tab_2.click()
    input_div = driver.find_element(by=By.ID, value="t2_raw_text")
    input_div.send_keys("color colour coloring 11 colouring colored coloured colorish")
    tab_2.click()
    level_details_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='level-details-list']"))
    )
    # input_div = driver.find_element(by=By.ID, value="t2_raw_text")
    driver.find_element(by=By.ID, value="t2_raw_text")
    print(level_details_list.text)
    word_count = driver.find_elements(By.XPATH, "//*[@id='t2_raw_text']/span")
    print(f"Number of words returned = {len(word_count)}")


    driver.quit()

if __name__ == "__main__":
    main()
