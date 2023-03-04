import pytest
from selenium import webdriver #подключение библиотеки
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import valid_email, valid_password


@pytest.fixture(autouse=True)
def testing():
    pytest.driver = webdriver.Chrome('./chromedriver.exe')
# настраиваем неявные ожидания
    pytest.driver.implicitly_wait(10)
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')

    yield

    pytest.driver.quit()


def list_of_pets_data(strt, elements):
    """ данная процедура формирует из полного списока всех характеристик
    питомцев список с требуемыми данными( имя, тип, возраст и т.д)
    :param elements: полученный полный список характеристик питомцев
           strt: с какого елемента начинаем отсчёт (какие данные нужны)
    :return: список с требуемыми данными
    """
    field_nbr = 4 # число полей в карточке питомца включая кнопку "удалить питомца"
    element_data = elements[strt::field_nbr]
    pets_data = []
    for i in element_data:
        pets_data.append(i.text)
# сразу проверяем на отсутствие в карточке пустого поля
        assert i.text != "", 'В карточке питомца имеется путсое поле'
    return pets_data

def test_page_my_pets():
    """ This test checks if everything is OK with page "my_pets" """
# Входим в аккаунт
    pytest.driver.find_element(By.ID, 'email').send_keys(valid_email)
    pytest.driver.find_element(By.ID, 'pass').send_keys(valid_password)
# явные ожидания, ждём появления кнопки и только потом давим
    WebDriverWait(pytest.driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        'button[type="submit"]'))).click()
# переходим на страницу с моими питомцами, используем явные ожидания
    WebDriverWait(pytest.driver, 5).until(
        EC.presence_of_element_located((By.LINK_TEXT,
                                        u"Мои питомцы"))).click()
# Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element(By.CSS_SELECTOR,
                                      '.navbar-brand.header2').text == "PetFriends"
# считываем число питомцев из поля "Питомцев: "
    my_pets = pytest.driver.find_element(By.CSS_SELECTOR,
                                         'div[class=".col-sm-4 left"]')
    number_my_pets = int(my_pets.text.split ('\n')[1].split(':')[1])
# just for check myself, can be removed if future
    print('\n Моих питомцев: ', number_my_pets)

# составляем полный список данных моих питомцев
    elements = pytest.driver.find_elements(By.XPATH, '//tbody/tr/td')

# формируем список имён моих питомцев
    pet_names = list_of_pets_data(0, elements)
# формируем список типов моих питомцев
    pet_breeds = list_of_pets_data(1, elements)
# формируем список возрастов моих питомцев
    pet_age = list_of_pets_data(2, elements)

# проверяем что присутствуют все питомцы сравнивая число питомцев
# с количеством имён
    assert number_my_pets == len(pet_names), \
        'Несоответствие числа карточек и питомцев'

# Хотя бы у половины питомцев есть фото
    pet_images = pytest.driver.find_elements(By.CSS_SELECTOR, 'th img')
    pets_with_image = 0
    for i in range(number_my_pets):
        if pet_images[i].get_attribute('src') != "":
            pets_with_image += 1
    assert pets_with_image >= number_my_pets/2, \
        "Чилсло питомцев без фото меньше половины!"

# В списке нет повторяющихся питомцев
    for pet1 in range(number_my_pets-1):
        pet2 = pet1+1
        while pet2 < number_my_pets:
            assert pet_names[pet1] != pet_names[pet2] or \
                   pet_breeds[pet1] != pet_breeds[pet2] or \
                   pet_age[pet1] != pet_age[pet2] , "Есть одинаковые питомцы"
            pet2 += 1

# проверяем что у всех питомцев разные имена
    assert len(pet_names) == len(set(pet_names)), 'Имена питомцев повторяются!'

    #just for check my code
    print(pet_names, '\n', pet_breeds, '\n', pet_age)


