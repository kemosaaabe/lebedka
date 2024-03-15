import requests
import random
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

# session = requests.Session()
api_link = "http://localhost:90/online_store/backend" # 5432 - default PostgreSQL port

# [POST] /online_store/backend/use
def create_user(username: str):
    """ Создаёт пользователя """
    r = requests.post(url=f'{api_link}/user', json={'name': username})

    return r


# [DELETE] /online_store/backend/user/:id
def delete_user(user_id: int):
    """ Удаляет пользователя """
    r = requests.delete(url=f'{api_link}/user/{user_id}')

    return r


# [GET] /online_store/backend/user
def get_all_users():
    """ Возвращает всех пользователей """
    r = requests.get(url=f'{api_link}/user')

    return r


# [POST] /online_store/backend/orders/:id
def create_order(user_id: int):
    """ Создаёт заказ. Данные о корзине берутся из Redis """
    r = requests.post(url=f'{api_link}/orders/{user_id}')

    return r


# [GET] /online_store/backend/orders/:id
def get_order(user_id: int):
    """ Возвращает все заказы юзера """
    r = requests.get(url=f'{api_link}/orders/{user_id}') 

    return r


# [DELETE] /online_store/backend/orders/:id
def delete_order(order_id: int):
    """ Удаляет заказ клиента """
    r = requests.delete(url=f'{api_link}/orders/{order_id}')

    return r


# [POST] /online_store/backend/products
def add_product(name: str, price: int):
    r = requests.post(url=f'{api_link}/products', json={'name': name, 'price': price})

    return r


# [GET] /online_store/backend/products
def get_all_products():
    r = requests.get(url=f'{api_link}/products')

    return r


# [DELETE] /online_store/backend/products/:id
def delete_product(product_id: int):
    r = requests.delete(url=f'{api_link}/products/{product_id}')

    return r


# [POST] /online_store/backend/cart
def create_user_cart(user_id: int, products_id: list[int]):
    """ Создаёт корзину клиента """

    r = requests.post(url=f'{api_link}/cart', json={'user_id': user_id, 'products_id': products_id})

    return r


# [GET] /online_store/backend/cart/:id
def get_user_cart(user_id: int):
    """ Возврщает текущую корзину с товарами клиента """
    r = requests.get(url=f'{api_link}/cart/{user_id}')

    return r


# [DELETE] /online_store/backend/cart/:id
def delete_user_cart(user_id: int):
    """ Удаляет текушую корзину клиента """
    r = requests.delete(url=f'{api_link}/cart/{user_id}')

    return r


def create_users_for_db():
    """ 
        Создаём пользователей 
        
        Возвращает:
        users: list[str] - список имён пользователей 
        users_dict: dict(int: str) - словарь соответствия id пользователя и его имени
    """

    # Создаём пользователей
    users = ['Бадма', 'Саша', 'Егор', 'Витя', 'Аня', 'Карина', 'Рустам', 'Стас']
    users_dict = {}

    for user in users:
        r = create_user(user)
        if r.status_code == 200:
            print(f'User {user} created. Returned: {r}')
            users_dict[r.json().get('data').get('id')] = user
        else:
            print(f'User {user} was NOT created. Returned: {r}')

    return users, users_dict


def create_products_for_db():
    """ 
        Создаём продукты 
        
        Возвращает:
        products: list[str] - список названий продуктов 
        products_dict: dict(int: str) - словарь соответствия id продукта и его названия
    """

    products = ['Флаг радужный', 'Символика нац.', 'Страпон детский', 'Шарики анальные', 'Кляп мужской', 'Костюм госпожи', 'Тапочки для танцевальной дискотеки']
    products_dict = {}

    for product in products:
        r = add_product(name=product, price=random.randint(1, 999))
        if r.status_code == 200:
            print(f'Product {product} was created. Returned: {r}')
            products_dict[r.json().get('data').get('id')] = product
        else:
            print(f'Product {product} was NOT created. Returned: {r}')

    return products, products_dict


def create_carts_for_db(users_dict: dict, products: list, products_dict:dict):
    """ 
        Создаём корзины для пользователей
        Берём случайно число продуктов и случайные продукты для каждого пользователя
    """
    responses_time = []
    # Создаём корзины
    for user in users_dict.keys():
        # Создаём список продуктов в корзине
        user_products_list = []

        # Берём случайное число товаров в коризне
        for _ in range(random.randint(1, len(products))):
            # Берём случайный id продукта из нашего словарика продуктов
            user_products_list.append(random.choice(list(products_dict.keys())))

        r = create_user_cart(user, products_id=user_products_list)
        responses_time.append(r.elapsed.total_seconds())
    
    return responses_time


def user_actions_imitation(users: list, products: list, users_dict: dict, products_dict: dict):
    """ 
        Имитируем действия пользователей. Удаляем корзины и создаём заново

        Возвращает:
        deleted_users_carts: list[int] - список пользователей, у которых мы удаляли корзины, чтобы при создании заказов они создавались только у тех,
                                         у кого корзина есть
      
    """
    # Имитируем поведение. Удаляем корзины и создаём заново
    deleting_user_time = []
    create_user_time = []
    deleted_users_carts = []
  
    # Имитируем действия большого количества запросов
    for _ in range(10):
        for _ in range(random.randint(1, len(users))):
            user_id = random.randint(1, len(users_dict.keys()))
            if user_id not in deleted_users_carts:
                r = delete_user_cart(user_id=user_id)
                deleting_user_time.append(r.elapsed.total_seconds())

                if r.status_code == 200:
                    deleted_users_carts.append(user_id)
                else:
                    print(f"Cart was NOT deleted. Result: {r.json().get('data')}") 

        count_to_delete = random.randint(1, len(deleted_users_carts))
        for index in range(count_to_delete):
            deleted_users_carts.remove(random.choice(deleted_users_carts))

        # У некоторых, кто удалил корзину, создаём их заново
            # Создаём список продуктов в корзине
            user_products_list = []

            # Берём случайное число товаров в коризне
            for _ in range(random.randint(1, len(products))):
                # Берём случайный id продукта из нашего словарика продуктов
                user_products_list.append(products_dict[random.choice(list(products_dict.keys()))])

            r = create_user_cart(index, products_id=user_products_list)
            create_user_time.append(r.elapsed.total_seconds())
    
    return deleted_users_carts, deleting_user_time, create_user_time


def create_orders_for_db(users_dict: dict, deleted_users_carts: list):
    """ Создаём заказы """
    orders_creation_time = []

    for user in users_dict.keys():
        if user not in deleted_users_carts:
            r = create_order(user)

            if r.status_code == 200:
                print(f'Order for user {user} was created. Returned: {r}')
            else:
                print(f'Order for user {user} was NOT created. Returned: {r}')

            orders_creation_time.append(r.elapsed.total_seconds())

    return orders_creation_time


def main():
    # Создаём пользователей
    users, users_dict = create_users_for_db()
    # Создаём продукты
    products, products_dict = create_products_for_db()
    # Создаём корзины пользователей
    carts_creation_time = create_carts_for_db(users_dict=users_dict, products=products, products_dict=products_dict)
    # Имитируем действия пользователей: удаляем у случайных корзины и у некоторых из них создаём заново
    deleted_users_carts, users_cart_removal_time, user_cart_creation_time = user_actions_imitation(users=users, products=products, users_dict=users_dict, products_dict=products_dict)
    # Создаём заказы 
    orders_creation_time = create_orders_for_db(users_dict=users_dict, deleted_users_carts=deleted_users_carts)

    carts_creation_time = [x * 1000 for x in carts_creation_time]
    users_cart_removal_time = [x * 1000 for x in users_cart_removal_time]
    user_cart_creation_time = [x * 1000 for x in user_cart_creation_time]
    orders_creation_time = [x * 1000 for x in orders_creation_time]

    figure, axis = plt.subplots(nrows=2, ncols=2)

    axis[0, 0].hist(carts_creation_time, color='lightgreen', ec='black', bins=10, rwidth=0.9)
    axis[0, 0].set_title("Время создания корзины")

    axis[0, 1].hist(users_cart_removal_time, color='lightgreen', ec='black', bins=10, rwidth=0.9)
    axis[0, 1].set_title("Время удаления корзины пользователя")

    axis[1, 0].hist(user_cart_creation_time, color='lightgreen', ec='black', bins=10, rwidth=0.9)
    axis[1, 0].set_title("Время создания корзины пользователя")

    axis[1, 1].hist(orders_creation_time, color='lightgreen', ec='black', bins=10, rwidth=0.9)
    axis[1, 1].set_title("Время создания заказов")

    # Combine all the operations and display 
    print(f"Среднее время создания корзины: {mean(carts_creation_time)}")
    print(f"Среднее время удаления корзины пользователя: {mean(users_cart_removal_time)}")
    print(f"Среднее время создания корзины пользователя: {mean(user_cart_creation_time)}")
    print(f"Среднее время создания заказов: {mean(orders_creation_time)}")

    plt.show()

if __name__ == '__main__':
    main()
